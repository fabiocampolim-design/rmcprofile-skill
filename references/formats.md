# RMCProfile 6.7.9 file formats

Every format the toolkit reads or writes, in the layout the RMCProfile manual
v6.7.9 documents (page numbers from the PDF at rmcprofile.ornl.gov/manual/).
The implementation is `scripts/rmcprofile_tools.py`; each section names its
functions. Fixtures in `tests/` are written by the tests in these layouts —
no file from the package is tracked.

## `.rmc6f` — version-6f configuration (manual §4.11, p. 93–96)

`read_rmc6f(path) -> Rmc6f`, `Rmc6f.write(path)`. Line endings LF or CRLF
(one shipped tutorial file is CRLF).

| Line | Meaning | `Rmc6f` field |
|---|---|---|
| `(Version 6f format configuration file)` and any other `(...)` lines | banner, kept verbatim | `banner` |
| `Metadata date: dd-mm-yyyy`, `Metadata title:`, … | free header lines `Key: value` | `header[key]` |
| `Number of types of atoms: n` | | `len(atom_types)` |
| `Atom types present: S F` | order is the order used everywhere else (`.dat` `ATOMS ::`, partials) | `atom_types` |
| `Number of each atom type: 54 324` | | `counts` |
| `Number of moves generated/tried/accepted: n`, `Number of prior configuration saves: n` | run counters | `header[...]` |
| `Number of atoms: N` | must equal the number of atom lines and the sum of counts | `n_atoms()` |
| `Supercell dimensions: na nb nc` | | `supercell` |
| `Number density (Ang^-3): ρ` | | `density` |
| `Cell (Ang/deg): a b c α β γ` | the *supercell* cell | `cell` |
| `Lattice vectors (Ang):` + three rows | rows are the vectors | `lattice` (3×3) |
| `Atoms:` then one line per atom: `index label x y z site ia ib ic` | fractional coordinates of the supercell; `site` = site number in the unit cell; `ia ib ic` = which unit cell | `atoms`, `frac`, `site`, `cellidx` |

`cart()` = `frac @ lattice`. `.his6f` (§4.11.2) starts with the same header
and appends the accumulated PDFs; when present it is read **instead of**
`.rmc6f` unless the `.dat` says `IGNORE_HISTORY_FILE ::` (§3.2).

## `.dat` — main control file (manual §4.1, p. 35–68)

`read_dat(path) -> DatFile`, `DatFile.write(path)`, `get`, `set`,
`data_blocks()`, `filenames()`, `minimum_distances()`, `time_limit_minutes()`.

Three kinds of line, `%%` starts a comment anywhere:

1. **Scalar** `KEY :: value` — `TITLE`, `MATERIAL`, `PHASE`, `TEMPERATURE`,
   `PRESSURE`, `INVESTIGATOR`, `DATA_NOTE`, `RMC_NOTE`, `NUMBER_DENSITY`
   (Å⁻³), `MINIMUM_DISTANCES` (one per pair in the order AA AB AC BB BC CC …),
   `MAXIMUM_MOVES` (one per atom type, Å), `R_SPACING`, `PRINT_PERIOD`,
   `TIME_LIMIT` (minutes; 0 = one pass then save), `SAVE_PERIOD`,
   `INPUT_CONFIGURATION_FORMAT` / `SAVE_CONFIGURATION_FORMAT` (`rmc6f`,
   `cfg`, `his6f`), `IGNORE_HISTORY_FILE ::` (empty value), `SEED`, `BOX_SIZE`.
2. **`ATOMS :: S F`** — the atom types, same order as the configuration.
3. **Block** `NAME ::` or `NAME :: n`, followed by item lines `> KEY :: value`
   or flag lines `> FLAG`. A line `KEY ::` / `KEY :: <integer>` with an
   upper-case key that is not a known scalar opens a block; a block may have
   no items (`POLYHEDRAL_RESTRAINT :: 5`, GaPO4 exercise). Blocks seen in the
   package: `FLAGS` (`NO_MOVEOUT`, `NO_SAVE_CONFIGURATIONS`,
   `NO_RESOLUTION_CONVOLUTION`), `NEUTRON_REAL_SPACE_DATA :: n`,
   `NEUTRON_RECIPROCAL_SPACE_DATA :: n`, `XRAY_RECIPROCAL_SPACE_DATA ::`,
   `EXAFS ::`, `BRAGG ::`, `POTENTIALS ::`, `BVS ::`, `DISTANCE_WINDOW ::`,
   `POLYHEDRAL_RESTRAINT :: n`, `FIXED_COORDINATION_CONSTRAINTS :: n`,
   `AVERAGE_COORDINATION_CONSTRAINTS :: n`, `WEIGHT_OPTIMIZATION ::`.

