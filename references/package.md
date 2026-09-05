# The RMCProfile package — what it is and how the toolkit reaches it

RMCProfile is a closed-source Fortran95 program distributed as compiled
packages from SourceForge (`sourceforge.net/projects/rmcprofile/files/`),
linked from `rmcprofile.ornl.gov/download/`. Its terms are the site's
disclaimer: *"delivered to you AS IS and for non-profit making purposes"*.
This project never redistributes any part of it — you download and unpack
the package yourself, then tell the toolkit where it is.

## Versions and files (2026-09-04)

| Version | Files | Notes |
|---|---|---|
| **6.7.9** (stable, June 2025) | `RMCProfile_V6.7.9_Windows_Serial.zip` (845 MB), `..._Windows_Parallel.zip`, `..._Linux_64.tgz` (475 MB), `..._Linux_64_Legacy.tgz`, `..._Linux_64_ARM64.tgz`, `..._Linux_64_GPU.tgz`, `..._Mac_Intel.dmg`, `..._Mac_ARM64.dmg` | the version this toolkit drives; the Linux setup script announces `6.7.9.5`, the shipped `.out` files were made by `6.7.9.1` |
| 7b.35 (beta) | Linux X64/Legacy/ARM64, macOS X64/ARM64, Windows X64 | mixed-phase RMC, molecular potentials, automatic weights (change-log page); watched, not driven |
| 6.5.2 (old) | Linux 32/64, macOS Lion/Mavericks, Windows | historical |

SourceForge answers plain `curl` with a Cloudflare JavaScript challenge; a
browser download works. Unpack the archive; the directory you need is the
one that contains `exe/` and `tutorial/` (called `RMCProfile_package`).

## Layout of `RMCProfile_package`

| Entry | Windows Serial | Linux 64 |
|---|---|---|
| setup | `RMCProfile_setup.bat` → `exe\setup_cmds.bat "<HOME>"` | `RMCProfile_setup` → `exe/setup_cmds <HOME>` (opens an xterm); `RMCProfile_setup_no_term` |
| `exe/` | 77 entries: `rmcprofile.exe` and ~40 tool `.exe`, `.bat` wrappers, `Python38/` (bundled interpreter for `rmcplotpy.bat` and the Python tools), `cygwin_libs*/`, `cuda_lib/`, `FoX/`, `modules/`, `libs/` | 61 entries: `rmcprofile` (ELF, links `libs/libgfortran.so.4`), the tools as ELF binaries or shell wrappers, `Python-3.12.2/`, `libs/` (gfortran, PGPLOT, OpenMP, CUDA 12 runtime, `rmcplot.py`, `np_gen.py`, `rmc_strain.py`, `bulk_shells.py`) |
| `tutorial/` | `ex_1 ex_2 ex_3 ex_4 ex_6 ex_7` (no `ex_5`), `rmcprofilemanual.pdf`, `rmcprofile_tutorial.pdf`, `rmcprofile_tutorial_new.pdf`, `GASP manual.pdf` | same |
| helper commands | `manual.bat`, `tutorial.bat` open the PDFs; `rmcplotpy.bat` = `python exe\libs\rmcplot.py "%cd%" <stem>`; `rmcprofile.bat` starts a run in a new console | `manual`, `tutorial` (`open` the PDFs — macOS command, does nothing on most Linux), `rmcplotpy` = `python -W ignore exe/libs/rmcplot.py "$PWD" <stem>` |

## Environment the package expects

What the setup scripts do, and what `rmcprofile_tools.package_env()` sets
instead so a run works from any process without the interactive window:

| Platform | What `setup` does | The runner sets |
|---|---|---|
| Windows (`setup_cmds.bat "<HOME>"`) | `RMCPROFILE_DIR=<HOME>`, `PATH=<HOME>\exe;<HOME>\exe\cygwin_libs;<HOME>\exe\cuda_lib;%PATH%`, window title, starts `graphics_server.bat` | `RMCPROFILE_DIR` and the three PATH entries; no graphics server (batch runs do not plot) |
| Linux (`exe/setup_cmds <HOME>`) | `PGPLOT_DIR=<HOME>/exe/libs`, `LD_LIBRARY_PATH=<HOME>/exe/libs`, `LIBRARY_PATH=<HOME>/exe/libs`, `PATH=$PATH:<HOME>/exe`, `RMCProfile_PATH=<HOME>`, then `xterm -e $SHELL -i` | the four variables plus `RMCProfile_PATH`; no xterm |

