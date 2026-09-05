# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""The input-set checker catches the mistakes the manual warns about (§3.2,
§4.1, §5.6.1) before the binary is started."""

import numpy as np

import rmcprofile_tools as rt
from test_datfile import DAT
from test_rmc6f import ATOMS, HEADER


def _write_set(d, *, drop=(), atoms_line="ATOMS :: Na Cl", stale_neigh=False, end_point=1500):
    dat = DAT.replace("ATOMS :: Na Cl", atoms_line).replace("END_POINT :: 1500", "END_POINT :: %d" % end_point)
    (d / "nacl.dat").write_text(dat, encoding="utf-8")
    if "rmc6f" not in drop:
        (d / "nacl.rmc6f").write_text(HEADER + "".join(f"{i+1} {el} {x:.6f} {y:.6f} {z:.6f} {s} 0 0 0\n"
                                                       for i, (el, x, y, z, s) in enumerate(ATOMS)), encoding="utf-8")
    if "data" not in drop:
        x = np.arange(0.02, 30.02, 0.02)
        rt.write_data_file(d / "nacl_gr.dat", x, -0.1 * np.ones_like(x), "nacl")
    if "bragg" not in drop:
        (d / "nacl.bragg").write_text("        2           1   1.0   180.0\nTime, I(obs)\n 6.98 1.31\n 6.99 1.30\n", encoding="utf-8")
        (d / "nacl.back").write_text("1\n 1.0\n", encoding="utf-8")
        (d / "nacl.inst").write_text("1\n1\n 1477.07 0.5 10.94 17.95\n", encoding="utf-8")
    if stale_neigh:
        (d / "nacl.neigh").write_text("stale\n", encoding="utf-8")


def _codes(findings, level=None):
    return [f.code for f in findings if level is None or f.level == level]


def test_complete_set_has_no_errors(tmp_path):
    _write_set(tmp_path)
    f = rt.check_input_set("nacl", tmp_path)
    assert _codes(f, "ERROR") == []
    assert "summary" in _codes(f, "INFO")


def test_missing_configuration_and_data(tmp_path):
    _write_set(tmp_path, drop=("rmc6f", "data"))
    codes = _codes(rt.check_input_set("nacl", tmp_path), "ERROR")
    assert "no-configuration" in codes and "data-file-missing" in codes


def test_atom_order_mismatch(tmp_path):
    _write_set(tmp_path, atoms_line="ATOMS :: Cl Na")
    codes = _codes(rt.check_input_set("nacl", tmp_path), "ERROR")
    assert "atom-order" in codes


def test_bragg_needs_inst_and_back(tmp_path):
    _write_set(tmp_path)
    (tmp_path / "nacl.inst").unlink()
    codes = _codes(rt.check_input_set("nacl", tmp_path), "ERROR")
    assert "bragg-inst-missing" in codes


def test_end_point_beyond_data_and_stale_neighbours(tmp_path):
    _write_set(tmp_path, end_point=99999, stale_neigh=True)
    f = rt.check_input_set("nacl", tmp_path)
    assert "end-point-beyond-data" in _codes(f, "WARN")       # the program clamps; ex_1 ships END_POINT 3000 on 1186 points
    assert "stale-neighbour-files" in _codes(f, "WARN")
    assert _codes(f, "ERROR") == []


def test_minimum_distance_count_must_match_pairs(tmp_path):
    _write_set(tmp_path)
    t = (tmp_path / "nacl.dat").read_text(encoding="utf-8").replace("MINIMUM_DISTANCES ::   3.5  2.4  3.5 Angstrom",
                                                                    "MINIMUM_DISTANCES ::   3.5  2.4 Angstrom")
    (tmp_path / "nacl.dat").write_text(t, encoding="utf-8")
    assert "minimum-distances-count" in _codes(rt.check_input_set("nacl", tmp_path), "ERROR")


def test_filename_case_mismatch_is_flagged(tmp_path):
    """ex_6's neutron .dat names GaPO4_...gr while the file is gapo4_...gr: fine on
    Windows, a silent stop on Linux (docs/02 P-10). On a case-sensitive filesystem the
    file is simply missing; on Windows the checker must still warn."""
    _write_set(tmp_path)
    t = (tmp_path / "nacl.dat").read_text(encoding="utf-8").replace("FILENAME :: nacl_gr.dat", "FILENAME :: NaCl_GR.dat")
    (tmp_path / "nacl.dat").write_text(t, encoding="utf-8")
    codes = _codes(rt.check_input_set("nacl", tmp_path))
    assert "filename-case" in codes or "data-file-missing" in codes
    assert "data-file-missing" not in codes or "filename-case" not in codes


def test_polyhedral_restraint_needs_its_poly_file(tmp_path):
    """The package waits forever for a missing .poly (audit 2026-09-05)."""
    _write_set(tmp_path)
    t = (tmp_path / "nacl.dat").read_text(encoding="utf-8").replace("END ::", "POLYHEDRAL_RESTRAINT :: 4\n\nEND ::")
    (tmp_path / "nacl.dat").write_text(t, encoding="utf-8")
    assert "poly-file-missing" in _codes(rt.check_input_set("nacl", tmp_path), "ERROR")
    (tmp_path / "nacl.poly").write_text("title\n1.613 100 300\n", encoding="utf-8")
    assert "poly-file-missing" not in _codes(rt.check_input_set("nacl", tmp_path))
