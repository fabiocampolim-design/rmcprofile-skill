# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Configuration analysis, checked against exact geometry (rock-salt NaCl,
a = 5.64 Å) and against Keen's definitions of G(r) and F(Q)."""

import numpy as np
import pytest

import rmcprofile_tools as rt


def nacl(n=3):
    """n x n x n supercell of rock-salt NaCl, a = 5.64 Å."""
    a = 5.64
    base = {"Na": [(0, 0, 0), (.5, .5, 0), (.5, 0, .5), (0, .5, .5)],
            "Cl": [(.5, 0, 0), (0, .5, 0), (0, 0, .5), (.5, .5, .5)]}
    atoms, frac, site, cell = [], [], [], []
    for el in ("Na", "Cl"):
        for i, j, k in np.ndindex(n, n, n):
            for s, (x, y, z) in enumerate(base[el]):
                atoms.append(el)
                frac.append([(x + i) / n, (y + j) / n, (z + k) / n])
                site.append(s + 1 + (4 if el == "Cl" else 0))
                cell.append([i, j, k])
    N = len(atoms)
    return rt.Rmc6f(atom_types=["Na", "Cl"], counts=[N // 2, N // 2], cell=(n * a,) * 3 + (90.0,) * 3,
                    lattice=n * a * np.eye(3), supercell=(n, n, n), density=N / (n * a) ** 3,
                    atoms=np.array(atoms, dtype=object), frac=np.array(frac), site=np.array(site), cellidx=np.array(cell))


def test_pair_labels_follow_the_manual_order():
    assert rt.pair_labels(["S", "F"]) == ["S-S", "S-F", "F-F"]
    assert rt.pair_labels(["Sr", "Ti", "O"]) == ["Sr-Sr", "Sr-Ti", "Sr-O", "Ti-Ti", "Ti-O", "O-O"]


def test_partial_gr_peaks_at_the_rock_salt_distances():
    cfg = nacl(3)
    r, g = rt.partial_gr(cfg, rmax=8.0, dr=0.02)
    first_nacl = r[np.nonzero(g["Na-Cl"])[0][0]]                 # an ideal lattice distance can sit on a bin edge
    assert first_nacl == pytest.approx(2.82, abs=0.02)          # a/2
    first_nana = r[np.nonzero(g["Na-Na"])[0][0]]
    assert first_nana == pytest.approx(3.988, abs=0.02)         # a/sqrt2
    assert g["Na-Cl"][(r > 3.0) & (r < 3.8)].max() == 0.0        # nothing between the shells
    # normalisation: integral of 4*pi*r^2*rho_Cl*g_NaCl over the first shell = 6 neighbours
    rho_cl = cfg.counts[1] / np.prod(cfg.cell[:3])
    shell = (r > 2.6) & (r < 3.0)
    assert np.sum(4 * np.pi * r[shell] ** 2 * rho_cl * g["Na-Cl"][shell] * 0.02) == pytest.approx(6.0, rel=0.02)


def test_total_gr_at_r_zero_is_minus_the_square_of_the_mean_scattering_length():
    """Keen 2001: G(r) -> -(sum_i c_i b_i)^2 as r -> 0. For SF6 the tutorial data
    files start at -0.2759 barn — our own arithmetic must give the same number."""
    cfg = rt.Rmc6f(atom_types=["S", "F"], counts=[1, 6])
    w = rt.neutron_weights(cfg)
    g0 = sum(w[p] * (0.0 - 1.0) for p in rt.pair_labels(["S", "F"]))
    assert g0 == pytest.approx(-0.2759, abs=0.0005)
    assert rt.NEUTRON_B["S"] == pytest.approx(2.847) and rt.NEUTRON_B["F"] == pytest.approx(5.654)


def test_total_gr_and_fq_on_nacl():
    cfg = nacl(3)
    r, parts = rt.partial_gr(cfg, rmax=8.0, dr=0.02)
    r2, G = rt.total_gr(r, parts, cfg, radiation="neutron")
    assert np.allclose(r, r2)
    cNa = cCl = 0.5
    assert G[0] == pytest.approx(-(cNa * rt.NEUTRON_B["Na"] + cCl * rt.NEUTRON_B["Cl"]) ** 2 / 100, rel=1e-6)
    q = np.arange(0.5, 20.0, 0.02)
    F = rt.fq_from_gr(r, G, cfg.density, q)
    assert F.shape == q.shape and np.isfinite(F).all()
    # first strong maximum of F(Q) for NaCl near Q = 2*pi/d(200) = 2*pi/2.82
    win = (q > 1.5) & (q < 3.0)
    assert q[win][np.argmax(F[win])] == pytest.approx(2 * np.pi / 2.82, abs=0.15)


def test_coordination_and_angles_are_exact_for_the_ideal_lattice():
    cfg = nacl(2)
    counts, hist = rt.coordination(cfg, "Na", "Cl", rmax=3.0)
    assert hist == {6: cfg.counts[0]} and counts.sum() == 6 * cfg.counts[0]
    ang = rt.bond_angles(cfg, "Na", "Cl", "Cl", rmax=3.0)
    assert len(ang) == cfg.counts[0] * 15                      # C(6,2) = 15 Cl-Na-Cl angles per Na
    assert sorted(set(np.round(ang, 3))) == [90.0, 180.0]
    assert np.sum(np.isclose(ang, 180.0)) == cfg.counts[0] * 3


def test_average_cell_divides_by_the_supercell():
    cfg = nacl(3)
    assert rt.average_cell(cfg) == pytest.approx((5.64, 5.64, 5.64, 90.0, 90.0, 90.0))


def test_rmax_beyond_half_cell_is_refused():
    with pytest.raises(ValueError, match="half the shortest cell edge"):
        rt.partial_gr(nacl(1), rmax=5.0, dr=0.02)


def test_pdf_subcommand_writes_csvs(tmp_path):
    cfg = nacl(2)
    p = tmp_path / "nacl.rmc6f"
    cfg.write(p)
    rc = rt.main(["pdf", str(p), "--rmax", "5", "--outdir", str(tmp_path / "out"), "--log-dir", str(tmp_path / "logs"), "-q"])
    assert rc == 0
    r, parts = rt.read_partials_csv(tmp_path / "out" / "nacl_PDFpartials.csv")
    assert list(parts) == ["Na-Na", "Na-Cl", "Cl-Cl"] and len(r) > 100
    x, calc, _ = rt.read_csv_pair(tmp_path / "out" / "nacl_GofR.csv")
    assert calc[0] == pytest.approx(-(0.5 * rt.NEUTRON_B["Na"] + 0.5 * rt.NEUTRON_B["Cl"]) ** 2 / 100, rel=1e-6)
    rc = rt.main(["coord", str(p), "--pair", "Na", "Cl", "--rmax", "3.0", "--log-dir", str(tmp_path / "logs"), "-q"])
    assert rc == 0
    rc = rt.main(["angles", str(p), "--triplet", "Na", "Cl", "Cl", "--rmax", "3.0", "--outdir", str(tmp_path / "out"),
                  "--log-dir", str(tmp_path / "logs"), "-q"])
    assert rc == 0 and (tmp_path / "out" / "nacl_angles_Cl-Na-Cl.csv").is_file()


def test_partial_gr_in_blocks_equals_the_full_matrix():
    """0.5.5: partial_gr histograms row blocks instead of the N x N distance matrix (4.4 GB on
    the 14 000-atom SF6 exercise); the counts must be identical, block size notwithstanding."""
    cfg = nacl(3)
    rng = np.random.default_rng(3)
    cfg.frac = (cfg.frac + rng.normal(0, 0.01, cfg.frac.shape)) % 1.0
    r, ref = rt.partial_gr(cfg, rmax=8.0, dr=0.02)
    dist = rt._min_image_distances(cfg)
    idx = {t: np.where(cfg.atoms == t)[0] for t in cfg.atom_types}
    _, edges = rt.rmc_grid(8.0, 0.02)
    for lab, g in ref.items():
        a, b = lab.split("-")
        block = dist[np.ix_(idx[a], idx[b])]
        h, _ = np.histogram(block[np.isfinite(block)], bins=edges)
        V = abs(np.linalg.det(cfg.lattice))
        full = h / (len(idx[a]) * (len(idx[b]) / V) * 4 * np.pi * r ** 2 * 0.02)
        assert np.allclose(full, g, rtol=1e-12, atol=0), lab      # same counts; only the float association differs
    small = list(rt._distance_blocks(cfg, idx["Na"], idx["Na"], block=7))
    assert sum(x.shape[0] for x in small) == len(idx["Na"]) and small[0].shape == (7, len(idx["Na"]))
    assert np.isinf(small[0][np.arange(7), np.arange(7)]).all()          # an atom with itself is never a pair
