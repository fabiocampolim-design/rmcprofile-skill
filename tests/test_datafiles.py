# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Experimental data files (manual §4.12) in both layouts, and the Bragg
family (.bragg/.back/.inst/.hkl, manual §4.13) plus .dw (§2.5)."""

import numpy as np
import pytest

import rmcprofile_tools as rt


def test_two_line_header_data_file(tmp_path):
    p = tmp_path / "gr.dat"
    p.write_text(" 4\nnacl test                    mutli by  0.1\n  0.02 -0.10\n  0.04 -0.10\n  0.06 -0.09\n  0.08 -0.05\n", encoding="utf-8")
    d = rt.read_data_file(p)
    assert d.x.tolist() == pytest.approx([0.02, 0.04, 0.06, 0.08])
    assert d.y.tolist() == pytest.approx([-0.10, -0.10, -0.09, -0.05])
    assert d.err is None and d.title.startswith("nacl test") and d.metadata == {}


def test_stog_style_data_file(tmp_path):
    p = tmp_path / "gr.stog"
    p.write_text("# File: pair distribution function file\n# Title: NaCl 300K\n# Number of points: 3\n# ------------------------------------\n"
                 "2.00000000000000004E-002 -13.27 0.738\n4.00000000000000008E-002 -8.58 0.562\n5.99999999999999978E-002 -2.93 0.354\n", encoding="utf-8")
    d = rt.read_data_file(p)
    assert d.x.tolist() == pytest.approx([0.02, 0.04, 0.06])
    assert d.err.tolist() == pytest.approx([0.738, 0.562, 0.354])
    assert d.metadata["Title"] == "NaCl 300K" and d.title == "NaCl 300K"


def test_write_two_line_and_stog_round_trip(tmp_path):
    x = np.arange(0.02, 0.11, 0.02)
    y = -0.2759 * np.ones_like(x)
    for style in ("two-line", "stog"):
        p = tmp_path / ("out_%s.dat" % style)
        rt.write_data_file(p, x, y, "SF6 190K", style=style)
        d = rt.read_data_file(p)
        assert np.allclose(d.x, x) and np.allclose(d.y, y)
        assert d.title == "SF6 190K"
    first = (tmp_path / "out_two-line.dat").read_text(encoding="utf-8").splitlines()
    assert first[0].strip() == "5"


def test_bragg_family(tmp_path):
    (tmp_path / "s.bragg").write_text("        3           2   41.0000000000000        204.094067137014     \nTime,   I(obs),  Histogram = 2, Bank = 2\n   6.98 1.31\n   6.99 1.30\n   7.00 1.30\n", encoding="utf-8")
    (tmp_path / "s.back").write_text("3\n 1.2484\n -0.0617876\n -0.0556794\n", encoding="utf-8")
    (tmp_path / "s.inst").write_text("2\n1\n 1477.07 0.5 10.94 17.95\n 0.0 3.985 35.95 40.82\n2\n 4850.45 -2.57 -2.46 63.62\n 0.0 3.985 35.95 40.82\n", encoding="utf-8")
    (tmp_path / "s.hkl").write_text("1.00\n-20 20 1.0\n-20 20 1.0\n-20 20 1.0\n", encoding="utf-8")
    (tmp_path / "s.dw").write_text("0 1.37  2.00\n0 1.74  2.42\n", encoding="utf-8")
    b = rt.read_bragg(tmp_path / "s.bragg")
    assert b.npoints == 3 and b.bank == 2 and b.scale == pytest.approx(41.0) and b.volume == pytest.approx(204.094067137014)
    assert b.x.tolist() == pytest.approx([6.98, 6.99, 7.00]) and b.y.tolist() == pytest.approx([1.31, 1.30, 1.30])
    back = rt.read_back(tmp_path / "s.back")
    assert back.tolist() == pytest.approx([1.2484, -0.0617876, -0.0556794])
    inst = rt.read_inst(tmp_path / "s.inst")
    assert [bk["bank"] for bk in inst] == [1, 2] and inst[1]["values"][0] == pytest.approx(4850.45)
    hkl = rt.read_hkl(tmp_path / "s.hkl")
    assert hkl["scale"] == pytest.approx(1.0) and hkl["ranges"] == [(-20, 20, 1.0)] * 3
    assert rt.read_dw(tmp_path / "s.dw") == [(0, 1.37, 2.0), (0, 1.74, 2.42)]


def test_bragg_point_count_mismatch_is_an_error(tmp_path):
    (tmp_path / "s.bragg").write_text("        5           2   41.0        204.0\nTime, I(obs)\n 6.98 1.31\n 6.99 1.30\n", encoding="utf-8")
    with pytest.raises(ValueError, match="5"):
        rt.read_bragg(tmp_path / "s.bragg")
