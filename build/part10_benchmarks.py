# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
from nbbuild import md, code

CELLS = [

md(r"""
## 39. The cross-check, live, and what the numbers cost

Everything this book computes on its own — partials on RMCProfile's grid, Keen's $G(r)$ with
the neutron weights — is compared with the package's own output by `upstream_adapter`:
it stages a shipped exercise in a scratch directory, runs the program, and measures the
largest difference between our functions and the program's `_PDFpartials.csv` and
`_PDF1.csv` for the same box. The tolerances live in `tests/records/crosscheck_v1.json`
with the values measured on both builds (2.8e-4 on a partial that peaks near 20 — the
package works in single precision; 3e-5 barn on $G(r)$). Here it runs in the reader's
installation.

Cost: `rmclite` makes about 1 900 moves per second on 64 atoms with three partial targets
(one distance row per move, pure numpy). RMCProfile on the synthetic NaCl set of chapter 4
made 25 000 moves in 30 s *with* an $F(Q)$ data set, and about 20 000 moves per second
with $G(r)$ only — the Fourier transform per move is what a reciprocal-space data set
costs. The study repository's package audit records the shipped exercises' timings on both
builds.
"""),

code(r"""
if not skip_without_package("the live cross-check"):
    work = os.path.join(WORK, "crosscheck_ex_1")
    ua.stage_exercise(PKG, "ex_1", work)
    res = ua.run_and_crosscheck(PKG, "ex_1", work, timeout_min=3)
    rec = ua.load_records()
    tol = rec["exercises"]["ex_1"]
    print(f"rc={res['returncode']}, {res['seconds']:.0f} s, chi2 {res['final_chi2']['chi2']}")
    for lab, v in res["partials"].items():
        print(f"  partial {lab:6s} max|diff| = {v:.2e}   (tolerance {tol['tolerance_partials']:.0e})")
    print(f"  G(r)          max|diff| = {res['gofr']:.2e}   (tolerance {tol['tolerance_gofr']:.0e} barn)")
    check("the package's smoke test reproduces its chi2/dof 0.4201", abs(res["final_chi2"]["chi2"] - 0.4201) < 1e-4)
    check("our partials equal RMCProfile's within the recorded tolerance", ua.within_tolerance(res, rec))
    check("the record carries provenance for the tolerances", "provenance" in tol and "single precision" in tol["provenance"])

# rmclite throughput, measured now
box = rl.Box.from_rmc6f(rt.build_configuration((5.64,) * 3 + (90,) * 3,
                        [("Na", 0, 0, 0), ("Na", .5, .5, 0), ("Na", .5, 0, .5), ("Na", 0, .5, .5),
                         ("Cl", .5, 0, 0), ("Cl", 0, .5, 0), ("Cl", 0, 0, .5), ("Cl", .5, .5, .5)], (2, 2, 2)))
r, parts, _ = rl.synth_targets(box, 5.0, 0.02, 0.0, np.random.default_rng(0))
eng = rl.RmcLite(box, 5.0, 0.02, [rl.PartialTarget(lab, r, parts[lab], 0.2) for lab in parts], max_move={"Na": 0.05, "Cl": 0.05}, seed=0)
t0 = time.time()
eng.run(2000)
rate = 2000 / (time.time() - t0)
print(f"rmclite: {rate:.0f} moves/s on 64 atoms with three partial targets")
check("rmclite runs at hundreds of moves per second or more", rate > 300, f"{rate:.0f} moves/s")
"""),

md(r"""
## 40. The ecosystem, and how to contribute

RMCProfile's own site lists the neighbours it considers relevant; one honest line each, from
what their pages say, with no ranking:

| Tool | What it is | Relation to RMCProfile |
|---|---|---|
| RMC++ (Budapest) | the general reverse Monte Carlo code descended from RMCA, for liquids and glasses | the common ancestor; RMCProfile added crystals, Bragg profiles and the constraint families |
| HRMC (CSIRO) | hybrid RMC with interatomic potentials | the potential idea RMCProfile's `POTENTIALS ::` block adopts for specific bonds |
| fullrmc (Bachir Aoun) | a Python RMC engine with a modular constraint system | a scriptable alternative; no Bragg-profile fitting |
| EPSR / Dissolve (ISIS) | empirical potential structure refinement for liquids and glasses | data-driven potentials rather than direct moves |
| DISCUS (Neder, Proffen) | diffuse-scattering simulation and refinement of disordered crystals | the `rmc_to_discus` export; a different route to the same disorder |
| PDFgui / diffpy-CMI (Columbia, BNL) | small-box PDF refinement and its scriptable successor | the average-structure-plus-parameters description that RMC's big box complements |
| GudrunN/X, PDFgetX3, Mantid, ADDIE | data reduction from raw scattering to $F(Q)$ and $G(r)$ | what produces the files chapter 4 synthesised |
| Topas4RMC, sofq_calib, rmc_tools (conda, GPL) | RMCProfile's own Python side tools | the surface where this project's patches can go |

Contributing to RMCProfile itself goes through its mailing list; the program is closed-source,
so contributions are reports, reproductions and documentation. The study behind this book
keeps a findings ledger with the evidence for each item — a run log, a file and line — and
sends nothing without its owner's review.
"""),

code(r"""
# the ledger's discipline, in code: a finding is only PROVEN with a reproduction. Here is one
# from chapter 4 reproduced in the reader's own installation: the package stops with exit
# code 0 when an input file is missing.
if not skip_without_package("the exit-code reproduction"):
    NACL = [("Na", 0, 0, 0), ("Na", .5, .5, 0), ("Na", .5, 0, .5), ("Na", 0, .5, .5),
            ("Cl", .5, 0, 0), ("Cl", 0, .5, 0), ("Cl", 0, 0, .5), ("Cl", .5, .5, .5)]
    cfg = rt.build_configuration((5.64,) * 3 + (90,) * 3, NACL, (2, 2, 2))
    r2, parts2, G2 = rl.synth_targets(rl.Box.from_rmc6f(cfg), 5.0, 0.02, 0.0, np.random.default_rng(1))
    work = os.path.join(WORK, "exit0")
    rt.write_input_set("m", work, cfg, gr=(r2, G2), min_dist={"Na-Na": 3.0, "Na-Cl": 2.2, "Cl-Cl": 3.0}, max_move=0.05, time_limit_min=0.0)
    os.remove(os.path.join(work, "m.rmc6f"))                      # the fatal condition
    findings = rt.check_input_set("m", work)
    print("checker:", [f.code for f in findings if f.level == "ERROR"])
    res = rt.run_rmcprofile("m", work, PKG, timeout_min=2)
    with open(res.log_path, encoding="utf-8", errors="replace") as f:
        tail = f.read()[-300:]
    print("RMCProfile said:", tail.strip().splitlines()[-1])
    print("exit code:", res.returncode, "| outputs:", res.outputs)
    check("the checker refuses the set (no-configuration) before the program is even started", "no-configuration" in [f.code for f in findings])
    check("RMCProfile stops on the missing file but returns exit code 0 (finding P-11)", res.returncode == 0 and "does not exist" in tail)
    check("the run produced no fit output", not any(o.endswith("_PDF1.csv") for o in res.outputs))
"""),
]