Data-block items (§4.12): `FILENAME`, `DATA_TYPE` and `FIT_TYPE` (`F(Q)`,
`S(Q)`, `i(Q)`, `G(r)`, `D(r)`, `T(r)` — see `method.md`), `START_POINT`,
`END_POINT` (indices into the data file), `CONSTANT_OFFSET`, `WEIGHT` (σ of
that data set in χ²), `NEUTRON_COEFFICIENTS`, `CONVOLVE ::`, `STOG`,
`NO_FITTED_OFFSET`, `NO_FITTED_SCALE`, `RECIPROCAL_SPACE_FIT`,
`REAL_SPACE_FIT`, `RECIPROCAL_SPACE_PARAMETERS`, `REAL_SPACE_PARAMETERS`.
Bragg items (§4.13): `BRAGG_SHAPE` (`gsas`, `gsas2`, `gsas3`, `GSAS3_NEW`
for GSAS-II, `xray2`, `topas`), `SUPERCELL`, `RECALCULATE`, `DMIN`, `WEIGHT`.
Item lines come in three shapes and the writer keeps each: `> KEY :: value`, `> KEY ::` with
no value (the program's own files write `CONVOLVE ::` this way; `DatBlock` stores `""`) and a bare
`> FLAG` (`NO_FITTED_OFFSET`, `RECALCULATE`; stored as `None`).
The file ends with `END ::`; the parser refuses a file without it.

## Experimental data files (manual §4.12, p. 97–98)

`read_data_file(path) -> DataFile(x, y, err, title, metadata)`,
`write_data_file(path, x, y, title, err=None, style="two-line"|"stog")`.

- **Two-line header** (what the package's exercises ship): line 1 = number
  of points, line 2 = a title (often `<name> mutli by <scale>`), then
  whitespace-separated columns `x y [err]`.
- **STOG style** (§5.1.1): `# Key: value` metadata lines (`File`, `Title`,
  `Number of points`, …), a `# ----` rule, then columns.
- Fortran `D` exponents are accepted. `x` is Q (Å⁻¹) or r (Å) as the block's
  `DATA_TYPE` implies.

## Bragg family (manual §4.13, p. 99–101)

| File | Layout | Function |
|---|---|---|
| `.bragg` | line 1: `npoints bank scale volume` (scale from the GSAS refinement, volume unused); line 2: a title; then `time intensity` rows — `npoints` of them | `read_bragg -> Bragg` |
| `.back` | `n` then `n` background coefficients (Chebyshev, GSAS) | `read_back -> ndarray` |
| `.inst` | `nbanks`, then for each bank its number on its own line followed by the GSAS profile-parameter lines | `read_inst -> [ {bank, values} ]` |
| `.hkl` | `scale` then three lines `hmin hmax step` | `read_hkl -> {scale, ranges}` |
| `.dw` (§2.5, now usually inside the `.dat`) | one line per pair: `flag rmin rmax` | `read_dw -> [(flag, rmin, rmax)]` |

`.poly`, `.fs`, `.sf` (polyhedral restraint and form-factor inputs) are
inputs the tutorial ships and RMCProfile waits for — never delete them when
cleaning a run directory.

## Output files (manual §3.4, p. 33–34)

| File | Content | Function |
|---|---|---|
| `<stem>.out` | summary, partial g(r) tables | (text) |
| `<stem>.chi2` / `<stem>_chi2.txt` | header `m_accepted m_generated m_tested chi2 Bragg_Chi2 Expt_1 …`, one row per print | `read_chi2_history -> {column: array}` |
| `chi2.dat`, `chisq0.txt`, `derivative.log`, `weights.log`, `weights_update.dat` | weight-optimisation bookkeeping | (text) |
| `<stem>_SQn.csv`, `<stem>_PDFn.csv`, `<stem>_FQn.csv`, `<stem>_XFQn.csv`, `<stem>_FT_XFQn.csv`, `<stem>_bragg.csv` | `x, calculated, experiment` (header names differ) | `read_csv_pair -> (x, calc, expt)` |
| `<stem>_PDFpartials.csv`, `<stem>_SQnpartials.csv`, `<stem>_FQnpartials.csv` | `r/Q, pair, pair, …` with a trailing comma | `read_partials_csv -> (x, {pair: values})` |
| `<stem>.braggout` | calculated and experimental Bragg profile (text) | — |
| `<stem>.his6f`, `<stem>.rmc6f`, `<stem>_NN.rmc6f` | configuration after the run; periodic saves | `read_rmc6f` |
| `<stem>.amp`, `<stem>.mamp`, `hkls` | Bragg-module caches reused by the next run | — |
| `<stem>-NN.log` | the program's own log copy (Windows build) | — |
| `<stem>.xml`, `<stem>.xhtml`, `<stem>.cssr`, `<stem>.ylm` | CML output, web summary, visualiser export, harmonics (when requested) | — |
| `*_OUTPUT.dat`, `*_Q_OUTPUT.csv`, `*_R_OUTPUT.csv` | EXAFS k- and R-space output per absorber | — |
