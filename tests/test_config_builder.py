# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Building a supercell configuration from a unit cell, folding it back, exporting it."""

import numpy as np
import pytest

import rmcprofile_tools as rt
from test_analysis import nacl

NACL_SITES = [("Na", 0, 0, 0), ("Na", .5, .5, 0), ("Na", .5, 0, .5), ("Na", 0, .5, .5),
              ("Cl", .5, 0, 0), ("Cl", 0, .5, 0), ("Cl", 0, 0, .5), ("Cl", .5, .5, .5)]


def test_build_configuration_matches_the_reference_lattice():
    cfg = rt.build_configuration((5.64, 5.64, 5.64, 90, 90, 90), NACL_SITES, (2, 2, 2))
    ref = nacl(2)
    assert cfg.atom_types == ["Na", "Cl"] and cfg.counts == [32, 32] and cfg.n_atoms() == 64
    assert cfg.supercell == (2, 2, 2) and cfg.cell == pytest.approx(ref.cell)
    assert cfg.density == pytest.approx(ref.density)
    assert np.allclose(np.sort(cfg.frac, axis=0), np.sort(ref.frac, axis=0))
    assert set(cfg.site) == set(range(1, 9)) and cfg.cellidx.max() == 1
    assert "Number density (Ang^-3)" in cfg.header or cfg.density > 0


def test_build_configuration_general_cell():
    a, c = 3.0, 5.0
    cfg = rt.build_configuration((a, a, c, 90, 90, 120), [("Zn", 1 / 3, 2 / 3, 0), ("Zn", 2 / 3, 1 / 3, 0.5)], (1, 1, 1))
    assert cfg.lattice[0].tolist() == pytest.approx([a, 0, 0])
    assert cfg.lattice[1].tolist() == pytest.approx([a * np.cos(np.radians(120)), a * np.sin(np.radians(120)), 0])
    assert abs(np.linalg.det(cfg.lattice)) == pytest.approx(a * a * c * np.sin(np.radians(120)))
    assert cfg.density == pytest.approx(2 / abs(np.linalg.det(cfg.lattice)))


def test_fold_to_unit_cell_recovers_the_sites():
    cfg = rt.build_configuration((5.64, 5.64, 5.64, 90, 90, 90), NACL_SITES, (3, 3, 3))
    frac_cell, idx = rt.fold_to_unit_cell(cfg)
    assert frac_cell.shape == (216, 3) and idx.shape == (216, 3)
    assert np.allclose(np.sort(np.unique(np.round(frac_cell, 6), axis=0), axis=0),
                       np.sort(np.unique(np.round([[x, y, z] for _, x, y, z in NACL_SITES], 6), axis=0), axis=0))
    assert rt.average_cell(cfg) == pytest.approx((5.64, 5.64, 5.64, 90, 90, 90))


def test_export_xyz_and_cif(tmp_path):
    cfg = nacl(2)
    rt.export_xyz(cfg, tmp_path / "nacl.xyz")
    lines = (tmp_path / "nacl.xyz").read_text(encoding="utf-8").splitlines()
    assert lines[0].strip() == "64" and len(lines) == 66
    xyz = np.array([[float(v) for v in ln.split()[1:4]] for ln in lines[2:]])
    assert np.allclose(xyz, cfg.cart(), atol=1e-5)
    rt.export_cif(cfg, tmp_path / "nacl.cif")
    cif = (tmp_path / "nacl.cif").read_text(encoding="utf-8")
    assert "_cell_length_a" in cif and "11.28" in cif and "_atom_site_fract_x" in cif
    assert cif.count("\nNa") + cif.count("\nCl") == 64 and "P 1" in cif
