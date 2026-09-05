# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""write_input_set turns a box plus synthetic data into a complete RMCProfile run
directory; bond_valence_sum is the toolkit's own BVS calculator."""

import os

import numpy as np
import pytest

import rmclite as rl
import rmcprofile_tools as rt
from test_analysis import nacl


def _synthetic(n=2, sd=0.05, seed=1):
    cfg = nacl(n)
    rng = np.random.default_rng(seed)
    box = rl.Box.from_rmc6f(cfg)
    box.frac = (box.frac + rng.normal(0, sd, box.frac.shape) / (5.64 * n)) % 1.0
    r, parts, G = rl.synth_targets(box, 5.0, 0.02, 0.0, rng)
    q = np.arange(0.5, 20.0, 0.02)
    F = rt.fq_from_gr(r, G, cfg.density, q)
    return cfg, r, G, q, F


def test_write_input_set_passes_the_checker(tmp_path):
    cfg, r, G, q, F = _synthetic()
    paths = rt.write_input_set("nacl", tmp_path, cfg, gr=(r, G), fq=(q, F),
                               min_dist={"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0}, max_move=0.05,
                               time_limit_min=0.0, title="synthetic NaCl")
    assert set(os.path.basename(p) for p in paths) == {"nacl.dat", "nacl.rmc6f", "nacl_gr.dat", "nacl_fq.dat"}
    findings = rt.check_input_set("nacl", tmp_path)
    assert [f.code for f in findings if f.level == "ERROR"] == []
    d = rt.read_dat(tmp_path / "nacl.dat")
    assert d.atoms == ["Na", "Cl"] and d.minimum_distances() == [3.0, 2.2, 3.0]
    assert d.get("NEUTRON_REAL_SPACE_DATA", "END_POINT") == str(len(r))
    assert d.get("NEUTRON_RECIPROCAL_SPACE_DATA", "FILENAME") == "nacl_fq.dat"
    assert float(d.scalars["NUMBER_DENSITY"].split()[0]) == pytest.approx(cfg.density, rel=1e-5)
    back = rt.read_data_file(tmp_path / "nacl_gr.dat")
    assert np.allclose(back.x, r) and np.allclose(back.y, G, atol=1e-7)


def test_run_written_set_with_the_package(package_home, tmp_path):
    cfg, r, G, q, F = _synthetic()
    rt.write_input_set("nacl", tmp_path, cfg, gr=(r, G), fq=(q, F),
                       min_dist={"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0}, max_move=0.05,
                       time_limit_min=0.0, title="synthetic NaCl")
    pkg = rt.find_package(package_home)
    res = rt.run_rmcprofile("nacl", tmp_path, pkg, timeout_min=3)
    assert res.returncode == 0, open(res.log_path, encoding="utf-8").read()[-1500:]
    assert any(o.endswith("_PDF1.csv") for o in res.outputs) and res.final_chi2 is not None
    x, calc, expt = rt.read_csv_pair(tmp_path / "nacl_PDF1.csv")
    assert np.allclose(expt, G[: len(expt)], atol=1e-4)             # the program read our data
    assert calc[0] == pytest.approx(G[0], abs=1e-3)                  # and computed G(r) of our box


def test_bond_valence_sum_on_rock_salt():
    cfg = nacl(2)
    bvs = rt.bond_valence_sum(cfg, "Na", "Cl", r0=2.15, b=0.37, cutoff=3.2)
    assert bvs.shape == (32,)
    assert np.allclose(bvs, 6 * np.exp((2.15 - 2.82) / 0.37))
    assert bvs.mean() == pytest.approx(0.98, abs=0.03)              # Na is about +1 in NaCl
