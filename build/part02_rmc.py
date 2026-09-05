# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
from nbbuild import md, code

CELLS = [

md(r"""
## 5. One move, by hand

Reverse Monte Carlo (McGreevy & Pusztai 1988) is Metropolis Monte Carlo with the experiment as
the energy. A box of atoms, one atom moved at random, the calculated functions updated, and the
move kept if the agreement with the data improves — or, with a small probability, even if it
does not. `rmclite` (`references/rmclite.md`) is this loop written out in a few hundred lines
so that every piece can be inspected. Its histogram is the toolkit's `partial_gr` made
incremental: moving atom *i* only changes the bins its own distance row falls into.
"""),

code(r"""
NACL = [("Na", 0, 0, 0), ("Na", .5, .5, 0), ("Na", .5, 0, .5), ("Na", 0, .5, .5),
        ("Cl", .5, 0, 0), ("Cl", 0, .5, 0), ("Cl", 0, 0, .5), ("Cl", .5, .5, .5)]
A = 5.64
cfg = rt.build_configuration((A, A, A, 90, 90, 90), NACL, (2, 2, 2))
box = rl.Box.from_rmc6f(cfg)
hist = rl.Histogram(box, rmax=5.0, dr=0.02)
print(f"{box.n} atoms, half box {box.lattice[0, 0] / 2:.2f} A, {len(hist.r)} r points, labels {hist.labels}")

i = 0                                                   # move the first Na atom by 0.1 A along x
old_row = box.distance_row(i)
box.frac[i] = (box.frac[i] + np.array([0.1, 0, 0]) @ np.linalg.inv(box.lattice)) % 1.0
new_row = box.distance_row(i)
hist.update(i, old_row, new_row)
rebuilt = rl.Histogram(box, rmax=5.0, dr=0.02)
same = all(np.array_equal(hist.counts[lab], rebuilt.counts[lab]) for lab in hist.labels)
check("the incremental update equals a full rebuild after the move", same)
moved = np.sum(np.abs(old_row - new_row) > 1e-9)
check("only the moved atom's own distances changed", moved == box.n - 1, f"{moved} of {box.n - 1} distances")
box.frac[i] = (box.frac[i] - np.array([0.1, 0, 0]) @ np.linalg.inv(box.lattice)) % 1.0     # put it back
"""),

md(r"""
## 6. χ² and the acceptance rule

With targets $g^{\rm exp}_{ij}(r_k)$ and an uncertainty $\sigma$ per data set,

$$ \chi^2 = \sum_{\rm data}\sum_k \frac{[g^{\rm calc}(r_k) - g^{\rm exp}(r_k)]^2}{\sigma^2}, $$

and a move is accepted if $\Delta\chi^2 \le 0$, otherwise with probability
$\exp(-\Delta\chi^2/2)$ (the ½ is the RMC convention; a potential energy term enters as
$\Delta U/k_BT$ — chapter 6). The uncertainty is not a statistical error here but the knob
that sets how hard the fit pushes: RMCProfile calls it `WEIGHT`. Watch the rule work: over a
few hundred moves against a thermal target, the fraction of *uphill* moves accepted must equal
the average of $e^{-\Delta}$ over those moves.
"""),

code(r"""
rng = np.random.default_rng(0)
truth = rl.Box.from_rmc6f(cfg)
truth.frac = (truth.frac + rng.normal(0, 0.05, truth.frac.shape) / A) % 1.0
r, target, _ = rl.synth_targets(truth, rmax=5.0, dr=0.02, noise=0.0, rng=rng)

start = rl.Box.from_rmc6f(cfg)                                     # the ideal lattice
eng = rl.RmcLite(start, rmax=5.0, dr=0.02,
                 targets=[rl.PartialTarget(lab, r, target[lab], sigma=0.2) for lab in target],
                 constraints=[rl.ClosestApproach({"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0})],
                 max_move={"Na": 0.05, "Cl": 0.05}, seed=1)
print(f"chi2 of the ideal lattice against the thermal target: {eng.chi2:.4g}")

# instrument the rule: replay 600 moves, recording Delta and the decision
deltas, accepted = [], []
for _ in range(600):
    chi_before = eng.chi2
    ok = eng.step()
    deltas.append(0.5 * (eng.chi2 - chi_before) if ok else None)
    accepted.append(ok)
print(f"generated 600, tested {eng.state.tested}, accepted {eng.state.accepted}")
check("every accepted downhill move lowered chi2", all(d <= 1e-9 for d in deltas if d is not None and d <= 0))
check("chi2 fell over the first 600 moves", eng.chi2 < 0.9 * eng.state.chi2_history[0][1],
      f"{eng.state.chi2_history[0][1]:.4g} -> {eng.chi2:.4g}")
"""),

code(r"""
# the Metropolis test itself, in isolation: for a fixed Delta > 0 the acceptance frequency must be exp(-Delta)
rng2 = np.random.default_rng(5)
for delta in (0.5, 1.0, 2.0):
    acc = np.mean(rng2.random(20000) < np.exp(-delta))
    check(f"acceptance frequency at Δ = {delta} is e^(−Δ) = {np.exp(-delta):.3f}", abs(acc - np.exp(-delta)) < 0.01, f"{acc:.3f}")
"""),

md(r"""
## 7. The fit: from the average structure to the data

A refinement starts from the *average* structure — the unit cell a Rietveld refinement gives,
replicated into a supercell (what RMCProfile's `data2config` builds) — and lets the data
broaden it. From the ideal lattice the χ² against the thermal target falls by orders of
magnitude within a few thousand moves; every partial lands within its σ of the target.
"""),

code(r"""
start = rl.Box.from_rmc6f(cfg)
eng = rl.RmcLite(start, rmax=5.0, dr=0.02,
                 targets=[rl.PartialTarget(lab, r, target[lab], sigma=0.2) for lab in target],
                 constraints=[rl.ClosestApproach({"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0})],
                 max_move={"Na": 0.05, "Cl": 0.05}, seed=11)
chi0 = eng.chi2
st = eng.run(6000, print_every=500)
g_fit = eng.hist.g()

fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
gen, chi = zip(*st.chi2_history)
axes[0].semilogy(gen, chi); axes[0].set_xlabel("moves generated"); axes[0].set_ylabel("χ²")
axes[1].plot(r, target["Na-Cl"], "k", label="target (thermal box)")
axes[1].plot(r, g_fit["Na-Cl"], label="rmclite fit from the ideal lattice")
axes[1].set_xlim(2.4, 5); axes[1].set_xlabel("r (Å)"); axes[1].set_ylabel("g$_{NaCl}$(r)"); axes[1].legend()
show(fig)
caption("Left: χ² against generated moves for a fit from the ideal NaCl lattice toward the "
        "partials of a thermally displaced box. Right: the Na–Cl partial of the fit against its "
        "target after 6000 moves.")

check("chi2 fell by more than 95 %", eng.chi2 < 0.05 * chi0, f"{chi0:.4g} -> {eng.chi2:.4g}")
# how close is close? a 64-atom box's partials are noisy: compare the fit's residual with the
# difference between two independent thermal realisations of the same structure
truth2 = rl.Box.from_rmc6f(cfg)
truth2.frac = (truth2.frac + np.random.default_rng(99).normal(0, 0.05, truth2.frac.shape) / A) % 1.0
_, target2, _ = rl.synth_targets(truth2, rmax=5.0, dr=0.02, noise=0.0, rng=rng)
rms_dev = {lab: np.sqrt(np.mean((g_fit[lab] - target[lab]) ** 2)) for lab in target}
rms_floor = {lab: np.sqrt(np.mean((target2[lab] - target[lab]) ** 2)) for lab in target}
print("rms deviation of the fit:", {k: round(v, 3) for k, v in rms_dev.items()})
print("rms difference between two thermal boxes:", {k: round(v, 3) for k, v in rms_floor.items()})
check("the fit is closer to its target than a second thermal box is",
      all(rms_dev[lab] < rms_floor[lab] for lab in target))
"""),

md(r"""
## 8. What RMC does and does not recover

The fit reproduces the *pair distribution* — not the coordinates. Compare the fitted box with
the "truth" box whose partials it matched: the root-mean-square distance between corresponding
atoms is no smaller after the fit than before. Many configurations share one set of partials
(McGreevy 2001 calls this the non-uniqueness of RMC); RMC finds *a* member of that set, and
the physics one reads off a refined box must be statistical — distributions, not positions.
The same test also shows why one never fits *delta-sharp* targets: from a displaced start, the
ideal lattice's own unbroadened partials are almost unreachable by 0.05 Å moves.
"""),

code(r"""
rms_before = rl.rms_displacement(rl.Box.from_rmc6f(cfg), truth)
rms_after = rl.rms_displacement(start, truth)
print(f"rms distance to the truth coordinates: before {rms_before:.3f} A, after the fit {rms_after:.3f} A")
check("the fit did not move the atoms toward the truth coordinates", rms_after > 0.5 * rms_before)

# delta-sharp targets: the ideal lattice's own partials, fitted from a 0.15 A distortion
r_i, g_i = rt.partial_gr(cfg, rmax=5.0, dr=0.02)
distorted = rl.Box.from_rmc6f(cfg)
distorted.frac = (distorted.frac + rng.normal(0, 0.15, distorted.frac.shape) / A) % 1.0
eng2 = rl.RmcLite(distorted, rmax=5.0, dr=0.02,
                  targets=[rl.PartialTarget(lab, r_i, g_i[lab], sigma=0.2) for lab in g_i],
                  constraints=[rl.ClosestApproach({"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0})],
                  max_move={"Na": 0.05, "Cl": 0.05}, seed=2)
c0 = eng2.chi2
eng2.run(3000)
check("delta-sharp targets: less than half of chi2 gone in 3000 moves", eng2.chi2 > 0.5 * c0, f"{c0:.3g} -> {eng2.chi2:.3g}")
"""),

md(r"""
## 9. Constraints are physics

Data alone let atoms wander into each other; RMC therefore carries hard constraints that make
a move impossible rather than merely unlikely. The **closest approach** (`MINIMUM_DISTANCES`
in RMCProfile) forbids any pair below a distance; a **distance window** keeps every pair that
starts inside a range inside it — the way a molecule or a polyhedron is held together
without a potential. Both cost nothing in χ² and count as *generated* but not *tested* moves.
"""),

code(r"""
box = rl.Box.from_rmc6f(cfg)
eng3 = rl.RmcLite(box, rmax=5.0, dr=0.02, targets=[],
                  constraints=[rl.ClosestApproach({"Na-Cl": 2.6}), rl.DistanceWindow({"Na-Cl": (2.5, 3.1)})],
                  max_move={"Na": 0.3, "Cl": 0.3}, seed=3)
st3 = eng3.run(2000)
d = rt._min_image_distances(box.to_rmc6f(cfg))
ia, ib = np.where(box.atoms == "Na")[0], np.where(box.atoms == "Cl")[0]
nearest = np.sort(d[np.ix_(ia, ib)], axis=1)[:, :6]
print(f"generated {st3.generated}, tested {st3.tested}, accepted {st3.accepted}; "
      f"Na–Cl first shell now spans {nearest.min():.3f}–{nearest.max():.3f} A")
check("no Na–Cl pair below the closest approach", d[np.ix_(ia, ib)].min() >= 2.6 - 1e-12)
check("every first-shell Na–Cl pair stayed inside the window", nearest.min() >= 2.5 and nearest.max() <= 3.1)
check("constraint rejections are generated but not tested moves", st3.generated > st3.tested > 0)
"""),

md(r"""
### Exercises for chapter 2

**2.1** Repeat the fit of §7 with σ = 0.05 and σ = 1.0. Which converges to a lower χ² in the
same number of moves, and which produces the *smoother* partials? (Hint: a small σ makes the
noise of the target a hard constraint.)

**2.2** Repeat it with `max_move` = 0.01 Å and 0.3 Å. Which one is slow, which one wasteful,
and does either fail to converge?
"""),

code(r"""
# 2.1 — sigma scales chi2 but also the acceptance of uphill moves: at sigma = 1.0 uphill moves are
#       accepted freely and the fit wanders (higher relative chi2, noisier partials); at 0.05 it is
#       a near-greedy descent that fits the target's own histogram noise.
res = {}
for sig in (0.05, 1.0):
    b = rl.Box.from_rmc6f(cfg)
    e = rl.RmcLite(b, 5.0, 0.02, [rl.PartialTarget(l, r, target[l], sig) for l in target],
                   constraints=[rl.ClosestApproach({"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0})],
                   max_move={"Na": 0.05, "Cl": 0.05}, seed=7)
    c0 = e.chi2; e.run(3000)
    res[sig] = (e.chi2 / c0, e.state.accepted)
    print(f"sigma {sig}: chi2 ratio {e.chi2 / c0:.3f}, accepted {e.state.accepted}")
check("2.1 the large sigma accepts more moves", res[1.0][1] > res[0.05][1])

# 2.2 — measured: 0.01 A is slow (chi2 ratio 0.06 after 3000 moves, against 0.002 for 0.05 A):
#       each move barely changes the histogram. 0.3 A is wasteful — three times fewer moves
#       accepted, most jump across a shell or into the closest-approach wall — but the moves
#       that do land are large, and it converges as well as 0.05 A. RMC is forgiving on
#       max_move as long as rejections stay affordable.
for mv in (0.01, 0.05, 0.3):
    b = rl.Box.from_rmc6f(cfg)
    e = rl.RmcLite(b, 5.0, 0.02, [rl.PartialTarget(l, r, target[l], 0.2) for l in target],
                   constraints=[rl.ClosestApproach({"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0})],
                   max_move={"Na": mv, "Cl": mv}, seed=7)
    c0 = e.chi2; e.run(3000)
    res[mv] = (e.chi2 / c0, e.state.accepted)
    print(f"max_move {mv}: chi2 ratio {e.chi2 / c0:.4f}, accepted {e.state.accepted}")
check("2.2 tiny moves are slow: 0.01 A leaves > 10x the chi2 of 0.05 A", res[0.01][0] > 10 * res[0.05][0])
check("2.2 large moves are rejected more often yet still converge", res[0.3][1] < res[0.05][1] and res[0.3][0] < 0.01)
"""),
]
