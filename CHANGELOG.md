# Changelog

All notable changes to rmcprofile-skill. Format: Keep a Changelog; versions: SemVer.

## [0.5.5] — 2026-09-06

### Changed
- `partial_gr` histograms row blocks of the minimum-image distances instead of building the full N × N × 3 array (4.4 GB on the 14 000-atom SF6 exercise); the counts are identical (`tests/test_analysis.py`).
- `upstream_adapter crosscheck`: an exercise without a record now says so and exits 3 (it read "within tolerance: False" — every exercise but ex_1 did on the 6.8.0-rc.1 audit); G(r) is compared only when the run produced a PDF column (X-ray-only exercises have none); a configuration the reader refuses is reported as an error row, not a traceback; `--update-records` accepts partials-only results; the PDF column is compared in the function the exercise fits (`FIT_TYPE`: G(r), D(r) = 4πrρG or T(r)) and on the CSV's own r points (the SnO exercise fits D(r) from r = 1.40 Å: 4e-5 in D(r), 3.6 barn read as G(r)).
- `tests/records/crosscheck_v1.json` now holds ex_1, ex_3, ex_4_5K, ex_6_xray and ex_7, measured on 6.7.9 (Windows build).

### Found (study repository, `docs/02`)
- 6.8.0-rc.1: PDF outputs equal 6.7.9's to the last digit on every exercise that ran; the new Bragg pipeline allocates 1.6 MB per reflection and stops on the GaPO4 X-ray and SrTiO3 exercises when the memory is not there (P-23); the shipped GaPO4 neutron start file is one atom short (P-22).

## [0.5.4] — 2026-09-05

