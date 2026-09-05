# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
import glob
import json
import os
import subprocess
import sys

from conftest import ROOT

TOOLS = os.path.join(ROOT, "scripts", "rmcprofile_tools.py")


def _run(args, cwd, drop_home=False):
    env = {k: v for k, v in os.environ.items() if not (drop_home and k == "RMCPROFILE_HOME")}
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, TOOLS, *args], capture_output=True, text=True, cwd=cwd, env=env)


def test_version_prints_version_file():
    with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as f:
        ver = f.read().strip()
    p = _run(["--version"], ROOT)
    assert p.returncode == 0 and ver in p.stdout


def test_selftest_passes_and_writes_audit_log(tmp_path):
    p = _run(["--selftest", "--outdir", str(tmp_path / "out"), "--log-dir", str(tmp_path / "logs")], ROOT)
    assert p.returncode == 0, p.stdout + p.stderr
    logs = glob.glob(str(tmp_path / "logs" / "rmcprofile_tools_*.json"))
    assert len(logs) == 1
    with open(logs[0], encoding="utf-8") as f:
        rec = json.load(f)
    assert rec["version"] and rec["argv"][0] == "--selftest" and rec["ok"] is True
    assert all(c["ok"] for c in rec["checks"]) and len(rec["checks"]) >= 4


def test_check_subcommand_reports_findings(tmp_path):
    (tmp_path / "x.dat").write_text("TITLE :: x\nATOMS :: Na Cl\nMINIMUM_DISTANCES :: 1 2 Angstrom\nEND ::\n", encoding="utf-8")
    p = _run(["check", "x", "--dir", str(tmp_path), "--log-dir", str(tmp_path / "logs")], ROOT)
    assert p.returncode == 1
    assert "ERROR no-configuration" in p.stdout and "ERROR minimum-distances-count" in p.stdout


def test_run_without_package_fails_loudly(tmp_path):
    (tmp_path / "x.dat").write_text("TITLE :: x\nEND ::\n", encoding="utf-8")
    p = _run(["run", "x", "--dir", str(tmp_path), "--log-dir", str(tmp_path / "logs")], ROOT, drop_home=True)
    assert p.returncode == 2 and "RMCPROFILE_HOME" in p.stdout + p.stderr
