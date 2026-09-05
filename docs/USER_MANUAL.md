# rmcprofile-skill — User Manual

Version 0.1.0. A Python toolkit, AI-agent skill and (from later releases)
chapter notebooks and a course on Reverse Monte Carlo modelling of total
scattering data with [RMCProfile](https://rmcprofile.ornl.gov/).

## 1. What you need

| Component | Where it comes from |
|---|---|
| Python 3.12 with numpy, scipy, matplotlib, pytest | the installers below create the conda env `rmcprofile` |
| RMCProfile 6.7.9 | **you** download it from rmcprofile.ornl.gov/download/ (SourceForge; a browser download works, plain `curl` is blocked), unpack it, and set `RMCPROFILE_HOME` to the `RMCProfile_package` directory — the one that contains `exe/` and `tutorial/`. It is distributed by its authors "AS IS and for non-profit making purposes"; this project does not redistribute it |

Everything that does not need the binary — formats, the checker, the
configuration analysis — works without `RMCPROFILE_HOME`; package-bound
checks and tests are skipped, never failed, when it is unset.

## 2. Install

Windows (PowerShell):

```
scripts\install_rmcprofile_windows.ps1 -DryRun     # prints every command
scripts\install_rmcprofile_windows.ps1             # creates env + kernel rmcprofile-mc
$env:RMCPROFILE_HOME = "C:\RMCProfile\RMCProfile_package"
```

Linux / macOS / WSL:

```
bash scripts/install_rmcprofile.sh --dry-run
bash scripts/install_rmcprofile.sh [--conda /path/to/conda]
export RMCPROFILE_HOME=$HOME/RMCProfile_package
```

Both scripts print one status line per step (`create-env : OK`, …) and a
`rmcprofile-package : FOUND|NOT FOUND` line. Then:

```
python scripts/verify_rmcprofile.py
```

Five checks: imports; formats round trip; the Keen identity
G(r→0) = −(Σ c_i b_i)² for SF6 (−0.2759 barn); rock-salt shells and
coordination; the package smoke test (`tutorial/ex_1` in a temp dir, a few
seconds, χ²/dof 0.4201). Flags: `-q` / `--quiet`, `--home` (package
directory instead of `RMCPROFILE_HOME`), `--minutes` (cap for the smoke
test, default 3.0), `--version`. Exit 0 only when every check passes.

Always run with `PYTHONIOENCODING=utf-8` on Windows (cp1252 console).

## 3. The toolkit: `scripts/rmcprofile_tools.py`

Global flags, accepted before or after a subcommand: `--version`,
`--selftest` (round-trip every format on synthetic files, exit 0/1),
`--outdir` (where outputs go, default `out`), `--log-dir` (where the JSON
audit log goes, default `logs`), `-q` / `--quiet`. Every run writes
`logs/rmcprofile_tools_<timestamp>.json` with the version, arguments, verdict
and checks.

### `check` — validate an input set

```
python scripts/rmcprofile_tools.py check STEM --dir RUNDIR
```

`--dir` is the directory holding `STEM.dat` and its companions. Output: one
line per finding, `LEVEL code: message`; exit 1 if any ERROR.

| Code | Level | Meaning |
|---|---|---|
| `no-dat`, `dat-parse` | ERROR | no `STEM.dat`, or it has no `END ::` / an item outside a block |
| `no-configuration` | ERROR | no `STEM.rmc6f`, `.his6f` or `.cfg` — RMCProfile would stop (with exit code 0) |
| `rmc6f-parse` | ERROR | header and atom lines disagree |
| `atom-order` | ERROR | `ATOMS ::` order differs from the configuration's |
| `minimum-distances-count`, `maximum-moves-count` | ERROR | wrong number of values (per pair AA AB AC BB BC CC; per type) |
| `data-block-no-filename`, `data-file-missing`, `data-file-parse` | ERROR | a data block's file |
| `bragg-file-missing`, `bragg-inst-missing`, `bragg-back-missing`, `bragg-parse` | ERROR | the `BRAGG ::` block's files |
| `poly-file-missing` | ERROR | `POLYHEDRAL_RESTRAINT ::` without `STEM.poly` — RMCProfile waits for it forever |
| `end-point-beyond-data` | WARN | RMCProfile clamps `END_POINT` to the data length |
| `no-weight`, `hkl-range-unspecified`, `stale-neighbour-files` | WARN | see `references/pitfalls.md` |
| `history-file`, `potential-lists-regenerated`, `summary` | INFO | |

### `run` — run RMCProfile

```
python scripts/rmcprofile_tools.py run STEM --dir RUNDIR --timeout 10
```

`--dir` as above; `--home` names the package directory (default
`RMCPROFILE_HOME`); `--timeout` kills the run after that many minutes
(reported as `rc=None`). The checker runs first and refuses on an ERROR.
Stdout and stderr go to `RUNDIR/run.log`; the summary line reports the
return code, wall time and output count; `final:` echoes the last row of
`STEM.chi2`. Exit 2 when no package is found.

The runner sets the environment the package's own setup script would
(`references/package.md`): on Windows `RMCPROFILE_DIR` and the `exe`,
`cygwin_libs`, `cuda_lib` PATH entries; on Linux `RMCProfile_PATH`,
`PGPLOT_DIR`, `LD_LIBRARY_PATH`, `LIBRARY_PATH` and `exe` on PATH.

### `pdf`, `coord`, `angles` — analyse a configuration

```
python scripts/rmcprofile_tools.py pdf    FILE.rmc6f --rmax 8 --dr 0.02 --qmax 30 --dq 0.02 --radiation neutron --outdir out
python scripts/rmcprofile_tools.py coord  FILE.rmc6f --pair Na Cl --rmax 3.0
python scripts/rmcprofile_tools.py angles FILE.rmc6f --triplet Na Cl Cl --rmax 3.0 --dangle 2 --outdir out
```

- `pdf`: partial g_ij(r) by histogram (minimum image; `--rmax` must be below
  half the shortest cell edge, `--dr` the bin), Keen's G(r) in barn with
  neutron weights (`--radiation {neutron,xray}`; `xray` is reserved for the
  X-ray chapter), and F(Q) on `--dq` … `--qmax`. Files:
  `<stem>_PDFpartials.csv`, `<stem>_GofR.csv`, `<stem>_FofQ.csv` (same
  layout as RMCProfile's own CSVs, readable with `read_csv_pair` /
  `read_partials_csv`).
- `coord`: number of B atoms within `--rmax` of every A (`--pair A B`),
  printed as mean and histogram.
- `angles`: B-A-C angles for `--triplet A B C` with both arms within
  `--rmax`, histogrammed in `--dangle`-degree bins to
  `<stem>_angles_B-A-C.csv`.

## 4. Python API

```python
import sys; sys.path.insert(0, "scripts")
import rmcprofile_tools as rt
cfg = rt.read_rmc6f("sample.rmc6f")            # Rmc6f: atom_types, counts, cell, lattice, frac, site, cellidx
r, parts = rt.partial_gr(cfg, rmax=8.0, dr=0.02)
r, G = rt.total_gr(r, parts, cfg)              # barn
F = rt.fq_from_gr(r, G, cfg.density, q)
d = rt.read_dat("sample.dat"); d.set("BRAGG", "WEIGHT", "0.02"); d.write("sample.dat")
res = rt.run_rmcprofile("sample", ".", rt.find_package())
x, calc, expt = rt.read_csv_pair("sample_PDF1.csv")
```

Definitions and citations: `references/method.md`. File layouts:
`references/formats.md`.

## 5. The manual builder

```
python docs/build_manual.py [--outdir DIR] [--no-pdf] [-v | --verbose]
```

Writes `USER_MANUAL.html` (pandoc if present, else a built-in converter)
and, with pandoc and a LaTeX engine, `USER_MANUAL.pdf`.

## 6. Troubleshooting

| Symptom | See |
|---|---|
| the run prints "Waiting for .poly file" and never ends | `check` → `poly-file-missing`; never delete `.poly`, `.fs`, `.sf` |
| the run "stops" with exit code 0 and no outputs | a missing configuration; read `outputs`/`final_chi2`, not the code |
| a refinement continues from an old state | a leftover `.his6f`; add `IGNORE_HISTORY_FILE ::` or delete it |
| WSL runs are much slower than Windows | CPU build vs CUDA build, and `/mnt/*` I/O — work in `/tmp` or `$HOME` |
| `UnicodeEncodeError` on Windows | `PYTHONIOENCODING=utf-8` |
| `rmax exceeds half the shortest cell edge` | enlarge the supercell |

More in `references/pitfalls.md`.

## 7. Licence

Apache-2.0 (`LICENSE`, `NOTICE`). Independent of and not affiliated with
the RMCProfile developers or their institutions. RMCProfile is distributed
by its authors under their own terms; this project does not redistribute
it.
