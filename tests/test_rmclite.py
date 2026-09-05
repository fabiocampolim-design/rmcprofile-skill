# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""rmclite: the clean-room RMC engine. Tests are physics and bookkeeping
checks on exact lattices, all seeded and fast (< 10 s each)."""

import numpy as np
import pytest

import rmclite as rl
import rmcprofile_tools as rt
from test_analysis import nacl


def test_box_round_trip_and_distance_row():
    cfg = nacl(2)
    box = rl.Box.from_rmc6f(cfg)
    assert box.n == 64 and box.types == ["Na", "Cl"]
    row = box.distance_row(0)
    assert np.isinf(row[0]) and np.isclose(np.sort(row)[:6], 2.82).all()
    back = box.to_rmc6f(cfg)
    assert np.allclose(back.frac, cfg.frac) and back.atom_types == cfg.atom_types


def test_histogram_matches_partial_gr_and_updates_incrementally():
    cfg = nacl(3)
    box = rl.Box.from_rmc6f(cfg)
    h = rl.Histogram(box, rmax=8.0, dr=0.02)
    r, ref = rt.partial_gr(cfg, rmax=8.0, dr=0.02)
    for lab in ref:
        assert np.allclose(h.g()[lab], ref[lab])
    rng = np.random.default_rng(1)
    for _ in range(50):                                     # move atoms, update incrementally
        i = int(rng.integers(box.n))
        old = box.distance_row(i)
        box.frac[i] = (box.frac[i] + rng.normal(0, 0.01, 3) / 16.92) % 1.0
        h.update(i, old, box.distance_row(i))
    full = rl.Histogram(box, rmax=8.0, dr=0.02)
    for lab in full.counts:
        assert np.array_equal(h.counts[lab], full.counts[lab]), lab


def test_targets_are_zero_on_their_own_configuration():
    cfg = nacl(2)
    box = rl.Box.from_rmc6f(cfg)
    h = rl.Histogram(box, rmax=5.0, dr=0.02)
    g = h.g()
    t1 = rl.PartialTarget("Na-Cl", h.r, g["Na-Cl"], sigma=0.05)
    _, G = rt.total_gr(h.r, g, cfg)
    t2 = rl.TotalGTarget(h.r, G, sigma=0.01, weights=rt.neutron_weights(cfg))
    q = np.arange(0.5, 15.0, 0.05)
    t3 = rl.FqTarget(q, rt.fq_from_gr(h.r, G, cfg.density, q), sigma=0.01, density=cfg.density,
                     weights=rt.neutron_weights(cfg))
    assert t1.chi2(h) == 0.0 and t2.chi2(h) == 0.0 and t3.chi2(h) < 1e-20


def test_closest_approach_is_never_violated_and_seed_reproduces():
    cfg = nacl(2)
    dmin = {"Na-Na": 3.5, "Na-Cl": 2.4, "Cl-Cl": 3.5}
    runs = []
    for _ in range(2):
        box = rl.Box.from_rmc6f(cfg)
        eng = rl.RmcLite(box, rmax=5.0, dr=0.02, targets=[], constraints=[rl.ClosestApproach(dmin)],
                         max_move={"Na": 0.1, "Cl": 0.1}, seed=7)
        st = eng.run(500)
        assert st.generated == 500 and st.accepted > 0
        d = rt._min_image_distances(box.to_rmc6f(cfg))
        for lab, dm in dmin.items():
            a, b = lab.split("-")
            ia, ib = np.where(box.atoms == a)[0], np.where(box.atoms == b)[0]
            assert d[np.ix_(ia, ib)].min() >= dm - 1e-12, lab
        runs.append(box.frac.copy())
    assert np.array_equal(runs[0], runs[1])


def test_distance_window_keeps_members_inside():
    cfg = nacl(2)
    box = rl.Box.from_rmc6f(cfg)
    win = {"Na-Cl": (2.5, 3.1)}                            # the six nearest Cl of every Na
    eng = rl.RmcLite(box, rmax=5.0, dr=0.02, targets=[], constraints=[rl.DistanceWindow(win)],
                     max_move={"Na": 0.3, "Cl": 0.3}, seed=2)
    st = eng.run(800)
    assert st.accepted > 0
    d = rt._min_image_distances(box.to_rmc6f(cfg))
    ia, ib = np.where(box.atoms == "Na")[0], np.where(box.atoms == "Cl")[0]
    nearest = np.sort(d[np.ix_(ia, ib)], axis=1)[:, :6]
    assert nearest.min() >= 2.5 and nearest.max() <= 3.1


def test_synthetic_recovery_reproduces_the_partials_not_the_coordinates():
    """Targets synthesised from a thermally displaced 'truth' box (s.d. 0.05 A);
    the fit starts from the ideal lattice. chi2 must fall by > 95 % and every
    partial must land within sigma of its target — while the rms distance to
    the truth's coordinates does NOT shrink: RMC reproduces the pair
    distribution, not the configuration (McGreevy 2001; measured 2026-09-05:
    chi2 1.26e6 -> 422 in 20 000 moves, rms to truth 0.090 -> 0.120 A).
    Fitting delta-sharp targets of the ideal lattice itself is pathological
    (a 0.05 A move rarely lands in the exact 0.02 A bin): 16 % drop in 6000 moves."""
    cfg = nacl(2)
    a = 2 * 5.64
    rng = np.random.default_rng(3)
    truth = rl.Box.from_rmc6f(cfg)
    truth.frac = (truth.frac + rng.normal(0, 0.05, truth.frac.shape) / a) % 1.0
    r, parts, G = rl.synth_targets(truth, rmax=5.0, dr=0.02, noise=0.0, rng=rng)
    start = rl.Box.from_rmc6f(cfg)                       # the ideal lattice
    rms0 = rl.rms_displacement(start, truth)
    targets = [rl.PartialTarget(lab, r, parts[lab], sigma=0.2) for lab in parts]
    eng = rl.RmcLite(start, rmax=5.0, dr=0.02, targets=targets,
                     constraints=[rl.ClosestApproach({"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0})],
                     max_move={"Na": 0.05, "Cl": 0.05}, seed=11)
    chi0 = eng.chi2
    st = eng.run(8000)
    assert eng.chi2 < 0.05 * chi0
    g = eng.hist.g()
    for lab in parts:
        assert np.sqrt(np.mean((g[lab] - parts[lab]) ** 2)) < 0.3, lab      # within 1.5 sigma on average (measured 0.20 on Na-Cl)
    assert rl.rms_displacement(start, truth) > 0.5 * rms0                    # coordinates are not recovered
    assert st.chi2_history[0][1] == pytest.approx(chi0) and st.chi2_history[-1][1] == pytest.approx(eng.chi2)


def test_harmonic_potential_thermalises_the_bond():
    """No data, one harmonic Na-Cl bond potential at T: the Na-Cl first-shell
    distance variance approaches k_B T / k (equipartition, one degree of
    freedom per bond) within 30 %."""
    cfg = nacl(2)
    box = rl.Box.from_rmc6f(cfg)
    k, T = 5.0, 300.0                       # eV/A^2, K
    pot = rl.BondPotential("Na-Cl", k=k, r0=2.82, cutoff=3.2, T=T)
    eng = rl.RmcLite(box, rmax=5.0, dr=0.02, targets=[], potentials=[pot], max_move={"Na": 0.05, "Cl": 0.05}, seed=5)
    eng.run(20000)
    d = rt._min_image_distances(box.to_rmc6f(cfg))
    ia, ib = np.where(box.atoms == "Na")[0], np.where(box.atoms == "Cl")[0]
    bonds = d[np.ix_(ia, ib)]
    bonds = bonds[bonds < 3.2]
    assert bonds.var() == pytest.approx(rl.KB_EV * T / k, rel=0.3)
