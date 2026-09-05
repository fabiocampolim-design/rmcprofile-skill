---
name: rmcprofile
description: Set up, check, run and analyse RMCProfile 6.7.9 refinements of neutron and X-ray total scattering data (F(Q), S(Q), G(r), D(r)), Bragg profiles, EXAFS and magnetic data — write and validate the .dat/.rmc6f input set, drive the installed binary, parse every output, compute partial PDFs, G(r), F(Q), coordination numbers and bond angles from .rmc6f configurations without the binary. Use this skill whenever the user mentions RMCProfile, reverse Monte Carlo, RMC, big-box modelling, rmc6f files, total scattering or PDF fitting of crystalline disorder — even without naming the program.
license: Apache-2.0
---

# rmcprofile-skill 0.5.3

A Python toolkit around RMCProfile, the Reverse Monte Carlo program for total
scattering (rmcprofile.ornl.gov). It reads and writes every input and output
format of version 6.7.9 (`references/formats.md`), checks an input set for the
mistakes the manual warns about, runs the binary the user installed, and
analyses configurations on its own (`references/method.md`), cross-checks itself
against the installed package (`scripts/upstream_adapter.py`) and carries a small
clean-room RMC engine for teaching (`scripts/rmclite.py`, `references/rmclite.md`). RMCProfile is
closed-source and distributed under its own "non-profit purposes" terms; this
skill never ships or copies it — it finds it through `RMCPROFILE_HOME`
(`references/package.md`). Read `references/pitfalls.md` before touching a run
directory. Run everything from the product root with the `rmcprofile` conda
env and `PYTHONIOENCODING=utf-8`; every flag is listed in `AGENTS.md`.

## 1. Set up and verify

```bash
scripts/install_rmcprofile_windows.ps1        # or scripts/install_rmcprofile.sh; both accept a dry-run
export RMCPROFILE_HOME=/path/to/RMCProfile_package    # the directory holding exe/ and tutorial/
python scripts/verify_rmcprofile.py           # imports, formats, Keen identity, rock-salt shells, package smoke test
```

The package is downloaded by the user from rmcprofile.ornl.gov/download/
(SourceForge) and unpacked; without `RMCPROFILE_HOME` every package-bound
check and test is skipped, not failed. `verify_rmcprofile.py` exits 0 only
when every check passes; its smoke test copies `tutorial/ex_1` to a temp dir
and runs it (a few seconds, χ²/dof 0.4201 on both builds).

## 2. Check an input set before running

```bash
python scripts/rmcprofile_tools.py check STEM --dir RUNDIR
```

Prints one line per finding, `LEVEL code: message`, exit 1 on any `ERROR`.
Codes: `no-dat`, `dat-parse`, `no-configuration`, `rmc6f-parse`,
`atom-order` (ATOMS :: and the configuration disagree), `minimum-distances-count`,
`maximum-moves-count`, `data-file-missing`, `data-file-parse`,
`data-block-no-filename`, `bragg-file-missing`, `bragg-inst-missing`,
`bragg-back-missing`, `bragg-parse`, `poly-file-missing` (the program would
wait forever), `bulk-rho-missing` (`PARTICLE_RADIUS ::` without `BULK_RHO ::`, the
program stops); warnings `end-point-beyond-data`, `filename-case` (Linux/macOS
would not find the file), `no-weight`,
`hkl-range-unspecified`, `stale-neighbour-files`, `history-file` (a `.his6f` from a
zero-move pass poisons the next run); info `potential-lists-regenerated`, `summary`.

## 3. Run RMCProfile and read the result

```bash
python scripts/rmcprofile_tools.py run STEM --dir RUNDIR --timeout 10      # minutes; --home overrides RMCPROFILE_HOME
```

The checker runs first and refuses to start on an error. The run's stdout goes
to `RUNDIR/run.log`; the summary line gives the return code, wall time and
the number of output files; `final:` echoes the last row of `<stem>.chi2`.
In Python: `res = run_rmcprofile(stem, rundir, find_package())` →
`res.returncode`, `res.seconds`, `res.outputs`, `res.final_chi2`. Read the
fit with `read_csv_pair("<stem>_PDF1.csv")` (r, calc, expt),
`read_partials_csv("<stem>_PDFpartials.csv")`, `read_chi2_history("<stem>.chi2")`.
A missing configuration makes RMCProfile stop *with exit code 0* — trust
`outputs` and `final_chi2`, not the code.

