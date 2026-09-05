# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
from nbbuild import md, code

CELLS = [

md(r"""
## 32. Beyond the pair distribution

Three data types in RMCProfile are not pair distribution functions and this book's engine
does not compute them. This chapter is documentary where it must be and live where the
package allows: EXAFS runs here on the shipped SnO exercise; magnetic scattering and
three-dimensional diffuse scattering are described from the manual with their keyword
blocks, so that a reader who has such data knows what the program expects.

**EXAFS** (manual §4.7, `EXAFS ::` block; Krayzman et al. 2009). The extended X-ray
absorption fine structure $\chi(k)$ of one absorbing element is a sum over its scattering
paths; RMCProfile computes it from the configuration with FEFF-style amplitudes and phases
supplied in the exercise's `.1sc1`/`.2sc3`… files and fits it in $k$ or in $r$ space.
Keywords: `FILENAME`, `TYPE(S)_OF_ABSORBING_ATOMS`, `START_POINT_(k_space)`,
`END_POINT_(k_space)`, `FIT_space`, `START_POINT_(r_space)`, `END_POINT_(r_space)`,
`R_SPACING`, `K_POWER`, `ENERGY_OFFSET`, `WEIGHT` — one block per edge. The absorber and
scatterer lists (`absorlist.dat`, `scattlist.dat`) and the path amplitudes come from the
`Prep/` step of the exercise, not from RMCProfile.
"""),

code(r"""
if not skip_without_package("the EXAFS run"):
    work = os.path.join(WORK, "exafs_ex_7")
    ua.stage_exercise(PKG, "ex_7", work)
    stem = ua.EXERCISES["ex_7"].stem
    d = rt.read_dat(os.path.join(work, stem + ".dat"))
    exafs = [b for b in d.blocks if b.name == "EXAFS"]
    print(f"{len(exafs)} EXAFS blocks; absorbers:", [b.get("TYPE(S)_OF_ABSORBING_ATOMS") for b in exafs],
          "| fit spaces:", [b.get("FIT_space") or b.get("Fit_space") for b in exafs])
    d.scalars["TIME_LIMIT"] = "0.0 MINUTES"
    d.scalars["SAVE_PERIOD"] = "0.0 MINUTES"
    d.write(os.path.join(work, stem + ".dat"))
    t0 = time.time()
    res = rt.run_rmcprofile(stem, work, PKG, timeout_min=6)
    print(f"rc {res.returncode}, {time.time() - t0:.0f} s | chi2 rows: {res.final_chi2}")
    outs = sorted(o for o in res.outputs if "EXAFS" in o and o.endswith(".csv"))
    print("EXAFS outputs:", outs)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, name in zip(axes, [o for o in outs if "_R_" in o]):
        x, calc, expt = rt.read_csv_pair(os.path.join(work, name))
        ax.plot(x, expt, "k", lw=0.8, label="data")
        ax.plot(x, calc, "C3", lw=0.8, label="RMCProfile, shipped box")
        ax.set_title(name.split("-")[0] + " edge, r space"); ax.set_xlabel("r (Å)"); ax.legend()
    show(fig)
    caption("The two EXAFS edges of the package's SnO exercise (Nb and Sr absorbers) in r space: "
            "the data and RMCProfile's calculation for the shipped starting configuration, "
            "evaluated with no moves.")
    check("RMCProfile evaluated both EXAFS edges (EXAFS_1 and EXAFS_2 chi2 rows)", res.returncode == 0 and {"EXAFS_1", "EXAFS_2"} <= set(res.final_chi2))
    check("it wrote a k-space and an r-space CSV per edge", len(outs) == 4)
"""),

md(r"""
## 33. Magnetic scattering

Magnetic neutron scattering adds to the nuclear pair distribution a spin–spin term with a
magnetic form factor, and RMCProfile refines spin orientations together with positions
(manual §4.8; Paddison & Goodwin 2012 for the spin-RMC idea). The `MAGNETISM ::` block
carries `FORM_FACTOR` (the ion's magnetic form factor coefficients), `MAGNETISM_FILE_STEM`,
`MAGNETIC_ATOMS` (which types carry a moment), `MAX_SPIN_MOVEMENT` and `SPIN_MOVE_RATE`
(how far and how often a spin rotates instead of an atom moving); the spins live in a
companion file to the `.rmc6f`. The package ships no magnetic exercise, so this section has
no run — a reader with a magnetic data set has the block above and the checker, which
accepts the keywords as scalars of the block without judging their values.
"""),

md(r"""
## 34. Three-dimensional diffuse scattering

Single-crystal diffuse scattering fits (manual §4.9, `DIFFUSE_SCATTERING3D ::`; Welberry &
Weber 2016 review the method) compare a calculated reciprocal-space volume with a measured
one; the configuration must be a `SUPERCELL_DIMENSIONS`-declared supercell so that the
average amplitude can be computed (that keyword's manual entry says so). The `.hkl`-style
reflection list of the Bragg block is not used — the data are a volume — and the fit is
costly per move. As for magnetism, the package ships no exercise and this book runs none.

Where this leaves the book: every real-space and reciprocal-space pair-distribution data
type is reproduced (chapters 1–4, 7), the X-ray route is reproduced in scale and partly in
shape (chapter 5), Bragg profiles and EXAFS are run on the shipped exercises with the
program's own files (chapters 5, 8), and magnetic and diffuse-scattering fits are described
from the manual only. Chapter 9 turns to what one does with a refined box.
"""),

code(r"""
# the keyword inventory of this chapter, as the checker sees it: block names RMCProfile knows
known = ["EXAFS", "MAGNETISM", "DIFFUSE_SCATTERING3D", "BRAGG", "NEUTRON_REAL_SPACE_DATA",
         "NEUTRON_RECIPROCAL_SPACE_DATA", "XRAY_REAL_SPACE_DATA", "XRAY_RECIPROCAL_SPACE_DATA"]
print("data-block names this book covers:", ", ".join(known))
check("chapter 8 lists the three data types it cannot reproduce with rmclite", {"EXAFS", "MAGNETISM", "DIFFUSE_SCATTERING3D"} <= set(known))
"""),

md(r"""
### Exercises for chapter 8

**8.1** In the SnO exercise's `.dat` file, which `K_POWER` weights the EXAFS data, and what
does a higher power do to the fit's sensitivity at large $k$?

**8.2** The EXAFS run above made no move. Set `TIME_LIMIT` to one minute and compare the
`EXAFS_1` χ² before and after (the shipped configuration is already refined, so expect a
small change).
"""),

code(r"""
if not skip_without_package("the exercises"):
    # 8.1 — read it off the staged file rather than quoting it
    kp = [b.get("K_POWER") for b in exafs]
    print("K_POWER per edge:", kp, "— chi(k) is multiplied by k^n, so a higher n amplifies the weak high-k oscillations")
    check("8.1 both EXAFS blocks declare a K_POWER", all(v is not None for v in kp))
    # 8.2 — a one-minute refinement of the shipped box
    work2 = os.path.join(WORK, "exafs_1min")
    ua.stage_exercise(PKG, "ex_7", work2)
    d2 = rt.read_dat(os.path.join(work2, stem + ".dat"))
    d2.scalars["TIME_LIMIT"] = "1.0 MINUTES"
    d2.scalars["SAVE_PERIOD"] = "1.0 MINUTES"
    d2.write(os.path.join(work2, stem + ".dat"))
    res2 = rt.run_rmcprofile(stem, work2, PKG, timeout_min=6)
    print(f"EXAFS_1 chi2: no moves {res.final_chi2['EXAFS_1']:.4g} -> one minute {res2.final_chi2['EXAFS_1']:.4g} ({res2.final_chi2['m_generated']} moves)")
    check("8.2 a minute of moves does not worsen the EXAFS_1 chi2 of the refined box", res2.final_chi2["EXAFS_1"] <= res.final_chi2["EXAFS_1"] * 1.05)
"""),
]
