# Design — rmcprofile-skill

The decisions behind this repository and the trade-offs they carry. The
build history is `CHANGELOG.md`; the agent contract `AGENTS.md`.

## What it is for

An AI-agent skill plus a verified Python toolkit for RMCProfile, built by
studying the program, its manual, its tutorials and its shipped package end
to end, so that (a) an agent or a person can set up, check, run and analyse
a refinement without re-reading 195 pages, and (b) the findings of that
study flow back to the developers as reports and documentation patches.
Chapter notebooks and an undergraduate course follow in later releases,
together with a small clean-room RMC engine for teaching.

## Decisions

1. **Nothing from the package is redistributed.** RMCProfile is
   closed-source Fortran shipped as binaries under a "non-profit purposes"
   disclaimer and no licence file. The toolkit locates the user's own copy
   through `RMCPROFILE_HOME`; test fixtures are synthetic files in the
   documented layouts; the manual is cited by section, never copied.
   Package-bound tests skip without the package so CI runs anywhere.
2. **Formats from the manual, then corrected by the real files.** The first
   readers were written from the manual's descriptions; the package's own
   smoke test then showed three layouts the manual does not spell out (the
   program's `[1]` atom-line flag, a `.bragg` with more rows than its header
   count, a clamped `END_POINT`). Each became a test with a synthetic
   fixture and an entry in `references/pitfalls.md`.
3. **One module, four responsibilities, one CLI.** `scripts/rmcprofile_tools.py`
   holds formats, checker, runner and analysis in clearly separated
   sections rather than four modules, so that a skill user imports one name;
   the CLI has one global option set accepted before or after a subcommand.
4. **The checker encodes the manual's warnings, not opinions.** Every ERROR
   corresponds to a documented failure (missing files, count mismatches,
   the `.poly` wait, the exit-code-0 stop); things RMCProfile tolerates are
   WARN or INFO.
5. **Analysis from Keen's definitions, validated on exact geometry.** G(r)
   in barn with natural-abundance neutron weights, F(Q) by direct transform,
   minimum image with an explicit half-box limit; tests use an ideal
   rock-salt lattice (known shells, known coordination, known angles) and
   the SF6 identity G(0) = −(Σ c b)² that the package's own data file
   reproduces.
6. **Two builds, both driven, both audited.** The Windows Serial zip and the
   Linux 64 tarball were installed and every shipped exercise run on both;
   the environment each setup script establishes is reproduced by
   `package_env()`. Deterministic passes agree to the printed precision;
   refinements differ by build (CUDA vs CPU move rate) and by seed.
7. **rmclite computes RMCProfile's functions by construction.** The teaching
   engine reuses the toolkit's grid and normalisation, so what it fits is
   exactly what the package tabulates; the package-bound test proves it on
   the shipped configuration. Its validations are honest about what RMC
   does: it reproduces the pair distribution, not the coordinates.
8. **Cross-check records are ours.** `tests/records/crosscheck_v1.json`
   stores tolerances, our measured maxima and a provenance line per
   exercise — never the package's data — so a regression in our histogram
   or weights is caught against a number that was actually measured on
   both builds.
9. **Docs are guarded by the suite.** Every CLI flag and subcommand must be
   in `AGENTS.md` and the manual; version strings must agree across
   `VERSION`, `CITATION.cff`, `CHANGELOG.md`, `SKILL.md`.

10. **The chapters are generated, executed and measured.** Every notebook in
   `chapters/` comes from `build/part*.py` through `build/assemble.py`
   (header, table of contents and tally cells are generated; global section
   and figure numbers), is executed by `build/execute.py` on the
   `rmcprofile-mc` kernel, and carries `check(...)` lines whose PASS/FAIL
   totals the suite pins. Package-bound cells skip without `RMCPROFILE_HOME`
   and say so. Where the manual and the program disagree the chapter
   *measures* the program (chapter 7: the damping is Gaussian, the
   nanoparticle keyword corrects the baseline) and the finding goes to the
   study repository's ledger; where the book cannot reproduce something
   (the X-ray F(Q) shape, magnetic and diffuse fits) it says so in the
   chapter rather than lowering a threshold until a check passes.

## What was deliberately left out of 0.3.0

EXAFS χ(k) computation and magnetic / diffuse-scattering models (chapter 8
runs the shipped EXAFS exercise and documents the other two); `.bvs`,
`.bonds`, `.triplets` readers; an F(Q) cross-check (RMCProfile convolves
F(Q) with the box function) and the X-ray F(Q) processing (finding N-8);
the `rmc_tools` parser comparison (its conda package ships Python 3.7
builds only); the course and the weekly upstream watch script (next
releases).

## Verified with

Suite of 146 checks (pytest; package-bound ones skip without
`RMCPROFILE_HOME`), pyflakes clean, `verify_rmcprofile.py` on the Windows
build and, through a Linux venv, on the WSL build; the S1 audit log of every
shipped exercise on both builds lives in the study repository.
