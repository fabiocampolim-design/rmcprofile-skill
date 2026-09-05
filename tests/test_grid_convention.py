# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""RMCProfile tabulates partials at r_k = k*dr with bins centred on r_k (bins
(k-1/2)dr .. (k+1/2)dr). Measured on the package's smoke test 2026-09-05: with
this grid our g_ij(r) equal the _PDFpartials.csv columns to 0.000; with the
bin-centre grid (k+1/2)dr they differ by up to 2.9 at sharp peaks."""

import os

import numpy as np
import pytest

import rmcprofile_tools as rt
from test_analysis import nacl


def test_rmc_grid_points_and_edges():
    r, edges = rt.rmc_grid(0.1, 0.02)
    assert r.tolist() == pytest.approx([0.02, 0.04, 0.06, 0.08, 0.10])
    assert edges.tolist() == pytest.approx([0.01, 0.03, 0.05, 0.07, 0.09, 0.11])


def test_partial_gr_default_is_the_rmcprofile_grid():
    cfg = nacl(3)
    r, g = rt.partial_gr(cfg, rmax=8.0, dr=0.02)
    assert r[0] == pytest.approx(0.02) and r[-1] == pytest.approx(8.0) and len(r) == 400
    rc, gc = rt.partial_gr(cfg, rmax=8.0, dr=0.02, grid="centre")
    assert rc[0] == pytest.approx(0.01)
    # the a/2 = 2.82 Na-Cl shell sits exactly on a grid point of the rmcprofile grid: one bin holds all six neighbours
    k = int(round(2.82 / 0.02)) - 1
    rho_cl = cfg.counts[1] / np.prod(cfg.cell[:3])
    assert g["Na-Cl"][k] * 4 * np.pi * r[k] ** 2 * rho_cl * 0.02 == pytest.approx(6.0, rel=1e-6)
    assert g["Na-Cl"][k - 1] == 0.0 and g["Na-Cl"][k + 1] == 0.0


def test_shipped_smoke_test_partials_match_exactly(package_home):
    """Our histogram versus RMCProfile's own _PDFpartials.csv for the shipped
    ex_1 configuration (no moves accepted in that run, so the .rmc6f is the
    configuration the CSV describes)."""
    d = os.path.join(package_home, "tutorial", "ex_1")
    cfg = rt.read_rmc6f(os.path.join(d, "rmcsf6_190k.rmc6f"))
    r_csv, parts_csv = rt.read_partials_csv(os.path.join(d, "rmcsf6_190k_PDFpartials.csv"))
    r, parts = rt.partial_gr(cfg, rmax=r_csv[-1] + 1e-9, dr=0.02)
    assert np.allclose(r, r_csv)
    for lab in parts_csv:
        # RMCProfile works in single precision: measured max |diff| = 2.8e-4 on the S-F peak
        # (g = 20, i.e. 1.4e-5 relative), 4.1e-5 on F-F, 7e-6 on S-S (2026-09-05)
        assert np.max(np.abs(parts[lab] - parts_csv[lab])) < 1e-3, lab
    x, calc, _ = rt.read_csv_pair(os.path.join(d, "rmcsf6_190k_PDF1.csv"))
    _, G = rt.total_gr(r, parts, cfg)
    assert np.max(np.abs(G - calc)) < 1e-4
