# AGENTS.md — rmcprofile-skill, the contract for agents

Everything runs from the product root (`rmcprofile-skill/`) with the
`rmcprofile` conda env and `PYTHONIOENCODING=utf-8`. RMCProfile itself is
never in this tree: set `RMCPROFILE_HOME` to the user's `RMCProfile_package`
directory (the one with `exe/` and `tutorial/`); without it every
package-bound test and check is skipped.

## Commands and every flag

`python scripts/rmcprofile_tools.py` — the toolkit.

| Scope | Flags |
|---|---|
| global (before or after a subcommand) | `--version`, `--selftest` (round-trip every format on synthetic files, exit 0/1), `--outdir` (default `out`), `--log-dir` (default `logs`), `-q` / `--quiet` |
| `check` STEM | `--dir` (directory holding the input set, default `.`) |
| `run` STEM | `--dir`, `--home` (RMCProfile_package directory, default `$RMCPROFILE_HOME`), `--timeout` (minutes; the process is killed and `rc=None` reported) |
| `pdf` FILE.rmc6f | `--rmax` (default 20.0; must be below half the shortest cell edge), `--dr` (0.02), `--qmax` (30.0), `--dq` (0.02), `--radiation {neutron,xray}` (`xray` raises until the X-ray chapter), `--grid {rmcprofile,centre}` (r grid: RMCProfile's k*dr, default, or bin centres) |
| `coord` FILE.rmc6f | `--pair A B` (required), `--rmax` (required) |
| `angles` FILE.rmc6f | `--triplet A B C` (required: apex A, arms B and C), `--rmax` (required), `--dangle` (2.0 degrees) |

Exit codes: 0 ok, 1 findings/failed run, 2 no package for `run` or bad usage.
Every invocation writes `logs/rmcprofile_tools_<stamp>.json` (rule 12 audit
log: version, argv, ok, checks, extras).

`python scripts/verify_rmcprofile.py` — health check: `-q` / `--quiet`,
`--home` (package directory), `--minutes` (smoke-test cap, 3.0), `--version`.
Seven checks (imports, formats, Keen identity, rock-salt shells, rmclite
recovery, package smoke test, package cross-check); exit 0 only when every
check passes; the two package checks are `[SKIP]` without a package.

`python scripts/upstream_adapter.py` — cross-check against the installed package.

| Scope | Flags |
|---|---|
| global | `--version`, `--selftest` (cross-check our own `pdf` output against itself, exact), `--outdir`, `--log-dir`, `-q` / `--quiet` |
| `list` | none — prints the eight exercises with their staging recipes |
| `crosscheck` EXERCISE (`ex_1` … `ex_7`) | `--home` (package directory), `--workdir` (scratch dir, default a fresh temp dir), `--timeout` (minutes), `--update-records` (rewrite the measured maxima and provenance in `tests/records/crosscheck_v1.json`) |

Exit 0 within tolerance, 1 outside, 2 without a package. Audit log
`logs/upstream_adapter_<stamp>.json`. The records file (`schema` 1) holds
per exercise `tolerance_partials`, `tolerance_gofr`, `measured`, `provenance`
and an `rmclite` block; it stores our numbers, never the package's data.

`python scripts/rmclite.py` — the teaching engine.

| Scope | Flags |
|---|---|
| common (global and per subcommand) | `--outdir`, `--log-dir`, `-q` / `--quiet`, `--rmax` (8.0), `--dr` (0.02), `--seed` (0) |
| global | `--version`, `--selftest` (2×2×2 rock salt, 2000 moves, χ² must fall by 80 %) |
| `synth` FILE.rmc6f | `--displace` (0.15 Å Gaussian displacement of every atom), `--noise` (s.d. added to each target partial) |
| `fit` FILE.rmc6f | `--target` (required, `_PDFpartials.csv` layout), `--gofr` (optional G(r) CSV), `--moves` (5000), `--sigma` (0.2), `--min-dist` (`"A-A:3.0,A-B:2.2"`), `--max-move` (0.05 Å), `--print-every` (0) |

`synth` writes `<stem>_displaced.rmc6f`, `<stem>_target_PDFpartials.csv`,
`<stem>_target_GofR.csv`; `fit` writes `<stem>_fit.rmc6f`, `<stem>_fit.chi2`,
`<stem>_fit_PDFpartials.csv`, `<stem>_fit_GofR.csv`; audit log
`logs/rmclite_<stamp>.json`. The `fit` histogram grid is taken from the target
file (`--rmax`/`--dr` apply to `synth`).

`python docs/build_manual.py` — `docs/USER_MANUAL.md` → HTML (+ PDF with
pandoc): `--outdir`, `--no-pdf`, `-v` / `--verbose`.

The book (`chapters/`): `python build/assemble.py` generates the notebooks from
`build/part*.py` — `--which KEY[,KEY]|all` (a notebook whose sources are unchanged
is kept, outputs included), `--outdir`,
`--log-dir`, `--list` (cells and figures per chapter, no write), `--force` (rewrite a
notebook whose sources are unchanged — by default such a notebook is kept with
its outputs), `-v` / `--verbose`, `-q` / `--quiet`. `python build/execute.py` runs them with
nbconvert — `--which`, `--indir`, `--outdir`, `--log-dir`, `--kernel`
(default `rmcprofile-mc`), `--timeout` (per cell, s), `--tally-only` (count
PASS/FAIL without executing), `-v`, `-q`; the tally goes to
`logs/execute.log`. `python build/gallery.py` writes `docs/figures/*.png` and
the README gallery block — `--check` (exit 1 if the block is stale).

`python scripts/watch_upstream.py` (rule 23, weekly upstream watch) — `--weekly`,
`--snapshot`, `--state-dir DIR` (default `<study>/forum/upstream-watch`), `--outdir DIR`
(default `<study>/docs/watch`), `--log-dir DIR`, `--timeout SECONDS`, `-q` / `--quiet`,
`--version`. Exit 0 ok, 1 a feed unreachable (report still written), 2 usage.
`scripts/register_watch_task.ps1` — `-Python`, `-Day`, `-At`, `-Remove`, `-DryRun`, `-Version`.

The course (`course/`, rule 22): `python course/tools/extract_figures.py` —
`--notebook IPYNB [IPYNB ...]`, `--outdir DIR`, `--check`, `-q` / `--quiet`,
`--version`; `python course/tools/build_deck.py` — `--content FILE`, `--check`,
`-q`, `--version`; `python course/tools/make_slides_pdf.py` — `--index FILE`,
`--out FILE`, `-q`, `--version` (Playwright); `python course/tools/verify_deck.py`
— `--index FILE`, `--screens DIR`, `--no-screens`, `-q`, `--version` (Playwright);
`python course/tools/make_handout.py` — `--src FILE`, `--out FILE`, `-q`,
`--version` (Playwright); `python course/tools/build_pptx.py` — `--index FILE`,
`--out FILE`, `-q`, `--version` (Playwright + python-pptx). Order after a
chapter changes: execute → extract_figures → build_deck → make_slides_pdf →
`pytest tests/test_course.py`.

Installers: `scripts/install_rmcprofile_windows.ps1 [-DryRun] [-Conda path]`,
`scripts/install_rmcprofile.sh [--dry-run] [--conda path]` — conda env
`rmcprofile`, kernel `rmcprofile-mc`, explicit per-step status.

## Python API (scripts/rmcprofile_tools.py)

Formats: `read_rmc6f`, `Rmc6f.write/cart/concentrations`, `read_dat`,
`DatFile.get/set/write/data_blocks/filenames/minimum_distances/time_limit_minutes`,
`read_data_file`, `write_data_file`, `read_bragg`, `read_back`, `read_inst`,
`read_hkl`, `read_dw`, `read_chi2_history`, `read_csv_pair`,
`read_partials_csv`. Checker: `check_input_set(stem, dir) -> [Finding]`.
Package: `find_package(home=None) -> Package|None`, `package_env(pkg)`,
`run_rmcprofile(stem, dir, pkg, timeout_min=None) -> RunResult`.
Analysis: `pair_labels`, `rmc_grid`, `partial_gr(cfg, rmax, dr, grid)`, `neutron_weights`,
`total_gr`, `fq_from_gr`, `coordination`, `bond_angles`, `average_cell`, `NEUTRON_B`.
Configurations: `lattice_from_cell`, `build_configuration(cell, sites, supercell)`,
`fold_to_unit_cell`, `export_xyz`, `export_cif`. Scattering: `faber_ziman_sq`,
`total_fq_from_partials(r, partials, cfg, q, radiation)`, `xray_form_factor` (needs `periodictable`),
`xray_weights`, `xray_coefficients_rmcprofile` (manual App. D), `cromer_mann_4term`,
`write_xray_file`, `ATOMIC_NUMBER`. Runs: `write_input_set(stem, dir, cfg, gr=, fq=, min_dist=, max_move=, time_limit_min=)`,
`bond_valence_sum(cfg, centre, neighbour, r0, b, cutoff)`.
Adapter (`upstream_adapter`): `EXERCISES`, `stage_exercise`, `crosscheck_partials`,
`crosscheck_gofr`, `run_and_crosscheck`, `load_records`, `save_records`, `within_tolerance`.
Engine (`rmclite`): `Box`, `Histogram`, `PartialTarget`, `TotalGTarget`, `FqTarget`,
`ClosestApproach`, `DistanceWindow`, `BondPotential`, `RmcLite`, `RunState`,
`synth_targets`, `rms_displacement`, `parse_min_dist`, `KB_EV`.

## Tests and checks

```
python -m pyflakes scripts tests docs          # must be silent
python -m pytest tests -q                      # ~40 s; package-bound tests skip without RMCPROFILE_HOME
python scripts/verify_rmcprofile.py
python tests/conformance.py --repo .           # vendored publication checker
```

The suite guards the docs: every flag above must appear in this file and in
`docs/USER_MANUAL.md`; `VERSION`, `CITATION.cff`, `CHANGELOG.md` and the
`SKILL.md` heading must agree; every `references/*.md` that `SKILL.md` names
must exist.

## Rules

- Nothing from the RMCProfile package in a tracked file: no binary, no
  bundled Python, no tutorial data, no manual text beyond a short cited
  excerpt. Fixtures are written by the tests.
- Formats come from the manual (`references/formats.md` cites the section),
  methods from the papers (`references/method.md`).
- Every `.py` starts with the SPDX header; every behaviour change bumps
  `VERSION` and `CHANGELOG.md`; release = tag `rmcprofile-skill-vX.Y.Z` after
  a green suite in a clean clone of the split.
- The withheld-material guard (`tests/test_no_held_material.py`) scans the
  whole git repository this product lives in.

## Release recipe (study repo → public repo)

```
git subtree split --prefix=rmcprofile-skill -b skill
git clone -b skill <study-repo> <tmp> && cd <tmp>
python -m pyflakes scripts tests docs && python -m pytest tests -q && python scripts/verify_rmcprofile.py
python tests/conformance.py --repo .
git tag -a rmcprofile-skill-vX.Y.Z -m "..."      # on the study repo; push of `skill` only when the owner says so
```