## 4. Prepare data files

```python
from rmcprofile_tools import write_data_file, read_data_file
write_data_file("sample_gr.dat", r, G, "sample 300 K", style="two-line")   # or style="stog"
```

`DATA_TYPE`/`FIT_TYPE` are `G(r)`, `D(r)`, `T(r)` in real space and `F(Q)`,
`S(Q)`, `i(Q)` in reciprocal space; the definitions, the r → 0 identity
G(0) = −(Σ c_i b_i)² and the weights are in `references/method.md`. A G(r)
whose low-r plateau is not −(Σ c b)² was not normalised the way RMCProfile
expects.

## 5. Build or edit a .dat

```python
from rmcprofile_tools import read_dat
d = read_dat("sample.dat")
d.set("NEUTRON_REAL_SPACE_DATA", "WEIGHT", "0.02")
d.scalars["TIME_LIMIT"] = "30.00 MINUTES"
d.write("sample.dat")
```

`DatFile` keeps scalars, the `ATOMS ::` line and every block in file order
and writes them back byte-stable; `d.get(block, key)`, `d.data_blocks()`,
`d.filenames()`. The block-versus-scalar rule and every keyword seen in the
package are in `references/formats.md`. Keep `NUMBER_DENSITY` equal to the
configuration's header density.

## 6. Analyse a configuration without the binary

```bash
python scripts/rmcprofile_tools.py pdf    FILE.rmc6f --rmax 8 --dr 0.02 --qmax 30 --dq 0.02 --radiation neutron --outdir out
python scripts/rmcprofile_tools.py coord  FILE.rmc6f --pair Na Cl --rmax 3.0
python scripts/rmcprofile_tools.py angles FILE.rmc6f --triplet Na Cl Cl --rmax 3.0 --dangle 2 --outdir out
```

`pdf` writes `<stem>_PDFpartials.csv` (g_ij), `<stem>_GofR.csv` (Keen's G(r)
in barn) and `<stem>_FofQ.csv`; `coord` prints the coordination histogram;
`angles` writes the B-A-C angle histogram. Sanity check: the first value of
G(r) must be −(Σ c_i b_i)² (−0.2759 barn for SF6). In Python:
`read_rmc6f`, `partial_gr`, `total_gr`, `fq_from_gr`, `coordination`,
`bond_angles`, `average_cell`, `NEUTRON_B`. `--rmax` must stay below half the
shortest supercell edge.

## 7. Pitfalls

`references/pitfalls.md`: the `.poly` wait, exit code 0 on a fatal error,
`.his6f` precedence, stale neighbour files, the CUDA-versus-CPU move rate,
`/mnt/*` slowness under WSL, the two `.rmc6f` atom-line layouts, CRLF, the
r-grid convention, natural-abundance weights, cp1252 consoles.

## 8. Cross-check against the installed package

```bash
python scripts/upstream_adapter.py list                      # the eight shipped exercises and their staging recipes
python scripts/upstream_adapter.py crosscheck ex_1 --timeout 3
```

`crosscheck` stages the exercise's pristine inputs in a scratch directory
(outputs removed, `.poly`/`.fs`/`.sf` kept, `ex_7`'s `TIME_LIMIT` cut to 5 min),
runs the package, then compares our partials and Keen G(r) for the resulting
`.rmc6f` with the package's own `_PDFpartials.csv` and `_PDF1.csv`. "within
tolerance: True" means every pair is within `tolerance_partials` (1e-3; the
package computes in single precision, measured 2.8e-4 on the g = 20 peak) and
G(r) within `tolerance_gofr` (1e-4 barn, measured 3e-5) of
`tests/records/crosscheck_v1.json`. `--update-records` rewrites the measured
maxima and provenance — only after a deliberate re-measurement. In Python:
`crosscheck_partials(rmc6f, partials_csv)`, `crosscheck_gofr(rmc6f, pdf_csv)`,
`stage_exercise`, `run_and_crosscheck`.

