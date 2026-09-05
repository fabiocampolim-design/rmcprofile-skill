# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Output files (manual §3.4): the chi² history, the fit CSVs, the partials CSV."""

import pytest

import rmcprofile_tools as rt


def test_chi2_history_both_layouts(tmp_path):
    p = tmp_path / "s.chi2"
    p.write_text("m_accepted   m_generated   m_tested   chi2   Bragg_Chi2   Expt_1   Expt_2\n 0   1   0    0.4201    0.4834    0.3496    0.7584\n 10  25  30   0.3900    0.4500    0.3300    0.7000\n", encoding="utf-8")
    h = rt.read_chi2_history(p)
    assert list(h) == ["m_accepted", "m_generated", "m_tested", "chi2", "Bragg_Chi2", "Expt_1", "Expt_2"]
    assert h["chi2"].tolist() == pytest.approx([0.4201, 0.39]) and h["m_generated"].tolist() == [1, 25]
    q = tmp_path / "s_chi2.txt"
    q.write_text("moves chi2 Expt_1\n1 2.0 1.5\n2 1.0 0.5\n", encoding="utf-8")
    assert rt.read_chi2_history(q)["Expt_1"].tolist() == [1.5, 0.5]


def test_fit_csvs(tmp_path):
    p = tmp_path / "s_SQ1.csv"
    p.write_text("Q (Ang^-1), RMC, Data\n  0.71 , -0.176 , -0.0909\n  0.73 , -0.203 , -0.130\n", encoding="utf-8")
    x, calc, expt = rt.read_csv_pair(p)
    assert x.tolist() == pytest.approx([0.71, 0.73]) and calc[1] == pytest.approx(-0.203) and expt[0] == pytest.approx(-0.0909)
    b = tmp_path / "s_bragg.csv"
    b.write_text("Flight time (us) , Calculated , Experiment\n 6988.14 , 1.2869 , 1.2862\n", encoding="utf-8")
    x, calc, expt = rt.read_csv_pair(b)
    assert x[0] == pytest.approx(6988.14) and expt[0] == pytest.approx(1.2862)


def test_partials_csv(tmp_path):
    p = tmp_path / "s_PDFpartials.csv"
    p.write_text("   r (Ang),     S-S  ,     S-F  ,     F-F  \n   0.02 , 0.0 , 0.0 , 0.0 , \n   0.04 , 0.1 , 0.2 , 0.3 , \n", encoding="utf-8")
    r, parts = rt.read_partials_csv(p)
    assert r.tolist() == pytest.approx([0.02, 0.04])
    assert list(parts) == ["S-S", "S-F", "F-F"] and parts["S-F"].tolist() == pytest.approx([0.0, 0.2])