The toolkit finds the package through **`RMCPROFILE_HOME`** (or `--home`):
the `RMCProfile_package` directory. `find_package()` returns `None` when it
is unset or wrong, and every package-bound check or test is skipped, never
failed, without it.

Under WSL the Linux build runs straight from a Windows drive
(`/mnt/d/...`): drvfs presents every file as executable, so no `chmod` was
needed (2026-09-05, WSL2 kernel 6.18, Ubuntu). `ldd exe/rmcprofile` reports
no missing library once `LD_LIBRARY_PATH` points at `exe/libs`.

## Running a refinement by hand

```
cd <work dir with STEM.dat, STEM.rmc6f, data files, Bragg files>
rmcprofile STEM > STEM.log          # Linux/WSL, after the environment above
rmcprofile.exe STEM > STEM.log      # Windows
```

`TIME_LIMIT :: 0.00 MINUTES` in the `.dat` makes the program initialise,
compute every function once, print the χ² summary and save — about 2 s on
WSL and 6 s on Windows for the 378-atom SF6 smoke test (`tutorial/ex_1`).
Both builds print the same numbers for that test:

```
Chi^2/dof        =  0.4201
Expt  Bragg Chi^2/npts   =  0.4834
Expt  1: ... Chi**2/nq =  0.3496      (G(r))
Expt  2: ... Chi**2/nq =  0.7584      (F(Q))
```

## The shipped exercises

| Exercise (tutorial §) | Directory to copy | Stem | Material, atoms, supercell | Data in the `.dat` | `TIME_LIMIT` |
|---|---|---|---|---|---|
| ex_1 (Ex. 1, smoke test) | `ex_1/` (a finished run) | `rmcsf6_190k` | SF6 190 K, 378 atoms, 3×3×3 | neutron G(r) + F(Q), Bragg (gsas2), polyhedral restraint 4 | 0 |
| ex_2 (Ex. 2–3, setting up + basic refinement) | `ex_2/.rmc_start/` (pristine inputs; `ex_2/rmc/` is the authors' finished run; `ex_2/gsas/` the GSAS files `data2config` reads) | `rmcsf6_190k` | SF6, 378 atoms, 3×3×3 | neutron G(r) + F(Q), Bragg, `.dw` | 10 min |
| ex_3 ("other things to try") | `ex_3/sf6/` (finished run; outputs deleted before re-running) | `rmcsf6_190k` | SF6, 10×10×10 supercell | neutron G(r) + three F(Q) banks, Bragg, polyhedral restraint | 0 |
| ex_4 (Ex. 4, SrTiO3 105 K transition) | `ex_4/5K/rmc/` + `ex_4/5K/data/`; same for `293K` | `srtio3_5k`, `srtio3_293k` | SrTiO3, 6×6×4 (5 K) and 8×8×8 (293 K) | neutron G(r) + F(Q), Bragg | 10 min |
| ex_6 (Ex. 5, X-ray) | `ex_6/rmc/start/` (X-ray) and `ex_6/rmc_neutron/start/` (neutron, `.cfg` input) | `gapo4_xray`, `gapo4_neutron` | GaPO4 quartz, 576 atoms, 4×4×2 | X-ray F(Q) + Bragg (xray2), polyhedral restraint 5; neutron G(r)+F(Q)+Bragg (gsas3) + distance window | 0 |
| ex_7 (Ex. 7, EXAFS) | `ex_7/RMC/` (complete run incl. the FEFF-derived path files and absorber/scatterer lists); `Configs/ Exp/ Prep/ First_Run/` are the preparation stages | `snao` | SrAl0.5Nb0.5O3, 8×8×8 box | neutron G(r) + two EXAFS edges (Nb, Sr), weight optimisation | 1000 min in the file (the tutorial text says 5) |

Timings of full re-runs on both builds are recorded in the study repository's
package audit and summarised in `references/pitfalls.md` where they matter.
