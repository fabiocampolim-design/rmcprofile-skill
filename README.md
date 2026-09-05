# rmcprofile-skill

An AI-agent skill and verified Python toolkit for
[RMCProfile](https://rmcprofile.ornl.gov/), the Reverse Monte Carlo program
for total scattering — with executed chapter notebooks and an undergraduate
course to follow in later releases.

RMCProfile itself is not included: download it from the RMCProfile site,
unpack it, and set `RMCPROFILE_HOME` to its `RMCProfile_package` directory.
Everything here that does not need the binary works without it.

## What it does

- **Drive** an RMCProfile 6.7.9 installation: read and write every input
  format (`.dat` keyword blocks, `.rmc6f` configurations, data files, the
  Bragg family, `.dw`), check an input set for the mistakes the manual warns
  about (and two it does not: the silent `.poly` wait and the exit-code-0
  stop), run the binary with the environment its setup script would set, and
  parse every output (χ² history, fit CSVs, partials).
- **Analyse** configurations without the binary: partial g(r), Keen's G(r)
  in barn, F(Q), coordination numbers, bond-angle distributions, the average
  cell — validated on exact geometry and on the identity
  G(r→0) = −(Σ c_i b_i)² that the package's own SF6 data reproduces.
- **Cross-check** itself against the installed package: stage any shipped
  exercise, run it, and compare our partials and G(r) with RMCProfile's own
  CSVs to recorded tolerances.
- **Teach** with `rmclite`, a clean-room Reverse Monte Carlo engine whose
  calculated functions equal RMCProfile's by construction: moves, χ² terms,
  constraints, a bond potential, Metropolis acceptance — small enough to read.
  The chapters (one per data type the program fits) and the course follow.

## Install

```
scripts\install_rmcprofile_windows.ps1        # Windows: conda env `rmcprofile` + kernel; -DryRun first
bash scripts/install_rmcprofile.sh            # Linux / macOS / WSL; --dry-run first
export RMCPROFILE_HOME=/path/to/RMCProfile_package    # the directory with exe/ and tutorial/
python scripts/verify_rmcprofile.py           # five checks, exit 0 only when all pass
```

`docs/USER_MANUAL.md` has the full walk-through; `AGENTS.md` the contract
for agents; `SKILL.md` the workflows.

## Quick start

```
python scripts/verify_rmcprofile.py                                   # environment + physics + package smoke test
python scripts/rmcprofile_tools.py check  sf6 --dir runs/sf6          # findings, exit 1 on any ERROR
python scripts/rmcprofile_tools.py run    sf6 --dir runs/sf6 --timeout 10
python scripts/rmcprofile_tools.py pdf    runs/sf6/sf6.rmc6f --rmax 8 --outdir out
python scripts/rmcprofile_tools.py coord  runs/sf6/sf6.rmc6f --pair S F --rmax 2.0
python scripts/rmcprofile_tools.py angles runs/sf6/sf6.rmc6f --triplet S F F --rmax 2.0
python scripts/upstream_adapter.py crosscheck ex_1 --timeout 3            # our partials vs the package's, to tolerance
python scripts/rmclite.py synth truth.rmc6f --displace 0.05 --rmax 5 --outdir out
python scripts/rmclite.py fit average.rmc6f --target out/truth_target_PDFpartials.csv --moves 3000 --outdir out
```

## What is verified

- Suite of 146 checks (`python -m pytest tests -q`), pyflakes clean; the
  package-bound tests (real smoke test, layout) skip without
  `RMCPROFILE_HOME` and pass with either build.
- Both 6.7.9 builds installed and every shipped tutorial exercise run from
  pristine copies on Windows (CUDA build) and WSL Ubuntu (CPU build). The
  deterministic passes (`TIME_LIMIT 0`) print identical χ²/dof on both:
  SF6 0.4201, SF6 10×10×10 3.915, GaPO4 X-ray 252.5. The smoke test takes
  2–6 s.
- The Keen identity for SF6: our neutron weights give G(0) = −0.2759 barn,
  the value at which the package's own G(r) data file starts.
- On RMCProfile's r grid (r_k = k·dr, bins centred on r_k) our partials equal
  the package's `_PDFpartials.csv` to 2.8e-4 (its single precision) and our
  G(r) its `PDF1 (RMC)` column to 3e-5 barn, on both builds — the cross-check
  adapter asserts this against `tests/records/crosscheck_v1.json`.
- `rmclite`: incremental histograms bit-equal to a rebuild, constraints never
  violated, seeds reproduce, a harmonic bond thermalises to 0.78 k_BT/k, and a
  fit from the average structure cuts χ² by four orders of magnitude while
  reproducing the pair distribution rather than the coordinates.
- Formats round-trip on synthetic fixtures and were corrected against the
  real files the package writes (see `references/pitfalls.md`).

## Roadmap

X-ray weights and EXAFS parsing, chapter notebooks for every data type,
the course, the weekly upstream watch, more exercises in the cross-check
records.

## Licence

Apache-2.0 — see `LICENSE` and `NOTICE`.

### Disclaimer

This software is provided "as is", without warranties or conditions of any
kind, express or implied, including but not limited to merchantability, fitness
for a particular purpose and non-infringement. In no event shall the authors be
liable for any claim, damages or other liability arising from its use.
This project is independent and not affiliated with or endorsed by the
RMCProfile developers, Oak Ridge National Laboratory, ISIS/STFC, NIST or the
universities named in `NOTICE`. RMCProfile is distributed by its authors under
their own terms ("AS IS and for non-profit making purposes"); this project
does not redistribute it.

## Citation

`CITATION.cff`. Cite RMCProfile itself as Tucker et al., *J. Phys.: Condens.
Matter* 19 (2007) 335218 and Zhang et al., *J. Appl. Cryst.* 53 (2020) 1509.