### Changed
- README gallery: one block per chapter — link, full-width figure, caption below — instead of a three-column table that shrank every figure to a third of the page (Fabio's review).

### Fixed
- `watch_upstream.py`: two runs of one process within one Windows clock tick wrote the same audit-log name; the name now takes a suffix when it exists.

## [0.5.3] — 2026-09-05

### Fixed
- `build/gallery.py` read a `text/markdown` output the notebooks' `caption()` helper never emits, so every README gallery row had an empty caption column; it now parses the `text/html` caption (the same output `extract_figures.py` reads) and the gallery carries the nine captions. Found by the post-release `/code-review`; a test in `tests/test_notebooks.py` guards it.

## [0.5.2] — 2026-09-05

### Changed
- Chapter 9 §36 (book figure 22, course figure `s36-f1`): the coordination-number figure is now the running coordination number n(r) of Na against the cutoff radius for the fitted box and the truth (plateaus at 6 and 14), beside the r²-weighted Na–Cl bond-length distribution with mean and width — a single-bar histogram was a number, not a figure (Fabio's review).
- README: "Honest comparison with neighbours" and "How it was built" with the CRediT table; the docs guard asserts both sections.

## [0.5.1] — 2026-09-05

### Changed
- Chapters 5 (§22) and 8 (§32), and the two course figures built from them, now plot only RMCProfile's *calculated* Bragg profile and EXAFS χ(r) for the shipped exercises, with the correlation to the exercise's measured curve printed in the legend; the measured curves themselves belong to the package and are no longer drawn. First public release.

## [0.5.0] — 2026-09-05

### Added
- `scripts/watch_upstream.py` (playbook rule 23): the weekly upstream watch over the public surfaces — SourceForge file listing (RSS), every page and post of rmcprofile.ornl.gov (WordPress REST API, modification dates), the three GPL tools on the conda channel `apw247`, seven neighbouring GitHub projects, and the HTTP status of the issue tracker; `--weekly` writes `<study>/docs/watch/YYYY-WW.md` (a re-run in the same week appends), `--snapshot`, per-feed failure rows with exit 1, an audit log per run. `scripts/register_watch_task.ps1` registers the Windows Task Scheduler job (Mondays 08:00, console to a log). `tests/test_watch_upstream.py` fakes the three network seams.
- Study documents (not in the product): `docs/01` website survey, `docs/05` GPL tools audit with the `rmc_tools` parser comparison (agrees on all shipped configurations; P-19 crash on boxes under 100 atoms), `docs/06` literature run, `docs/07` ecosystem; drafts B-1, B-4, B-5.

## [0.4.0] — 2026-09-05

### Added
- The course (playbook rule 22): `course/` — eleven lectures L0–L10 (56 slides, 10 dividers) as a flat reveal.js deck (`deck/index.html`, vendored reveal.js 5.2.0 MIT), an A4 handout, lecturer notes with an anticipated question per slide, and the committed PDF fallback `course/slides.pdf` (66 pages). Every one of the 24 chapter figures appears under its full notebook caption with section and cell; `course/deck/content.en.js` is the single source. Tools: `extract_figures.py` (figures + `provenance.json` with SHA-256, `--check`), `build_deck.py` (`--check`), `make_slides_pdf.py`, `verify_deck.py`, `make_handout.py`, `build_pptx.py` (the last four need Playwright, `course/tools/requirements.txt`). `tests/test_course.py` guards content, provenance, generated outputs, the PDF page count, the licence and leaks.

## [0.3.0] — 2026-09-05

### Added
- The book: eleven executed chapter notebooks in `chapters/` (§1–40, one per data type RMCProfile fits, exercises with worked solutions), generated from `build/part*.py` by `build/assemble.py`, executed by `build/execute.py` on the `rmcprofile-mc` kernel with a PASS/FAIL tally; `build/gallery.py` writes `docs/figures/` and the README gallery; `tests/test_notebooks.py` guards sources, outputs, totals and leaks.
- Toolkit: `lattice_from_cell`, `build_configuration`, `fold_to_unit_cell`, `export_xyz`, `export_cif`, `faber_ziman_sq`, `xray_form_factor` / `xray_weights` / `total_fq_from_partials(..., radiation)` (needs `periodictable`), `xray_coefficients_rmcprofile`, `cromer_mann_4term`, `write_xray_file`, `write_input_set` (a complete synthetic input set; `IGNORE_HISTORY_FILE ::` by default), `bond_valence_sum`; `.dat` writer keeps the three keyword forms (`> KEY :: v`, `> KEY ::`, `> KEY`).
- Checker: `bulk-rho-missing` (`PARTICLE_RADIUS ::` without `BULK_RHO ::` stops the program), `history-file` warning (a zero-move `.his6f` poisons the next run).
- Measured, not assumed (chapter 7): `RESOLUTION_CORRECTION` applies exp(−(r·Expo)²/2), not the manual's exp(−r·Expo); `PARTICLE_RADIUS` replaces the bulk baseline −G₀ by −G₀·f(r) (spherical shape function, D = 2R) beyond the closest approach. Recorded as findings P-17 and P-18 in the study repository.

### Changed
- `write_input_set` defaults: save period = time limit, print period 1000.

## [0.2.0] — 2026-09-05

### Added
- `scripts/upstream_adapter.py`: stage any of the eight shipped exercises, run the package, compare our partials and Keen G(r) with its `_PDFpartials.csv` / `_PDF1.csv`; `list`, `crosscheck`, `--selftest`, `--update-records`; schema-1 records in `tests/records/crosscheck_v1.json` (tolerances 1e-3 / 1e-4, measured 2.8e-4 / 3e-5 on both builds).
- `scripts/rmclite.py`: clean-room RMC engine — `Box`, incremental `Histogram` on RMCProfile's grid, `PartialTarget` / `TotalGTarget` / `FqTarget`, `ClosestApproach`, `DistanceWindow`, `BondPotential`, `RmcLite` with Metropolis acceptance and seeds, `synth` / `fit` CLI writing RMCProfile-layout files; `references/rmclite.md`.
- `rmc_grid` and `partial_gr(..., grid="rmcprofile"|"centre")`; `pdf --grid`.
- `verify_rmcprofile.py` checks 5 (rmclite recovery) and 7 (package cross-check); SKILL.md workflows 8–9.

### Changed
- `partial_gr` now defaults to RMCProfile's grid: r values are k·dr (0.02, 0.04, …) instead of bin centres, and `pdf` CSVs start at r = dr.

## [0.1.0] — 2026-09-05

### Added
- Environment (`environment-rmcprofile.yml`, installers with dry-run) and the `RMCPROFILE_HOME` convention.
- `scripts/rmcprofile_tools.py`: readers/writers for `.rmc6f`, `.dat` (v6 keyword blocks), data files (STOG-style and two-line-header), `.bragg`/`.back`/`.inst`/`.hkl`/`.dw`; readers for `_chi2`/`.chi2`, `_SQn.csv`, `_PDFn.csv`, partials CSV, `_bragg.csv`; input-set checker; package locator and runner; configuration analysis (partial g(r), G(r) in barn, F(Q), coordination numbers, bond angles, average cell); CLI with audit log and `--selftest`.
- `scripts/verify_rmcprofile.py` health check.
- `references/formats.md`, `package.md`, `method.md`, `pitfalls.md`; `SKILL.md`; `AGENTS.md`; `docs/USER_MANUAL.md`.
- Test suite: formats round-trip, checker, runner (package-bound tests skip without `RMCPROFILE_HOME`), analysis, CLI, licence/SPDX, held-material guard, vendored conformance checker, docs guard.
