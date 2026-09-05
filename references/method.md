# The method behind the numbers

What the toolkit computes, with the equations it implements and where they
come from. Citations: Keen, *J. Appl. Cryst.* **34** (2001) 172,
doi:10.1107/S0021889800019993 ("A comparison of various commonly used
correlation functions for describing total scattering"); McGreevy & Pusztai,
*Mol. Simul.* **1** (1988) 359, doi:10.1080/08927028808080958; Tucker, Keen,
Dove, Goodwin & Hui, *J. Phys.: Condens. Matter* **19** (2007) 335218,
doi:10.1088/0953-8984/19/33/335218; the RMCProfile manual v6.7.9, Appendix E
("Basic theory of total scattering", p. 141–146).

## 1. Correlation functions (Keen 2001; manual App. E)

For a configuration with atom types *i, j* of concentrations *c_i* and
coherent scattering lengths *b_i* (fm; `NEUTRON_B`, Sears 1992 / NIST),
number density ρ₀ (Å⁻³):

| Function | Definition | Toolkit |
|---|---|---|
| partial pair distribution *g_ij(r)* | number of *j* atoms in a shell *dr* around an *i* atom ÷ (4π r² dr ρ_j); → 1 at large r | `partial_gr(cfg, rmax, dr)` |
| total *G(r)* [barn] | G(r) = Σ_ij c_i c_j b_i b_j (g_ij(r) − 1) (Keen eq. 10; the cross terms counted twice, so the pair weights are *w_ij = (2 − δ_ij) c_i c_j b_i b_j /100*) | `neutron_weights(cfg)`, `total_gr(r, partials, cfg)` |
| *D(r)* | 4π r ρ₀ G(r) | (chapters) |
| *T(r)* | D(r) + 4π r ρ₀ (Σ c_i b_i)² | (chapters) |
| *F(Q)* [barn] | F(Q) = ρ₀ ∫₀^∞ 4π r² G(r) sin(Qr)/(Qr) dr (Keen eq. 12) | `fq_from_gr(r, G, density, q)` |
| *S(Q)*, *i(Q)* | S(Q) = F(Q)/(Σ c_i b_i)² + 1; i(Q) = F(Q) | (chapters) |

**The r → 0 limit.** Every *g_ij* vanishes below the closest approach, so
G(0) = −Σ_ij c_i c_j b_i b_j = −(Σ_i c_i b_i)². For SF6 (c_S = 1/7,
c_F = 6/7, b_S = 2.847 fm, b_F = 5.654 fm) that is −0.2759 barn — exactly
the value at which the package's own SF6 G(r) data file starts. The toolkit
checks this identity in `verify_rmcprofile.py` and in the suite; a G(r) file
whose low-r plateau is not −(Σ c b)² was not normalised the way RMCProfile
expects (manual §4.12 and §5.2: "a peak at very low r is a characteristic
sign of inadequate data correction").

**`DATA_TYPE` / `FIT_TYPE` in the `.dat`.** The data file may hold G(r),
D(r), T(r) in real space or F(Q), S(Q), i(Q) in reciprocal space; RMCProfile
converts to the `FIT_TYPE` before comparing (manual §4.12). D(r) is the
usual choice for fitting because its errors are roughly uniform in r (§5.2);
F(Q) for the same reason in Q (§5.1). `CONVOLVE ::` convolves the
calculated F(Q) with the Fourier transform of a box of width r_max
(the configuration's half-box), which is what the finite box does to the
data (§5.1, Figure 5.1).

## 2. The RMC algorithm (McGreevy–Pusztai 1988; Tucker 2007; manual App. E.3)

1. Start from a configuration (a supercell of the average structure from
   Rietveld refinement, `data2config`; or a previous `.his6f`).
2. Pick an atom at random, displace it by a random vector of length up to
   `MAXIMUM_MOVES` for its type.
3. Reject at once if any distance falls below `MINIMUM_DISTANCES` for the
   pair, or outside a `DISTANCE_WINDOW`, or violates a coordination /
   polyhedral / bond-valence restraint that is set as hard.
4. Update only the histogram bins the move changes; recompute the
   calculated functions for every data set (G(r), F(Q), Bragg profile, EXAFS
   χ(k)); form
   χ² = Σ_datasets Σ_k [calc_k − expt_k]² / σ² with σ = that data set's
   `WEIGHT`, plus the soft-restraint energy terms (potentials, BVS, weighted
   polyhedral restraint).
5. Accept if Δχ² ≤ 0; otherwise accept with probability exp(−Δχ²/2)
   (Metropolis). `TEMPERATURE` in a `POTENTIALS ::` block sets the Boltzmann
   factor for the potential-energy term.
6. Repeat until `TIME_LIMIT`; save every `SAVE_PERIOD` (`.his6f`, CSVs).
   `TIME_LIMIT :: 0` performs the setup, one pass through the functions, the
   χ² report and the save — the package's own smoke test.

The counters in `<stem>.chi2` (`m_accepted`, `m_generated`, `m_tested`) and
the per-data-set χ²/n columns are the run's history; `read_chi2_history`
reads them, `run_rmcprofile` reports the last row.

## 3. What the analysis routines assume

- **Minimum image.** `partial_gr`, `coordination` and `bond_angles` use the
  minimum-image convention on the supercell; `rmax` must stay below half the
  shortest cell edge or the function refuses. RMCProfile itself uses the same
  half-box limit (`r_max` = half the box), which is why `SUPERCELL` sizes in
  the exercises are chosen to reach the r range of the data.
- **The r grid is RMCProfile's.** *g_ij* is tabulated at r_k = k·dr
  (k ≥ 1) with bins centred on r_k, i.e. edges at (k ∓ ½)·dr — the
  convention of `_PDFpartials.csv`. Measured on the package's smoke test
  (2026-09-05): with this grid our partials agree to 2.8e-4 (the package's
  single precision); with plain bin-centre labels they differ by up to 2.9 at
  sharp peaks. `partial_gr(..., grid="centre")` keeps the other convention.
  An ideal-lattice distance lands on a grid point and fills one bin exactly.
- **Weights.** Neutron weights use bound coherent scattering lengths for the
  natural isotopic mixture; isotopically enriched samples (e.g. deuterated,
  `D`) must be entered as their own type. X-ray weights are Q-dependent form
  factors and arrive with the X-ray chapter (`radiation="xray"` raises until
  then).
- **Units.** Å, Å⁻¹, fm for *b*, barn for G(r) and F(Q) (1 barn = 100 fm²),
  Å⁻³ for ρ₀ — the manual's conventions; the `.dat` `NUMBER_DENSITY` and the
  `.rmc6f` header density must agree (RMCProfile prints both and uses the
  configuration's when they differ — seen in the GaPO4 exercise log).