## 9. Teach with rmclite

```bash
python scripts/rmclite.py synth truth.rmc6f --displace 0.05 --rmax 5 --outdir out     # targets of truth + a displaced copy
python scripts/rmclite.py fit   average.rmc6f --target out/truth_target_PDFpartials.csv --moves 3000 --sigma 0.2 --min-dist "Na-Na:3.0,Na-Cl:2.2,Cl-Cl:3.0" --outdir out
```

`fit` writes `<stem>_fit.rmc6f`, `<stem>_fit.chi2` (RMCProfile's header
`m_accepted m_generated m_tested chi2`), `<stem>_fit_PDFpartials.csv` and
`<stem>_fit_GofR.csv` — read them with the same readers as RMCProfile's
output. The acceptance rule is Δ = Δχ²/2 + ΔU/k_BT, accept if Δ ≤ 0 else
with probability e^(−Δ). Start from the average structure, never from a
random distortion; never fit unbroadened (delta-sharp) targets; expect the
pair distribution to be reproduced, not the coordinates
(`references/rmclite.md` §5). In Python: `Box.from_rmc6f`, `Histogram`,
`PartialTarget`, `TotalGTarget`, `FqTarget`, `ClosestApproach`,
`DistanceWindow`, `BondPotential`, `RmcLite(...).run(n)`, `synth_targets`.

## 10. Read or rebuild the book

`chapters/RMCProfile_NN_*.ipynb` — eleven executed notebooks (§1–40, index in
`chapters/README.md`): 1 total scattering and the PDF, 2 the RMC algorithm,
3 starting configurations, 4 fitting neutron data with RMCProfile, 5 X-ray
and Bragg, 6 constraints and potentials, 7 corrections (the measured forms of
`RESOLUTION_CORRECTION` and `PARTICLE_RADIUS`), 8 EXAFS / magnetic / diffuse,
9 analysing configurations, 10 benchmarks and ecosystem. Point a user at the
chapter, not at a paraphrase: every number in them was computed in the
notebook. To rebuild after editing `build/part*.py`:

```bash
python build/assemble.py --which 07          # regenerate one chapter (unchanged notebooks are kept with their outputs)
RMCPROFILE_HOME=... python build/execute.py --which 07   # execute it on the rmcprofile-mc kernel; PASS/FAIL tally in logs/execute.log
python build/gallery.py                      # docs/figures + README gallery
python -m pytest tests/test_notebooks.py -q  # sources, outputs, totals, leaks
```

## 11. Teach the course

`course/deck/index.html` — eleven lectures (L0 why local structure … L10
contributing), flat and linear, every chapter figure under its notebook
caption; `course/slides.pdf` is the same deck without a browser;
`course/handout/handout.html` the A4 companion; `course/notes/LECTURER_NOTES.md`
every slide's notes with its anticipated question. Point a lecturer at
`course/README.md` (syllabus, keys, rebuilding). After re-executing a chapter:

```bash
python course/tools/extract_figures.py      # figures + provenance (--check to test)
python course/tools/build_deck.py           # index.html, handout, notes (--check to test)
python course/tools/make_slides_pdf.py      # slides.pdf (Playwright; committed)
python -m pytest tests/test_course.py -q
```

## 12. Watch upstream weekly

```bash
python scripts/watch_upstream.py --weekly          # SourceForge listing, site pages/posts, conda tools, GitHub neighbours, tracker status
python scripts/watch_upstream.py --snapshot        # record the state without a report
powershell -File scripts/register_watch_task.ps1   # Windows Task Scheduler, Mondays 08:00 (-DryRun, -Remove)
```

Reports go to `<study>/docs/watch/YYYY-WW.md`, the snapshot and audit logs to
`<study>/forum/upstream-watch/` (gitignored). A feed that does not answer is a
row in the report and exit 1; read the report before trusting a silent week.
The first run (2026-W36) found a 6.8.0-rc.1 candidate on SourceForge that the
site's download page did not list.
