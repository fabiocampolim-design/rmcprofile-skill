# Pitfalls — what went wrong while building this, and where it is guarded

Each entry: symptom · cause · fix · where the toolkit guards it. Dates are
the day the trap was met on the reference machine (Windows 10, WSL2 Ubuntu,
RMCProfile 6.7.9 Windows Serial and Linux 64 builds).

## RMCProfile itself

- **"Waiting for .poly file" forever.** A `.dat` with `POLYHEDRAL_RESTRAINT ::`
  makes the program wait, silently and indefinitely, for `<stem>.poly`; it
  never times out. Cause: the file was deleted while "cleaning outputs" —
  `.poly`, `.fs` and `.sf` are *inputs*. Fix: keep them. Guard:
  `check_input_set` → `ERROR poly-file-missing` (2026-09-05).
- **Missing configuration exits with code 0.** "The file X.rmc6f does not
  exist! Hence we have to stop ..." — and the process returns 0. Scripts
  that trust the exit code see a successful run with no outputs. Guard: the
  checker refuses to start a run without a configuration
  (`ERROR no-configuration`); `run_rmcprofile` reports `outputs` and
  `final_chi2`, which are empty in this case — read them, not the code.
- **`.his6f` silently replaces `.rmc6f`.** A run directory with a leftover
  history file continues that refinement, whatever the `.rmc6f` says, unless
  the `.dat` carries `IGNORE_HISTORY_FILE ::`. Guard: `INFO history-file`.
- **Stale neighbour files.** `.neigh`/`.neighlist` encode the connectivity
  for distance-window and coordination constraints; after any change to the
  configuration they must be deleted (manual §5.6.1). Guard:
  `WARN stale-neighbour-files`.
- **`END_POINT` beyond the data is not an error.** The package's own smoke
  test uses `END_POINT :: 3000` on a 1186-point file; RMCProfile clamps.
  Guard: `WARN end-point-beyond-data` (was an ERROR until the smoke test
  proved otherwise).
- **`MINIMUM_DISTANCES` is per pair, `MAXIMUM_MOVES` per type.** Three types
  need six distances (AA AB AC BB BC CC) and three moves; the program's only
  hint is "Check the 'MINIMUM_DISTANCES' section ... if program stops here".
  Guard: `ERROR minimum-distances-count`, `ERROR maximum-moves-count`.
- **Two densities.** The `.dat` `NUMBER_DENSITY` and the configuration's
  header density can differ; the program prints both and uses the
  configuration's ("Using the configuration density"). Keep them equal when
  you write a `.dat` for a new box.
- **`TIME_LIMIT :: 0` is a feature.** Setup, one pass, χ² report, save —
  2–6 s for the 378-atom SF6 case. Use it to validate an input set before a
  long run.
- **The tutorial's SrTiO3 input set is hidden.** `ex_4/*/rmc/` holds only
  the `.dat` and `.dw`; the configuration and Bragg files sit in the hidden
  `rmc/.run/` directory (and the data in `../data/`). Copy `.run/.` too.
- **Exercise 7 (EXAFS) runs for 1000 minutes as shipped**, not the 5 the
  tutorial text promises; edit `TIME_LIMIT` before starting it.

## The two builds

- **Windows Serial = CUDA build.** `rmcprofile.exe` prints "Use CUDA
  version" when an NVIDIA GPU is present (GTX 1050 Ti here); the Linux 64
  tarball prints "Use CPU version" with OpenMP threads. On the SF6 exercise
  the Windows build generated 2.5× more moves in the same 10 minutes
  (101 804 vs 41 506) and reached χ² 0.53 where the CPU build was at 38.8 —
  the runs started from the same χ² (831.9); on the SrTiO3 293 K exercise the
  two builds were equal (93 500 vs 90 606). The gap depends on the exercise.
  Compare χ² at equal *moves*, not equal wall time, across builds.
- **WSL runs the Linux build from `/mnt/d` without `chmod`** (drvfs marks
  everything executable), but keep the *work directory* on the Linux
  filesystem (`/tmp`, `$HOME`): the periodic saves are I/O-bound and the
  move rate on `/mnt/*` degrades over a run (6 → 14 ms per move seen).
- **Both builds agree on the deterministic pass.** With `TIME_LIMIT 0` the
  SF6, SF6-10×10×10 and GaPO4 X-ray exercises print identical χ² on Windows
  and WSL (0.4201, 3.915, 252.5). A refinement (random moves) does not
  reproduce across builds or runs; only its statistics do.
- **The Linux build's `manual` and `tutorial` commands do nothing**: they
  call macOS `open`. Read `tutorial/*.pdf` directly.

## Formats

- **RMCProfile's own `.rmc6f` output differs from `data2config`'s.** Atom
  lines become `index label [1] x y z` — a bracketed flag, no site or cell
  columns — and the header order changes. `read_rmc6f` skips bracketed
  tokens and tolerates the missing columns (`site`/`cellidx` are zeros).
- **A shipped `.bragg` carries more rows than its header count** (1180
  declared, 1184 present). RMCProfile reads `npoints`; so does `read_bragg`.
- **One shipped `.rmc6f` is CRLF** (`ex_3`). `splitlines()` handles it;
  a reader that splits on `\n` alone keeps a `\r` on every atom line.
- **Fortran `D` exponents** appear in data files (`2.000D-02`); every numeric
  reader here maps `D`→`E`.
- **Block or scalar?** `POLYHEDRAL_RESTRAINT :: 5` is a block with no items,
  `IGNORE_HISTORY_FILE ::` a scalar with no value, `BOX_SIZE :: 8 8 8` a
  scalar. `references/formats.md` records the rule and the known keyword
  sets; a new keyword with an integer value that is really a scalar must be
  added to `_SCALAR_KEYWORDS` or it opens an empty block (harmless for
  reading, wrong for `write`).

## The analysis routines

- **`rmax` must be below half the shortest cell edge** (minimum image);
  `partial_gr` refuses otherwise. Build a bigger supercell instead.
- **Ideal-lattice distances can sit on a histogram bin edge** and split
  between two bins; the shell *integral* is exact, the bin *maximum* is not.
- **Neutron weights are for natural abundance.** Enter deuterium as `D`,
  and any enriched isotope as its own type with its own `b`.

## Building on Windows

- **Console is cp1252.** Run every Python command with
  `PYTHONIOENCODING=utf-8` or the first `Å` in a message raises
  `UnicodeEncodeError`.
- **`write_text` uses CRLF on Windows.** Fixtures that need LF (or that test
  CRLF handling) normalise explicitly, as `tests/test_rmc6f.py` does.
