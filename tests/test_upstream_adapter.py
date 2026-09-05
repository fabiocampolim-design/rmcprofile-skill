# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""The adapter stages a shipped exercise in a scratch directory, runs the
installed package, and compares our partials / G(r) with its CSVs. Records
(tests/records/crosscheck_v1.json) hold tolerances and the last measured
values; the package-bound tests skip without RMCPROFILE_HOME."""

import json
import os

import pytest

import rmcprofile_tools as rt
import upstream_adapter as ua
from conftest import ROOT

RECORDS = os.path.join(ROOT, "tests", "records", "crosscheck_v1.json")


def test_records_schema():
    with open(RECORDS, encoding="utf-8") as f:
        rec = json.load(f)
    assert rec["schema"] == 1 and rec["tool"] == "rmcprofile-skill"
    for name, e in rec["exercises"].items():
        assert name in ua.EXERCISES
        assert e["tolerance_partials"] > 0 and e["tolerance_gofr"] > 0
        assert set(e) >= {"tolerance_partials", "tolerance_gofr", "measured", "provenance"}


def test_exercise_table_names_the_audit_recipes():
    assert set(ua.EXERCISES) == {"ex_1", "ex_2", "ex_3", "ex_4_5K", "ex_4_293K", "ex_6_xray", "ex_6_neutron", "ex_7"}
    assert ua.EXERCISES["ex_4_5K"].copy == ["ex_4/5K/rmc/.run"] and ua.EXERCISES["ex_4_5K"].extra == ["ex_4/5K/data"]
    assert ua.EXERCISES["ex_7"].time_limit_override == 5.0
    assert ".poly" not in " ".join(ua.EXERCISES["ex_1"].outputs_to_delete)


def test_crosscheck_on_our_own_csvs(tmp_path):
    """Round trip through the CSV layouts: pdf-command output of a configuration
    cross-checked against that same configuration must be exact."""
    cfg = ua._nacl(2)
    p = tmp_path / "nacl.rmc6f"
    cfg.write(p)
    assert rt.main(["pdf", str(p), "--rmax", "5", "--outdir", str(tmp_path), "--log-dir", str(tmp_path / "logs"), "-q"]) == 0
    diffs = ua.crosscheck_partials(str(p), str(tmp_path / "nacl_PDFpartials.csv"))
    assert set(diffs) == {"Na-Na", "Na-Cl", "Cl-Cl"} and max(diffs.values()) < 1e-8
    assert ua.crosscheck_gofr(str(p), str(tmp_path / "nacl_GofR.csv")) < 1e-8


def test_stage_and_crosscheck_shipped_ex1(package_home, tmp_path):
    pkg = rt.find_package(package_home)
    work = ua.stage_exercise(pkg, "ex_1", str(tmp_path / "ex_1"))
    assert os.path.isfile(os.path.join(work, "rmcsf6_190k.poly"))          # inputs kept
    assert not os.path.isfile(os.path.join(work, "rmcsf6_190k_PDF1.csv"))  # outputs removed
    res = ua.run_and_crosscheck(pkg, "ex_1", work, timeout_min=3)
    assert res["returncode"] == 0 and res["final_chi2"]["chi2"] == pytest.approx(0.4201, abs=1e-4)
    with open(RECORDS, encoding="utf-8") as f:
        tol = json.load(f)["exercises"]["ex_1"]
    assert max(res["partials"].values()) <= tol["tolerance_partials"] and res["gofr"] <= tol["tolerance_gofr"]
    assert ua.within_tolerance(res, json.load(open(RECORDS, encoding="utf-8")))


def test_cli_list_and_selftest(tmp_path):
    assert ua.main(["list"]) == 0
    assert ua.main(["--selftest", "--outdir", str(tmp_path), "--log-dir", str(tmp_path / "logs"), "-q"]) == 0
    assert len(list((tmp_path / "logs").glob("upstream_adapter_*.json"))) == 1
