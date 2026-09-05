# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Playbook rule 15: the suite guards the docs — every CLI flag and every
subcommand is documented in AGENTS.md and docs/USER_MANUAL.md; VERSION,
CITATION and CHANGELOG agree; SKILL.md points at existing reference files."""

import argparse
import json
import os
import re
import sys

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "docs"))
sys.path.insert(0, os.path.join(ROOT, "build"))
sys.path.insert(0, os.path.join(ROOT, "course", "tools"))


def _read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _flags(parser):
    out = {s for a in parser._actions for s in a.option_strings if s.startswith("--") and s != "--help"}
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            for name, sp in a.choices.items():
                out.add("`%s`" % name)
                out |= {s for b in sp._actions for s in b.option_strings if s.startswith("--") and s != "--help"}
    return out


def test_build_manual_writes_html_without_pandoc(tmp_path, monkeypatch):
    """Rule 10: the manual builds from the Markdown even on a machine without pandoc."""
    import build_manual
    monkeypatch.setattr(build_manual.shutil, "which", lambda name: None)
    assert build_manual.main(["--outdir", str(tmp_path), "--no-pdf"]) == 0
    out = (tmp_path / "USER_MANUAL.html").read_text(encoding="utf-8")
    assert "<title>rmcprofile-skill" in out and "<h2>" in out and "<table>" in out
    assert "RMCPROFILE_HOME" in out


@pytest.mark.parametrize("module", ["rmcprofile_tools", "verify_rmcprofile", "build_manual", "upstream_adapter", "rmclite",
                                    "watch_upstream", "assemble", "execute", "gallery", "extract_figures", "build_deck", "make_slides_pdf",
                                    "verify_deck", "make_handout", "build_pptx"])
def test_script_flags_and_subcommands_are_documented(module):
    mod = __import__(module)
    agents, manual = _read("AGENTS.md"), _read("docs", "USER_MANUAL.md")
    for f in _flags(mod.build_parser()):
        assert f in agents, "%s: %s missing from AGENTS.md" % (module, f)
        assert f in manual, "%s: %s missing from docs/USER_MANUAL.md" % (module, f)


@pytest.mark.parametrize("module", ["rmcprofile_tools", "upstream_adapter", "rmclite"])
def test_flag_choices_are_documented(module):
    mod = __import__(module)
    agents, manual = _read("AGENTS.md"), _read("docs", "USER_MANUAL.md")
    parsers = [mod.build_parser()]
    for a in parsers[0]._actions:
        if isinstance(a, argparse._SubParsersAction):
            parsers.extend(a.choices.values())
    for sp in parsers:
        for b in sp._actions:
            if b.choices and b.option_strings:
                expected = "`%s {%s}`" % (b.option_strings[-1], ",".join(b.choices))
                assert expected in agents and expected in manual, "%s: %s" % (module, expected)


def test_version_citation_changelog_agree():
    ver = _read("VERSION").strip()
    assert 'version: "%s"' % ver in _read("CITATION.cff")
    assert "## [%s]" % ver in _read("CHANGELOG.md")
    assert "# rmcprofile-skill %s" % ver in _read("SKILL.md")
    assert "Version %s" % ver in _read("docs", "USER_MANUAL.md")


def test_skill_md_references_exist_and_workflows_present():
    skill = _read("SKILL.md")
    refs = set(re.findall(r"`references/([\w\-]+\.md)`", skill))
    assert refs, "SKILL.md names no reference file"
    for ref in refs:
        assert os.path.isfile(os.path.join(ROOT, "references", ref)), ref
    for n in range(1, 10):
        assert "## %d." % n in skill, "workflow %d missing" % n


def test_checker_codes_are_documented():
    """Every finding code the checker can emit is explained in the manual and SKILL.md."""
    src = _read("scripts", "rmcprofile_tools.py")
    codes = set(re.findall(r'Finding\("(?:ERROR|WARN|INFO)", "([\w\-]+)"', src))
    assert len(codes) >= 15
    manual, skill = _read("docs", "USER_MANUAL.md"), _read("SKILL.md")
    for c in codes:
        assert "`%s`" % c in manual, "%s missing from docs/USER_MANUAL.md" % c
        assert "`%s`" % c in skill, "%s missing from SKILL.md" % c


def test_records_file_is_documented_and_valid():
    rec = json.loads(_read("tests", "records", "crosscheck_v1.json"))
    assert rec["schema"] == 1 and "ex_1" in rec["exercises"] and "rmclite" in rec
    assert "crosscheck_v1.json" in _read("AGENTS.md") and "crosscheck_v1.json" in _read("docs", "USER_MANUAL.md")


def test_readme_is_the_product_page():
    readme = _read("README.md")
    for section in ("## What it does", "## Install", "## Quick start", "## What is verified", "## Licence", "### Disclaimer"):
        assert section in readme, section
    assert "RMCPROFILE_HOME" in readme and "verify_rmcprofile.py" in readme


def test_readme_has_the_comparison_and_the_credit_table():
    """Rules 2 and 9: the README says honestly what the neighbours do better, and carries the
    CRediT table of who did what (Fabio's review of the first public release, 2026-09-05)."""
    readme = _read("README.md")
    assert "## Honest comparison with neighbours" in readme and "| If you want" in readme
    assert "## How it was built" in readme and "Role (CRediT)" in readme
    assert readme.count("| ●") + readme.count("| ○") >= 12
