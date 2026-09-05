# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Faber-Ziman partial structure factors, X-ray form factors and weights."""

import numpy as np
import pytest

import rmcprofile_tools as rt
from test_analysis import nacl


def test_faber_ziman_neutron_total_equals_direct_transform():
    cfg = nacl(3)
    r, parts = rt.partial_gr(cfg, rmax=8.0, dr=0.02)
    q = np.arange(0.5, 15.0, 0.05)
    _, G = rt.total_gr(r, parts, cfg)
    F_direct = rt.fq_from_gr(r, G, cfg.density, q)
    F_fz = rt.total_fq_from_partials(r, parts, cfg, q, radiation="neutron")
    assert np.allclose(F_direct, F_fz, atol=1e-9)
    s = rt.faber_ziman_sq(r, parts["Na-Cl"], cfg.density, q)
    assert s.shape == q.shape and np.isfinite(s).all()


def test_xray_form_factor_and_weights():
    pt = pytest.importorskip("periodictable")
    assert pt
    q = np.array([0.0, 2.0, 10.0])
    f = rt.xray_form_factor("Na", q)
    assert f[0] == pytest.approx(11.0, abs=0.05) and f[2] < f[1] < f[0]
    assert rt.xray_form_factor("Cl", np.array([0.0]))[0] == pytest.approx(17.0, abs=0.05)
    cfg = nacl(2)
    w = rt.xray_weights(cfg, np.array([0.0]))
    assert set(w) == {"Na-Na", "Na-Cl", "Cl-Cl"} and sum(v[0] for v in w.values()) == pytest.approx(1.0)
    r, parts = rt.partial_gr(cfg, rmax=5.0, dr=0.02)
    qq = np.arange(0.5, 15.0, 0.05)
    Fx = rt.total_fq_from_partials(r, parts, cfg, qq, radiation="xray")
    assert Fx.shape == qq.shape and np.isfinite(Fx).all()


def test_xray_z_coefficients_reproduce_manual_appendix_d():
    """Manual App. D, Table D.3 (GaPO4: Ga 1/6, P 1/6, O 4/6 with Z = 31, 15, 6)."""
    cfg = rt.Rmc6f(atom_types=["Ga", "P", "O"], counts=[1, 1, 4])
    coef = rt.xray_coefficients_rmcprofile(cfg)
    assert [round(coef[k], 4) for k in ["Ga-Ga", "Ga-P", "Ga-O", "P-P", "P-O", "O-O"]] == \
        pytest.approx([0.1580, 0.1529, 0.3261, 0.0370, 0.1577, 0.1683], abs=1.5e-4)
    assert sum(coef.values()) == pytest.approx(1.0)


def test_cromer_mann_4term_fit_for_the_xray_file(tmp_path):
    pytest.importorskip("periodictable")
    coef = rt.cromer_mann_4term("Na")
    assert len(coef) == 9
    q = np.linspace(0, 20, 201)
    s = q / (4 * np.pi)
    f_fit = sum(coef[2 * k] * np.exp(-coef[2 * k + 1] * s ** 2) for k in range(4)) + coef[8]
    assert np.max(np.abs(f_fit - rt.xray_form_factor("Na", q))) < 0.05
    rt.write_xray_file(tmp_path / "s.xray", ["Na", "Cl"])
    lines = (tmp_path / "s.xray").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2 and lines[0].split()[0] == "NA" and len(lines[0].split()) == 10
