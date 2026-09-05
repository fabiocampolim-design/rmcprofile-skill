# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
from nbbuild import md, code

CELLS = [

md(r"""
## 28. What the instrument does to G(r)

A measured $F(Q)$ ends at a finite $Q_{\max}$ and is smeared by the instrument's resolution;
its Fourier transform $G(r)$ is therefore damped at large $r$ and its peaks broadened.
RMCProfile corrects the *calculated* function so that it can be compared with the data as
measured (manual §4.1, App. F): `RESOLUTION_CORRECTION` damps the calculated real-space
function, `BROADENING_CORRECTION` convolves it with a Gaussian whose width grows with $r$,
`R_CUTOFF` zeroes the Fourier ripples below the closest approach, and `PARTICLE_RADIUS`
applies a nanoparticle shape function. As in chapter 4 the data are synthetic, so the right
correction is known and the wrong one measurable — and everything runs at `TIME_LIMIT 0`,
which makes every comparison deterministic: one evaluation of the ideal lattice against
the data, no moves.
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
G0 = -sum(c * rt.NEUTRON_B[t] for t, c in zip(cfg.atom_types, np.array(cfg.counts) / cfg.n_atoms())) ** 2 * rt.BARN_PER_FM2
print(f"G(r -> 0) = -(sum c b)^2 = {G0:.4f} barn")

def evaluate(tag, G_data, block_items=(), scalars=()):
    '''One RMCProfile pass (TIME_LIMIT 0) of the ideal lattice against G_data; returns (chi2, r, calc, expt).'''
    work = os.path.join(WORK, tag)
    rt.write_input_set("k", work, cfg, gr=(r, G_data), min_dist={"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0},
                       max_move=0.05, time_limit_min=0.0, title=tag)
    d = rt.read_dat(os.path.join(work, "k.dat"))
    for k, v in block_items:
        d.set("NEUTRON_REAL_SPACE_DATA", k, v)
    for k, v in scalars:
        d.scalars[k] = v
        d.order.append(("scalar", k))
    d.write(os.path.join(work, "k.dat"))
    res = rt.run_rmcprofile("k", work, PKG, timeout_min=3)
    if res.returncode != 0 or not res.final_chi2:
        raise RuntimeError(f"{tag}: rc={res.returncode}; see {res.log_path}")
    x, calc, expt = rt.read_csv_pair(os.path.join(work, "k_PDF1.csv"))
    chi = res.final_chi2["Expt_1"]
    print(f"{tag:14s}: Expt_1 chi2 = {chi:.4g}")
    return chi, x, calc, expt

print("synthetic thermal G(r) ready;", "package found" if PKG else "no package")
"""),

md(r"""
## 29. Damping: `RESOLUTION_CORRECTION` — measured, not assumed

The manual describes the keyword's value as "the exponent accounting for the dampening in
real-space … in the form of exp(−r∗Expo)". Before trusting a formula, measure it: evaluate
the same ideal lattice against the same data with and without the keyword and divide the
two calculated columns. The ratio below is not $e^{-\alpha r}$; it is the Gaussian
$e^{-(\alpha r)^2/2}$ — the form PDFgui calls `Qdamp`. This is the book's finding P-17:
the program is consistent, the manual's formula is not the one it applies.
"""),

code(r"""
if not skip_without_package("the damping measurement"):
    chi_ref, x, calc_ref, _ = evaluate("ref", G_truth)
    chi_a, _, calc_a, _ = evaluate("damp_measure", G_truth, [("RESOLUTION_CORRECTION", "0.20")])
    alpha_probe = 0.20
    ok = np.abs(calc_ref) > 0.05                    # avoid the zero crossings
    ratio = calc_a[ok] / calc_ref[ok]
    dev_exp = np.max(np.abs(ratio - np.exp(-alpha_probe * x[ok])))
    dev_gauss = np.max(np.abs(ratio - np.exp(-0.5 * (alpha_probe * x[ok]) ** 2)))
    print(f"max |ratio - exp(-a r)| = {dev_exp:.3f};  max |ratio - exp(-(a r)^2/2)| = {dev_gauss:.1e}")
    fig, ax = plt.subplots()
    ax.plot(x[ok], ratio, "k.", ms=3, label="calc(with RESOLUTION_CORRECTION 0.20) / calc(without)")
    ax.plot(x, np.exp(-alpha_probe * x), "--", label="exp(−α r)  (manual)")
    ax.plot(x, np.exp(-0.5 * (alpha_probe * x) ** 2), label="exp(−(α r)²/2)  (measured)")
    ax.set_xlabel("r (Å)"); ax.set_ylabel("ratio"); ax.legend()
    show(fig)
    caption("The damping RMCProfile applies for RESOLUTION_CORRECTION 0.20, measured as the "
            "ratio of two calculated G(r) columns of the same box: a Gaussian in r, not the "
            "exponential the manual writes.")
    check("the measured damping is Gaussian, exp(−(α r)²/2), to 1e-3", dev_gauss < 1e-3, f"{dev_gauss:.1e}")
    check("and it is not exp(−α r)", dev_exp > 0.1, f"{dev_exp:.3f}")
"""),

md(r"""
With the form known, synthesise "measured" data from the thermal box's $G(r)$ damped by
$e^{-(\alpha r)^2/2}$ with $\alpha = 0.05$ Å⁻¹, and evaluate the ideal lattice against
them with no correction, with the right $\alpha$, and with a wrong one. The χ² of the data
set is lowest for the right correction.
"""),

code(r"""
alpha = 0.05
G_damped = G_truth * np.exp(-0.5 * (alpha * r) ** 2)
if not skip_without_package("the damping comparison"):
    chi_none, x, calc_none, expt = evaluate("damp_none", G_damped)
    chi_right, _, calc_right, _ = evaluate("damp_right", G_damped, [("RESOLUTION_CORRECTION", "0.05")])
    chi_wrong, _, calc_wrong, _ = evaluate("damp_wrong", G_damped, [("RESOLUTION_CORRECTION", "0.20")])
    fig, ax = plt.subplots()
    ax.plot(x, expt, "k", lw=0.8, label="damped 'data' (α = 0.05 Å⁻¹)")
    ax.plot(x, calc_none, lw=0.8, alpha=0.7, label="ideal lattice, no correction")
    ax.plot(x, calc_right, lw=0.8, label="ideal lattice, RESOLUTION_CORRECTION 0.05")
    ax.set_xlim(2, 8); ax.set_xlabel("r (Å)"); ax.set_ylabel("G(r) (barn)"); ax.legend()
    show(fig)
    caption("Synthetic G(r) damped by exp(−(0.05 r)²/2) against RMCProfile's calculated G(r) "
            "of the ideal lattice without and with the matching RESOLUTION_CORRECTION: the "
            "corrected model's peaks shrink with r the way the data's do.")
    check("the right damping gives the lowest chi2 of the three", chi_right < chi_none and chi_right < chi_wrong,
          f"none {chi_none:.4g}, right {chi_right:.4g}, wrong {chi_wrong:.4g}")
"""),

md(r"""
## 30. Broadening: `BROADENING_CORRECTION`

Finite resolution in $Q$ also broadens each peak in $r$ by an amount growing with $r$:
RMCProfile convolves its calculated function with a Gaussian of $\sigma = \beta r$ (App. F,
eq. F.1; the parameter is not PDFgui's `Qbroad`, eq. F.2 relates them). Synthesise data
broadened that way — the toolkit does the $r$-dependent convolution explicitly — and the
matching $\beta$ again wins the χ² comparison.
"""),

code(r"""
def broaden(G, r, beta):
    '''Convolve G(r) with a Gaussian whose width grows as beta*r (the r-dependent broadening of App. F).'''
    out = np.zeros_like(G)
    dr = r[1] - r[0]
    for k, rk in enumerate(r):
        s = max(beta * rk, dr)
        w = np.exp(-0.5 * ((r - rk) / s) ** 2)
        out[k] = np.sum(w * G) / np.sum(w)
    return out

beta = 0.02
G_broad = broaden(G_truth, r, beta)
if not skip_without_package("the broadening comparison"):
    chi_b_none, x, calc_b_none, expt_b = evaluate("broad_none", G_broad)
    chi_b_right, _, calc_b_right, _ = evaluate("broad_right", G_broad, [("BROADENING_CORRECTION", "0.02")])
    chi_b_wrong, _, calc_b_wrong, _ = evaluate("broad_wrong", G_broad, [("BROADENING_CORRECTION", "0.08")])
    fig, ax = plt.subplots()
    ax.plot(x, expt_b, "k", lw=0.8, label="broadened 'data' (β = 0.02)")
    ax.plot(x, calc_b_none, lw=0.8, alpha=0.7, label="ideal lattice, no correction")
    ax.plot(x, calc_b_right, lw=0.8, label="ideal lattice, BROADENING_CORRECTION 0.02")
    ax.set_xlim(5.5, 8); ax.set_xlabel("r (Å)"); ax.set_ylabel("G(r) (barn)"); ax.legend()
    show(fig)
    caption("At large r the r-dependent broadening is visible: the uncorrected ideal-lattice "
            "peaks are sharp, the corrected ones spread like the synthetic data's.")
    peak = (x > 7.6) & (x < 8.0)
    check("the corrected column is broader than the uncorrected one at large r",
          calc_b_right[peak].max() < calc_b_none[peak].max())
    check("the right broadening gives the lowest chi2 of the three", chi_b_right < chi_b_none and chi_b_right < chi_b_wrong,
          f"none {chi_b_none:.4g}, right {chi_b_right:.4g}, wrong {chi_b_wrong:.4g}")
"""),

md(r"""
## 31. Nano-size: the shape envelope

In a nanoparticle the number of pairs at distance $r$ is reduced by the fraction that fits
inside the particle — for a sphere of diameter $D$ the envelope is $f(r) = 1 - \tfrac32
(r/D) + \tfrac12 (r/D)^3$ (Guinier). It multiplies the *pair* function, so in Keen's
$G(r) = \sum c_i c_j b_i b_j (g_{ij} - 1)$ it acts on $G - G(0)$ and leaves the baseline
$G(0) = -(\sum c b)^2$ alone: $G_{\rm nano} = f\,(G - G_0) + G_0$. RMCProfile applies it when
`PARTICLE_RADIUS ::` is given, and insists on a `BULK_RHO ::` (the bulk number density)
beside it — without that keyword the program stops with "Low dimension RMC requested. But
no 'BULK_RHO' keyword found", which the checker now reports before the run (finding P-18).
Measure the envelope the same way as the damping, then let the right radius win.
"""),

code(r"""
def sphere_envelope(r, D):
    x = np.clip(r / D, 0, 1)
    return 1 - 1.5 * x + 0.5 * x ** 3

D = 20.0
env = sphere_envelope(r, D)
G_nano = env * (G_truth - G0) + G0
check("the envelope is 1 at r = 0 and 0 at r = D", sphere_envelope(np.array([0.0]), D)[0] == 1.0 and sphere_envelope(np.array([D]), D)[0] == 0.0)
check("at r = D/2 the envelope is 5/16", abs(sphere_envelope(np.array([D / 2]), D)[0] - 5 / 16) < 1e-12)
if not skip_without_package("the nano-size comparison"):
    nano_keys = [("PARTICLE_RADIUS", f"{D / 2:.1f}"), ("BULK_RHO", f"{cfg.density:.6f}")]
    chi_n_none, x, calc_n_none, expt_n = evaluate("nano_none", G_nano)
    chi_n_right, _, calc_n_right, _ = evaluate("nano_right", G_nano, scalars=nano_keys)
    chi_n_wrong, _, calc_n_wrong, _ = evaluate("nano_wrong", G_nano, scalars=[("PARTICLE_RADIUS", "5.0"), ("BULK_RHO", f"{cfg.density:.6f}")])
    peaks = np.abs(calc_n_none - G0) > 0.5             # where G - G0 is large enough to divide
    ratio_n = (calc_n_right[peaks] - G0) / (calc_n_none[peaks] - G0)
    dev_n = np.max(np.abs(ratio_n - sphere_envelope(x[peaks], D)))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].plot(r, env, label=f"sphere envelope, D = {D:.0f} Å")
    axes[0].plot(x[peaks], ratio_n, "k.", ms=4, label="(calc_nano − G₀)/(calc_bulk − G₀), RMCProfile")
    axes[0].set_xlabel("r (Å)"); axes[0].legend()
    axes[1].plot(x, expt_n, "k", lw=0.8, label="nano 'data'")
    axes[1].plot(x, calc_n_none, lw=0.8, alpha=0.7, label="bulk model")
    axes[1].plot(x, calc_n_right, lw=0.8, label="PARTICLE_RADIUS 10 Å")
    axes[1].set_xlim(2, 8); axes[1].set_xlabel("r (Å)"); axes[1].set_ylabel("G(r) (barn)"); axes[1].legend()
    show(fig)
    caption("Left: the spherical shape function for a 20 Å particle and the envelope RMCProfile "
            "actually applies (measured at the peaks as the ratio of the calculated columns with "
            "and without PARTICLE_RADIUS, baseline removed). Right: the synthetic nanoparticle "
            "G(r) against the bulk model and the corrected one.")
    check("RMCProfile's envelope is the spherical shape function to 5 %", dev_n < 0.05, f"max deviation {dev_n:.3f}")
    check("the right radius gives the lowest chi2 of the three", chi_n_right < chi_n_none and chi_n_right < chi_n_wrong,
          f"none {chi_n_none:.4g}, right {chi_n_right:.4g}, wrong {chi_n_wrong:.4g}")
"""),

md(r"""
### Exercises for chapter 7

**7.1** Scan `RESOLUTION_CORRECTION` over 0.02, 0.05, 0.10 against the data of §29 and
plot χ² against α. Where is the minimum, and how sharp is it?

**7.2** Apply both damping (α = 0.05) and broadening (β = 0.02) to the synthetic data and
show that the two corrections together beat either alone.
"""),

code(r"""
if not skip_without_package("the exercises"):
    # 7.1
    alphas = [0.02, 0.05, 0.10]
    chis = [evaluate(f"scan_{a}", G_damped, [("RESOLUTION_CORRECTION", f"{a:.2f}")])[0] for a in alphas]
    print(dict(zip(alphas, np.round(chis, 4))))
    check("7.1 the chi2 minimum of the scan is at the true alpha = 0.05", alphas[int(np.argmin(chis))] == 0.05)
    # 7.2
    G_both = broaden(G_truth, r, beta) * np.exp(-0.5 * (alpha * r) ** 2)
    c_a = evaluate("both_alpha", G_both, [("RESOLUTION_CORRECTION", "0.05")])[0]
    c_b = evaluate("both_beta", G_both, [("BROADENING_CORRECTION", "0.02")])[0]
    c_ab = evaluate("both_ab", G_both, [("RESOLUTION_CORRECTION", "0.05"), ("BROADENING_CORRECTION", "0.02")])[0]
    check("7.2 both corrections together beat either alone", c_ab < c_a and c_ab < c_b, f"a {c_a:.4g}, b {c_b:.4g}, both {c_ab:.4g}")
"""),
]
