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
Exit 0 only when every check passes; the package smoke test is `[SKIP]`
without a package.

`python docs/build_manual.py` — `docs/USER_MANUAL.md` → HTML (+ PDF with
pandoc): `--outdir`, `--no-pdf`, `-v` / `--verbose`.

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
Analysis: `pair_labels`, `partial_gr`, `neutron_weights`, `total_gr`,
`fq_from_gr`, `coordination`, `bond_angles`, `average_cell`, `NEUTRON_B`.

## Tests and checks

```
python -m pyflakes scripts tests docs          # must be silent
python -m pytest tests -q                      # ~20 s; package-bound tests skip without RMCPROFILE_HOME
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
