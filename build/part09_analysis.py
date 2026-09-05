# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
from nbbuild import md, code

CELLS = [

md(r"""
## 35. A refined box is a statistical object

Chapter 2 showed that RMC reproduces the pair distribution, not the coordinates; chapter 4
refined a box against synthetic data. What one reads off such a box must therefore be
*distributions* — coordination numbers, bond lengths, bond angles, displacement clouds —
never the position of a particular atom. This chapter takes the boxes this book can make
without the package (an `rmclite` fit of the chapter-4 synthetic data) and shows the four
analyses the toolkit offers, each checked against the answer the synthetic truth knows.
"""),

code(r"""
NACL = [("Na", 0, 0, 0), ("Na", .5, .5, 0), ("Na", .5, 0, .5), ("Na", 0, .5, .5),
        ("Cl", .5, 0, 0), ("Cl", 0, .5, 0), ("Cl", 0, 0, .5), ("Cl", .5, .5, .5)]
A = 5.64
cfg = rt.build_configuration((A, A, A, 90, 90, 90), NACL, (3, 3, 3), title="NaCl 3x3x3")
rng = np.random.default_rng(0)
truth = rl.Box.from_rmc6f(cfg)
truth.frac = (truth.frac + rng.normal(0, 0.05, truth.frac.shape) / cfg.cell[0]) % 1.0
r, g_truth, G_truth = rl.synth_targets(truth, rmax=8.0, dr=0.02, noise=0.0, rng=rng)

def fit_box(seed, moves=6000):
    box = rl.Box.from_rmc6f(cfg)
    eng = rl.RmcLite(box, rmax=8.0, dr=0.02, targets=[rl.PartialTarget(lab, r, g_truth[lab], 0.2) for lab in g_truth],
                     constraints=[rl.ClosestApproach({"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0})],
                     max_move={"Na": 0.05, "Cl": 0.05}, seed=seed)
    c0 = eng.chi2
    eng.run(moves)
    return box.to_rmc6f(cfg), c0, eng.chi2

fitted, c0, c1 = fit_box(1)
print(f"rmclite fit from the ideal lattice: chi2 {c0:.3g} -> {c1:.3g}")
check("a refined box to analyse (chi2 fell by > 95 %)", c1 < 0.05 * c0)
"""),

md(r"""
## 36. Coordination numbers and bond lengths

`coordination(cfg, A, B, rmax)` counts the B atoms within `rmax` of every A atom and
returns the per-atom counts and their histogram — in rock salt every Na keeps six Cl
neighbours within 3.2 Å whatever the thermal motion, so the histogram is a single bar.
The bond-length distribution is the Na–Cl partial itself, weighted by the shell; its mean
and width are the two numbers a neutron PDF is usually asked for.
"""),

code(r"""
counts, hist = rt.coordination(fitted, "Na", "Cl", rmax=3.2)
counts_t, hist_t = rt.coordination(truth.to_rmc6f(cfg), "Na", "Cl", rmax=3.2)
print("fitted box: Na coordination histogram", hist, "| truth:", hist_t)
r_f, g_f = rt.partial_gr(fitted, rmax=8.0, dr=0.02)
shell = (r_f > 2.4) & (r_f < 3.2)
wgt = g_f["Na-Cl"][shell] * r_f[shell] ** 2
d_mean = np.sum(wgt * r_f[shell]) / np.sum(wgt)
d_std = np.sqrt(np.sum(wgt * (r_f[shell] - d_mean) ** 2) / np.sum(wgt))
wgt_t = g_truth["Na-Cl"][shell] * r[shell] ** 2
t_mean = np.sum(wgt_t * r[shell]) / np.sum(wgt_t)
t_std = np.sqrt(np.sum(wgt_t * (r[shell] - t_mean) ** 2) / np.sum(wgt_t))
print(f"Na–Cl bond: fitted {d_mean:.3f} ± {d_std:.3f} Å, truth {t_mean:.3f} ± {t_std:.3f} Å")

fig, ax = plt.subplots()
ax.bar(list(hist), list(hist.values()), width=0.6, label="fitted box")
ax.set_xlabel("Cl neighbours within 3.2 Å of a Na"); ax.set_ylabel("Na atoms"); ax.legend()
show(fig)
caption("Coordination-number histogram of the refined NaCl box: every one of the 108 Na atoms "
        "keeps its six Cl neighbours — thermal motion broadens shells, it does not change "
        "coordination in a close-packed ionic crystal.")
check("every Na keeps six Cl neighbours in the refined box", hist == {6: 108}, str(hist))
check("the mean Na–Cl bond length is the truth's within 0.01 Å", abs(d_mean - t_mean) < 0.01, f"{d_mean:.3f} vs {t_mean:.3f} Å")
check("the bond-length width is the truth's within 30 %", abs(d_std - t_std) < 0.3 * t_std, f"{d_std:.3f} vs {t_std:.3f} Å")
"""),

md(r"""
## 37. Bond angles and displacement clouds

`bond_angles(cfg, A, B, C, rmax)` returns every B–A–C angle whose two arms are within
`rmax`; in rock salt the Cl–Na–Cl angles are 90° and 180° and thermal motion spreads them
by a few degrees. `fold_to_unit_cell` collapses the supercell onto one cell so that the
displacement cloud of a site can be seen and measured.
"""),

code(r"""
ang = rt.bond_angles(fitted, "Na", "Cl", "Cl", rmax=3.2)
ang_t = rt.bond_angles(truth.to_rmc6f(cfg), "Na", "Cl", "Cl", rmax=3.2)
# displacement of every atom from its own ideal site (same atom order in both boxes), in Å
def displacements(box_cfg):
    d = box_cfg.frac - cfg.frac
    d -= np.round(d)
    return d @ cfg.lattice
na = displacements(fitted)[fitted.atoms == "Na"]
na_t = displacements(truth.to_rmc6f(cfg))[cfg.atoms == "Na"]
frac_cell, idx = rt.fold_to_unit_cell(fitted)              # the same atoms folded into one cell (for the record)

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].hist(ang, bins=np.arange(70, 191, 2), alpha=0.6, label="fitted box")
axes[0].hist(ang_t, bins=np.arange(70, 191, 2), histtype="step", color="k", label="truth")
axes[0].set_xlabel("Cl–Na–Cl angle (°)"); axes[0].set_ylabel("count"); axes[0].legend()
axes[1].scatter(na[:, 0], na[:, 1], s=6, alpha=0.6, label="fitted")
axes[1].set_xlabel("x − x₀ (Å)"); axes[1].set_ylabel("y − y₀ (Å)"); axes[1].set_aspect("equal"); axes[1].legend()
show(fig)
caption("Left: the Cl–Na–Cl angle distribution of the refined box (filled) and of the truth "
        "box (line): two peaks at 90° and 180° broadened by the thermal displacements. Right: "
        "the displacement of each of the 108 Na atoms from its ideal site, projected on ab — "
        "the displacement cloud of the Na site.")
near90 = ang[(ang > 70) & (ang < 110)]
check("the 90° peak is where it should be", abs(np.median(near90) - 90) < 1.0, f"median {np.median(near90):.1f}°")
check("the angle spread of the fit matches the truth's within 30 %", abs(near90.std() - ang_t[(ang_t > 70) & (ang_t < 110)].std()) < 0.3 * ang_t[(ang_t > 70) & (ang_t < 110)].std(),
      f"{near90.std():.2f}° vs {ang_t[(ang_t > 70) & (ang_t < 110)].std():.2f}°")
check("the Na displacement cloud has a thermal width", 0.03 < na[:, 0].std() < 0.12, f"{na[:, 0].std():.3f} Å (truth {na_t[:, 0].std():.3f} Å)")
"""),

md(r"""
## 38. Ensembles: several fits are better than one

One fitted box carries the statistical noise of its 216 atoms. Refining several boxes with
different seeds and averaging their partials reduces that noise — the average partial is
closer to the target than any single fit, and the spread between fits is the honest error
bar of anything read off a box. RMCProfile users do the same with several independent runs.
"""),

code(r"""
boxes = [fitted] + [fit_box(seed, moves=4000)[0] for seed in (2, 3, 4)]
parts = [rt.partial_gr(b, rmax=8.0, dr=0.02)[1]["Na-Cl"] for b in boxes]
mean_part = np.mean(parts, axis=0)
dev_single = [np.sqrt(np.mean((p - g_truth["Na-Cl"]) ** 2)) for p in parts]
dev_mean = np.sqrt(np.mean((mean_part - g_truth["Na-Cl"]) ** 2))
print("rms deviation from the target: single fits", np.round(dev_single, 3), "| ensemble mean", round(dev_mean, 3))
fig, ax = plt.subplots()
ax.plot(r, g_truth["Na-Cl"], "k", label="target")
for k, p in enumerate(parts):
    ax.plot(r, p, lw=0.6, alpha=0.5, label=f"fit {k + 1}" if k < 2 else None)
ax.plot(r, mean_part, "C3", lw=1.5, label="ensemble mean of 4 fits")
ax.set_xlim(2.4, 4.5); ax.set_xlabel("r (Å)"); ax.set_ylabel("g$_{NaCl}$(r)"); ax.legend()
show(fig)
caption("Four rmclite fits of the same synthetic data from different seeds (thin) and their "
        "mean (red) against the target (black): averaging over an ensemble beats any single "
        "box, and the spread between boxes is the error bar.")
check("the ensemble mean is closer to the target than every single fit", dev_mean < min(dev_single),
      f"{dev_mean:.3f} vs best single {min(dev_single):.3f}")
"""),

md(r"""
### Exercises for chapter 9

**9.1** Compute the Na–Na coordination within 4.3 Å (the second shell) of the fitted box.
How many neighbours, and is the histogram still a single bar?

**9.2** Export the fitted box to XYZ and CIF and confirm that the CIF's cell is the
supercell (16.92 Å) while `average_cell` gives 5.64 Å.
"""),

code(r"""
# 9.1 — twelve Na–Na neighbours at a/sqrt2 = 3.99 A; thermal motion does not break the shell
counts2, hist2 = rt.coordination(fitted, "Na", "Na", rmax=4.3)
print("Na–Na within 4.3 Å:", hist2)
check("9.1 twelve Na–Na second-shell neighbours for every Na", hist2 == {12: 108}, str(hist2))

# 9.2
rt.export_xyz(fitted, os.path.join(WORK, "fitted.xyz"))
rt.export_cif(fitted, os.path.join(WORK, "fitted.cif"))
with open(os.path.join(WORK, "fitted.cif"), encoding="utf-8") as f:
    cif = f.read()
check("9.2 the CIF cell is the supercell and the average cell the unit cell",
      "_cell_length_a   16.920000" in cif and abs(rt.average_cell(fitted)[0] - 5.64) < 1e-9)
"""),
]
