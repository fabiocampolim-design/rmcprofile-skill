# Changelog

All notable changes to rmcprofile-skill. Format: Keep a Changelog; versions: SemVer.

## [0.1.0] — 2026-09-05

### Added
- Environment (`environment-rmcprofile.yml`, installers with dry-run) and the `RMCPROFILE_HOME` convention.
- `scripts/rmcprofile_tools.py`: readers/writers for `.rmc6f`, `.dat` (v6 keyword blocks), data files (STOG-style and two-line-header), `.bragg`/`.back`/`.inst`/`.hkl`/`.dw`; readers for `_chi2`/`.chi2`, `_SQn.csv`, `_PDFn.csv`, partials CSV, `_bragg.csv`; input-set checker; package locator and runner; configuration analysis (partial g(r), G(r) in barn, F(Q), coordination numbers, bond angles, average cell); CLI with audit log and `--selftest`.
- `scripts/verify_rmcprofile.py` health check.
- `references/formats.md`, `package.md`, `method.md`, `pitfalls.md`; `SKILL.md`; `AGENTS.md`; `docs/USER_MANUAL.md`.
- Test suite: formats round-trip, checker, runner (package-bound tests skip without `RMCPROFILE_HOME`), analysis, CLI, licence/SPDX, held-material guard, vendored conformance checker, docs guard.
