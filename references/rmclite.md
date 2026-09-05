# rmclite — the teaching engine

`scripts/rmclite.py` is a small, clean-room Reverse Monte Carlo engine written
from the published method (McGreevy & Pusztai, *Mol. Simul.* **1** (1988) 359;
Tucker, Keen, Dove, Goodwin & Hui, *J. Phys.: Condens. Matter* **19** (2007)
335218; correlation functions after Keen, *J. Appl. Cryst.* **34** (2001) 172).
It exists so that the chapters can show what one move, one χ² term, one
constraint *does* on a box the reader can hold in mind. It contains no code
from RMCProfile and makes no claim to its speed or feature set.

## 1. What it is, and is not

| It does | It does not |
|---|---|
| a periodic box of a few hundred to a few thousand atoms (`Box`) | Bragg profiles, EXAFS, magnetic moments, atom swaps |
| single-atom displacement moves of random direction and length ≤ `max_move` per type | resolution, Q-damping or nano-size corrections |
| partial g_ij(r) on RMCProfile's grid (r_k = k·dr, bins centred on r_k), updated incrementally | potentials beyond a harmonic bond term |
| χ² over partial targets, a total Keen G(r) target (barn) and an F(Q) target (direct transform) | X-ray weights (arrive with the X-ray chapter) |
| closest-approach and distance-window constraints, Metropolis acceptance, seeds | cell lists (an O(N) distance row per move is enough at this size) |

Its calculated functions are RMCProfile's by construction: `Histogram` uses
the same grid and normalisation as `rmcprofile_tools.partial_gr`, which the
adapter proves equal to the package's `_PDFpartials.csv` on the shipped
smoke test (max |Δg| = 2.8e-4, single precision in the package;
`tests/test_rmclite_vs_package.py`, `tests/records/crosscheck_v1.json`).

## 2. The algorithm as implemented (`RmcLite.step`)

1. Pick an atom *i* at random; draw a direction from a Gaussian and a length
   uniform in [0, `max_move[type]`]; propose `frac_i' = frac_i + v·L⁻¹` (mod 1).
2. Compute the minimum-image distance row of *i* before and after
   (`Box.distance_row`, O(N)).
3. Constraints: `ClosestApproach` rejects if any new distance of a
   constrained pair is below its minimum; `DistanceWindow` rejects if a pair
   that started inside its window would leave it (members are fixed on first
   use from the starting configuration). A rejected move counts as
   *generated*, not *tested* — RMCProfile's `m_generated` / `m_tested`
   distinction.
4. Trial histogram: subtract the old row's bins, add the new row's (like
   pairs by 2, unlike pairs by 1 — see §3), without touching the current one.
5. χ² = Σ_targets Σ_k (calc_k − target_k)²/σ² on the trial histogram.
6. Acceptance: Δ = ½(χ²_new − χ²_old) + [U_new − U_old]/(k_B T); accept if
   Δ ≤ 0, else with probability e^(−Δ) (Metropolis). The ½ is the RMC
   convention (McGreevy–Pusztai eq. 5); the potential term is the ordinary
   Boltzmann factor with `KB_EV = 8.617333262e-5` eV/K.
7. On acceptance: commit the position, the trial histogram and χ²; record
   `(generated, chi2)` in the history at `print_every` and at the end.

## 3. The incremental histogram

`partial_gr` histograms the full n_a × n_b distance block: an unlike pair
(a, b) is counted once (row a, column b), a like pair twice (both
orderings). Summing every atom's own row counts every pair twice, so
`Histogram.rebuild` halves the unlike counts, and a move changes a like
pair's bins by 2 and an unlike pair's by 1 (`_factor`). The test
`test_histogram_matches_partial_gr_and_updates_incrementally` moves 50 atoms
with `update` and demands bit-equality with a fresh rebuild.

## 4. Targets and what each teaches

- **`PartialTarget`** — the cleanest classroom object: one pair, one curve,
  χ² tells you directly which shell is wrong.
- **`TotalGTarget`** — Keen's G(r) = Σ c_i c_j b_i b_j (g_ij − 1) with
  natural-abundance neutron weights: shows how the weights hide chemistry
  (Ti's negative length, hydrogen's) and why one total function cannot pin
  three partials.
- **`FqTarget`** — F(Q) by direct transform of G(r) over the box's r range:
  shows the ringing a finite box puts into reciprocal space, which is why
  RMCProfile convolves the *data* with the box function (`CONVOLVE ::`)
  rather than the model.

## 5. What the validations found (2026-09-05, `tests/test_rmclite.py`)

- **RMC reproduces the pair distribution, not the coordinates.** Targets
  synthesised from a thermally displaced 2×2×2 NaCl box (s.d. 0.05 Å);
  fit from the ideal lattice: χ² 1.26e6 → 422 in 20 000 moves (2 000 moves
  already give < 1 %), every partial within 1.5 σ on average — while the
  rms distance to the "truth" coordinates went from 0.090 to 0.120 Å. The
  fit found *a* configuration with the target's statistics, not *the*
  configuration. This is the non-uniqueness RMC is known for; the chapters
  make it the first lesson.
- **Delta-sharp targets are pathological.** Fitting the ideal lattice's own
  (unbroadened) partials from a displaced start: 16 % χ² drop in 6 000
  moves. A 0.05 Å move almost never lands in the exact 0.02 Å bin. Real
  data are broadened by thermal motion and resolution; so must be any
  synthetic target.
- **Start from the average structure.** From a random distortion of the
  lattice, χ² fell only 30–45 % in 6 000 moves; from the ideal lattice (what
  `data2config` builds from a Rietveld refinement) it fell four orders of
  magnitude. RMCProfile users start from the average structure for this
  reason.
- **Equipartition.** No data, one harmonic Na–Cl bond (k = 5 eV/Å²,
  r₀ = 2.82 Å) at 300 K, 20 000 moves: the first-shell bond-length variance
  is 0.78 × k_B T/k (0.00405 vs 0.00517 Å²), mean bond 2.828 Å. Each atom
  shares six bonds with three degrees of freedom, so the per-bond variance
  is below the free-oscillator value; the test allows 30 %.
- **Constraints hold exactly**: after 500 moves under closest-approach
  limits no pair is closer than its minimum; after 800 moves under a
  distance window every starting member is still inside it; a seed
  reproduces the run bit for bit.

Throughput on the reference laptop: about 1 900 moves/s for 64 atoms with
three partial targets (pure numpy, one distance row per move).

## 6. How the chapters use it

Chapter 02 (the RMC algorithm) drives `RmcLite` step by step and plots χ²
and the partials as moves accumulate; chapter 09 (analysing configurations)
compares an rmclite fit with an RMCProfile run on the same synthetic data
through the adapter; the course's "constraints as physics" lecture uses the
distance-window and bond-potential objects. The CLI (`synth`, `fit`) writes
RMCProfile-layout files so every reader in `rmcprofile_tools` works on both.
