# Changelog

All notable changes to rmcprofile-skill. Format: Keep a Changelog; versions: SemVer.

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
