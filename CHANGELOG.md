# Changelog

All notable changes to rmcprofile-skill. Format: Keep a Changelog; versions: SemVer.

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
