# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""The adapter stages a shipped exercise in a scratch directory, runs the
installed package, and compares our partials / G(r) with its CSVs. Records
(tests/records/crosscheck_v1.json) hold tolerances and the last measured
values; the package-bound tests skip without RMCPROFILE_HOME."""

import json
import os

import numpy as np

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


def test_within_tolerance_distinguishes_no_record_partials_only_and_reader_error():
    """0.5.5: on the 6.8.0-rc.1 audit every exercise but ex_1 read 'within tolerance: False'
    because the records held only ex_1; an X-ray exercise has no G(r) column; a configuration
    the reader refuses is an error row, not a traceback."""
    rec = {"exercises": {"ex_x": {"tolerance_partials": 1e-3, "tolerance_gofr": 1e-4}}}
    assert ua.within_tolerance({"exercise": "ex_new", "partials": {"A-A": 1e-5}, "gofr": 1e-6}, rec) is None
    assert ua.within_tolerance({"exercise": "ex_x", "partials": {"A-A": 2e-4}, "gofr": None}, rec) is True
    assert ua.within_tolerance({"exercise": "ex_x", "partials": {"A-A": 2e-3}, "gofr": None}, rec) is False
    assert ua.within_tolerance({"exercise": "ex_x", "partials": {"A-A": 2e-4}, "gofr": 2e-4}, rec) is False
    assert ua.within_tolerance({"exercise": "ex_x", "partials": {}, "gofr": None, "error": "boom"}, rec) is False


def test_crosscheck_partials_reports_a_short_configuration(tmp_path):
    """The shipped GaPO4 neutron start (both 6.7.9 and 6.8.0-rc.1) declares 576 atoms and holds
    575 — atom 2 is absent (P-22). The reader refuses it with the counts in the message."""
    from test_rmc6f import ATOMS, HEADER
    rows = [f"{i+1} {el} {x:.6f} {y:.6f} {z:.6f} {s} 0 0 0" for i, (el, x, y, z, s) in enumerate(ATOMS)]
    (tmp_path / "short.rmc6f").write_text(HEADER + "\n".join(rows[:-1]) + "\n", encoding="utf-8")
    (tmp_path / "short_PDFpartials.csv").write_text("r, Na-Na\n0.02, 0.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="atom lines"):
        ua.crosscheck_partials(str(tmp_path / "short.rmc6f"), str(tmp_path / "short_PDFpartials.csv"))


def test_crosscheck_gofr_aligns_a_pdf_column_that_starts_above_dr(tmp_path):
    """0.5.5: ex_7's _PDF1.csv starts at r = 1.40 A (where its data start); the comparison
    picks our G(r) on the CSV's own points instead of assuming r = dr, 2 dr, ..."""
    cfg = ua._nacl(2)
    cfg.write(tmp_path / "n.rmc6f")
    r, parts = rt.partial_gr(cfg, rmax=5.0, dr=0.02)
    _, G = rt.total_gr(r, parts, cfg)
    sel = slice(69, 250)                        # r = 1.40 ... 5.00
    lines = ["r (Ang), PDF (RMC), PDF (Expt)"] + [f"{r[i]:.6f}, {G[i]:.12f}, 0." for i in range(len(r))[sel]]
    (tmp_path / "n_PDF1.csv").write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    assert ua.crosscheck_gofr(str(tmp_path / "n.rmc6f"), str(tmp_path / "n_PDF1.csv")) < 1e-9


def test_crosscheck_gofr_honours_the_fit_type(tmp_path):
    """The compared column is whatever the exercise fits: D(r) = 4 pi r rho G(r) for the SnO
    exercise; the same numbers read 'in G(r)' were 3.6 barn apart."""
    ua._nacl(2).write(tmp_path / "n.rmc6f")
    cfg = rt.read_rmc6f(tmp_path / "n.rmc6f")          # the header carries the density to six decimals
    r, parts = rt.partial_gr(cfg, rmax=5.0, dr=0.02)
    _, G = rt.total_gr(r, parts, cfg)
    D = 4 * np.pi * r * cfg.density * G
    lines = ["r (Ang), PDF (RMC), PDF (Expt)"] + [f"{r[i]:.6f}, {D[i]:.12f}, 0." for i in range(len(r))]
    (tmp_path / "n_PDF1.csv").write_text(chr(10).join(lines) + chr(10), encoding="utf-8")
    (tmp_path / "n.dat").write_text("TITLE :: x" + chr(10) + "NEUTRON_REAL_SPACE_DATA :: 1" + chr(10) + "  > FILENAME :: f.dat" + chr(10)
                                    + "  > DATA_TYPE :: G(r)" + chr(10) + "  > FIT_TYPE :: D(r)" + chr(10) + "END ::" + chr(10), encoding="utf-8")
    assert ua._fit_type(str(tmp_path / "n.dat")) == "D(r)"
    assert ua.crosscheck_gofr(str(tmp_path / "n.rmc6f"), str(tmp_path / "n_PDF1.csv"), str(tmp_path / "n.dat")) < 1e-9
    assert ua.crosscheck_gofr(str(tmp_path / "n.rmc6f"), str(tmp_path / "n_PDF1.csv")) > 0.1     # read as G(r) it is far off
