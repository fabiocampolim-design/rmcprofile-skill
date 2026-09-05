/* SPDX-License-Identifier: Apache-2.0
   Copyright 2026 Fabio Campolim
   rmcprofile-skill course content, English. Strict JSON after the assignment:
   course/tools/build_deck.py, the handout, the lecturer notes and the tests all
   parse it. Figures are named by their provenance key (course/deck/figs); every
   number on a slide is a number a chapter cell printed. */
window.DECK_CONTENT = {
  "lang": "en",
  "deckTitle": "Reverse Monte Carlo with RMCProfile",
  "deckSubtitle": "An undergraduate course in eleven lectures — from the pair distribution function to a refined box",
  "author": "Fabio Campolim",
  "edition": "2026",
  "sections": {
    "welcome": {"name": "Welcome — why local structure", "lecture": "L0", "notebook": "§0–1",
                "summary": "What a crystal's average structure leaves out, what total scattering measures instead, and how this course and its notebooks run."},
    "pdf": {"name": "Scattering and the PDF", "lecture": "L1", "notebook": "§1–4",
            "summary": "Partial pair distribution functions, thermal broadening, Keen's G(r), D(r) and T(r) with their exact limits, and the Fourier route to F(Q)."},
    "mc": {"name": "Monte Carlo and Metropolis", "lecture": "L2", "notebook": "§5–6",
           "summary": "One atom moves, a histogram updates, a chi-squared changes; the Metropolis rule decides — the whole algorithm in one move."},
    "rmc": {"name": "Reverse Monte Carlo", "lecture": "L3", "notebook": "§7–9",
            "summary": "From the average structure to the data: what a fit reproduces (the pair distribution), what it does not (the coordinates), and why constraints are physics."},
    "prep": {"name": "Preparing a run", "lecture": "L4", "notebook": "§10–14",
             "summary": "A unit cell becomes a supercell and an rmc6f file; the .dat keyword file and the checker; synthetic data with a known answer."},
    "fit": {"name": "Fitting with RMCProfile", "lecture": "L5", "notebook": "§15–18",
            "summary": "RMCProfile computes what the toolkit computes; a real refinement of synthetic neutron data; CONVOLVE and the finite box; the same data through rmclite."},
    "constraints": {"name": "Constraints as physics", "lecture": "L6", "notebook": "§23–27",
                    "summary": "Closest approach, distance windows, bond potentials, fixed coordination and bond valence sums — measured on refined boxes."},
    "corrections": {"name": "Corrections", "lecture": "L7", "notebook": "§28–31",
                    "summary": "What the instrument does to G(r) and what RMCProfile does about it — measured, not assumed: the damping is Gaussian, the nanoparticle keyword corrects the baseline."},
    "beyond": {"name": "Beyond neutrons", "lecture": "L8", "notebook": "§19–22, §32–34",
               "summary": "X-ray form factors and contrast, an honest X-ray run, Bragg profiles from a Rietveld refinement, EXAFS on the shipped exercise, magnetic and diffuse fits described."},
    "reading": {"name": "Reading a configuration", "lecture": "L9", "notebook": "§35–38",
                "summary": "A refined box is a statistical object: coordination numbers, bond lengths, bond angles, displacement clouds and ensembles."},
    "contributing": {"name": "Contributing to RMCProfile", "lecture": "L10", "notebook": "§39–40",
                     "summary": "The live cross-check and what it costs, the ecosystem around RMCProfile, and how findings become reports the developers can use."},
    "close": {"name": "Close", "lecture": "", "notebook": "",
              "summary": "Where to go next."}
  },
  "stacks": [
    {"sec": "welcome", "slides": ["welcome-title", "welcome-why", "welcome-syllabus", "welcome-how", "welcome-math"]},
    {"sec": "pdf", "slides": ["pdf-partials", "pdf-thermal", "pdf-keen", "pdf-fq", "pdf-math"]},
    {"sec": "mc", "slides": ["mc-onemove", "mc-chi2", "mc-code", "mc-math"]},
    {"sec": "rmc", "slides": ["rmc-fit", "rmc-recover", "rmc-constraints", "rmc-math"]},
    {"sec": "prep", "slides": ["prep-supercell", "prep-fold", "prep-dat", "prep-checker", "prep-math"]},
    {"sec": "fit", "slides": ["fit-onepass", "fit-refine", "fit-convolve", "fit-rmclite", "fit-math"]},
    {"sec": "constraints", "slides": ["con-why", "con-mindist", "con-windows", "con-bvs", "con-math"]},
    {"sec": "corrections", "slides": ["cor-instrument", "cor-measured", "cor-damped", "cor-broad", "cor-nano", "cor-math"]},
    {"sec": "beyond", "slides": ["bey-formfactor", "bey-contrast", "bey-xrayrun", "bey-bragg", "bey-exafs", "bey-magnetic", "bey-math"]},
    {"sec": "reading", "slides": ["rd-statistical", "rd-coordination", "rd-angles", "rd-ensembles", "rd-math"]},
    {"sec": "contributing", "slides": ["ctr-crosscheck", "ctr-ecosystem", "ctr-how", "ctr-math"]},
    {"sec": "close", "slides": ["close-next"]}
  ],
  "slides": {
    "welcome-title": {
      "level": "intro", "layout": "hero",
      "kicker": "rmcprofile-skill · undergraduate course",
      "title": "Reverse Monte Carlo with RMCProfile",
      "sub": "From the pair distribution function to a refined box in eleven lectures — every figure computed live in the companion notebooks",
      "notes": "Set the contract on the first slide: nothing in this course is a cartoon. Every plot was produced by a cell of the companion chapter notebooks (chapters/) and can be re-run by the students; the numbers on the slides are the numbers those cells printed. The course assumes first-year mechanics and statistics (a histogram, a Gaussian, a Fourier transform seen once) and nothing about crystallography. Q: \"Do I need RMCProfile installed?\" A: Not for lectures 0–4 and 9: the notebooks carry their own reverse Monte Carlo engine, rmclite. Lectures 5–8 and 10 run the real program; without it those cells skip and say so."
    },
    "welcome-why": {
      "level": "intro", "layout": "text",
      "title": "Why local structure?",
      "lead": "A crystal structure is an <strong>average</strong>: one position per site, one displacement ellipsoid. Real materials disorder, tilt, hop and vibrate — and their properties live in that difference.",
      "bullets": [
        "Bragg peaks see the average unit cell; the diffuse scattering between them sees the deviations.",
        "Total scattering keeps both and Fourier-transforms them into the <strong>pair distribution function</strong>: how many atom pairs sit at each distance.",
        "Reverse Monte Carlo builds a box of thousands of atoms whose pair distribution matches the data — a picture of the disorder, not a parameter.",
        "RMCProfile is the program that does this for crystals, fitting G(r), F(Q) and the Bragg profile at once."
      ],
      "notes": "Give the contrast early: Rietveld refinement fits a handful of parameters of the average cell; RMC fits thousands of coordinates against the same data plus the diffuse part. Ask what a 'disordered crystal' could mean — a lead titanate with off-centred Pb, a spin glass, a nanoparticle. Q: \"If the box has thousands of coordinates, is the answer unique?\" A: No, and lecture 3 makes that the central lesson: the fit reproduces distributions, never a particular atom's position."
    },
    "welcome-syllabus": {
      "level": "intro", "layout": "syllabus",
      "title": "Eleven lectures",
      "lead": "Each lecture is one run of slides: a picture first, the physics next, the equations last. Notebook sections are given for every lecture.",
      "notes": "Walk the syllabus once. Three arcs: lectures 1–3 build the method with the notebooks' own engine (what is measured, how a move is accepted, what a fit means); lectures 4–8 run RMCProfile on synthetic data whose answer is known, one data type at a time; lectures 9–10 turn to what one reads off a box and how to talk to the program's developers. Q: \"Which lectures can be skipped?\" A: 7 and 8 are enrichment; 0–6 and 9 form the spine."
    },
    "welcome-how": {
      "level": "core", "layout": "text",
      "title": "How each lecture is built",
      "lead": "The deck is flat and linear: <strong>→</strong> is the only key you need. Every lecture opens with a divider and runs from its simplest slide to its most mathematical.",
      "bullets": [
        "<span class='c-3'>intro</span> slides: one figure, plain language, at most the symbols <span class='math'>r</span> and <span class='math'>Q</span>.",
        "<span class='c-1'>core</span> slides: the physics and how the toolkit or RMCProfile computes it (which function, which keyword).",
        "<span class='c-violet'>math</span> slides: the formulas behind the figures, with the derivation sketched in the lecturer notes.",
        "To run the notebooks: create the <code>rmcprofile</code> environment (<code>environment-rmcprofile.yml</code>), open <code>chapters/README.md</code>, start with chapter 0; every chapter ends with exercises and worked solutions.",
        "Speaker view: <code>S</code>. Next lecture: <code>Shift+→</code>. Overview: <code>Esc</code>."
      ],
      "notes": "This slide is for the lecturer as much as for the students: the level chip at the top-right of every slide says where you are, so a first-year audience stops after the core slides and a fourth-year audience goes on to the equations. Q: \"Where are the exercises?\" A: At the end of every chapter notebook, with worked solutions in the cell that follows; the handout lists which sections each lecture draws on."
    },
    "welcome-math": {
      "level": "math", "layout": "eq",
      "title": "The one function of the course",
      "lead": "Everything that follows is a way to compute, measure or fit Keen's total pair distribution function of a box of atoms.",
      "eqs": [
        {"label": "partial pair distribution", "math": "<span class='math'>g<sub>ij</sub>(r) = n<sub>ij</sub>(r) / ( 4π r<sup>2</sup> ρ c<sub>j</sub> Δr )</span>"},
        {"label": "Keen's G(r), in barn", "math": "<span class='math'>G(r) = Σ<sub>ij</sub> c<sub>i</sub> c<sub>j</sub> b<sub>i</sub> b<sub>j</sub> [ g<sub>ij</sub>(r) − 1 ]</span>"},
        {"label": "its exact limit", "math": "<span class='math'>G(r → 0) = − ( Σ<sub>i</sub> c<sub>i</sub> b<sub>i</sub> )<sup>2</sup></span>"}
      ],
      "bullets": [
        "<span class='math'>n<sub>ij</sub>(r)</span>: pairs of type <span class='math'>i</span>–<span class='math'>j</span> in the shell at <span class='math'>r</span>; <span class='math'>ρ</span>: number density; <span class='math'>c</span>: concentrations; <span class='math'>b</span>: neutron scattering lengths.",
        "The limit is a checkable number: for SF<sub>6</sub> the notebooks' weights give −0.2759 barn, the value at which the package's own G(r) data file starts.",
        "RMCProfile's grid is <span class='math'>r<sub>k</sub> = k·Δr</span> with bins centred on <span class='math'>r<sub>k</sub></span>; on it the notebooks' partials equal the program's to 2.8×10<sup>−4</sup>."
      ],
      "notes": "Derive the limit on the board: below the closest approach every g_ij is zero, so G = −Σ c_i c_j b_i b_j = −(Σ c b)². Stress that this is not a fit parameter but an identity, and that chapter 1 checks it to 1e-12 on a synthetic box while chapter 10 checks the package's file against it. Q: \"Why barn?\" A: b is in femtometres; b_i b_j in fm² is 0.01 barn — Keen's convention keeps G(r) in the same units as a cross-section, which is what the data reduction produces."
    },

    "pdf-partials": {
      "level": "intro", "layout": "fig", "fig": "s01-f1",
      "title": "Counting pairs at each distance",
      "lead": "Take a box of atoms, measure every pair distance, sort them into bins: the partial pair distribution functions. On an ideal NaCl lattice they are spikes at the shell distances.",
      "notes": "Read the figure aloud: the first Na–Cl spike at 2.82 Å is the bond; the Na–Na and Cl–Cl spikes at 3.99 Å are the second shell, twelve neighbours each. The heights are set by the shell multiplicity divided by 4πr²ρ, which is why far shells look smaller although they hold more atoms. Q: \"Why divide by 4πr²?\" A: A uniform gas would put pairs in a shell in proportion to its volume; dividing by that makes g = 1 the 'no structure' reference and g − 1 the structure."
    },
    "pdf-thermal": {
      "level": "core", "layout": "fig-right", "fig": "s02-f1",
      "title": "Thermal motion broadens the peaks",
      "lead": "Displace every atom by a Gaussian of 0.05 Å and the spikes become peaks whose width is the pair's relative displacement — this is what a real material's PDF looks like.",
      "bullets": [
        "The peak <em>area</em> is conserved: the shell still holds six neighbours.",
        "The width of a pair peak is √2 times a single atom's displacement when the two move independently — correlated motion narrows it.",
        "The notebooks' 'truth box' for every later lecture is exactly this: an ideal lattice plus 0.05 Å Gaussian displacements, seed 0."
      ],
      "notes": "This is the moment to say what a synthetic experiment is: we know the atoms, we compute the PDF, and later we ask the fit to recover what we already know. A real measurement never gives that luxury, which is why the course builds its intuition here. Q: \"Is 0.05 Å realistic?\" A: Room-temperature displacement parameters of ionic crystals give root-mean-square displacements of 0.1–0.2 Å; 0.05 Å is a cold, well-behaved crystal chosen so that the shells stay separate."
    },
    "pdf-keen": {
      "level": "core", "layout": "fig", "fig": "s03-f1",
      "title": "Keen's total functions: G(r), D(r), T(r)",
      "lead": "The partials are weighted by concentrations and scattering lengths into one measurable function. Three conventions differ by factors of r; each has an exact limit the notebook checks.",
      "notes": "Keen (2001) is the reference: G(r) tends to −(Σcb)² at r → 0 and to 0 at large r; D(r) = 4πrρG(r) is what PDFgui calls G(r) and starts at zero with slope −4πρ(Σcb)²; T(r) = D(r) + 4πrρ(Σcb)² is positive and vanishes at the origin. RMCProfile's DATA_TYPE keyword accepts each. Q: \"Which one should I fit?\" A: Whichever your reduction produced — the fit is the same physics; but tell RMCProfile which, because the baseline and the weighting differ."
    },
    "pdf-fq": {
      "level": "core", "layout": "fig", "fig": "s04-f1",
      "title": "Into reciprocal space: F(Q) and the box's ringing",
      "lead": "The same box in reciprocal space: Faber–Ziman partials S<sub>ij</sub>(Q) − 1 by a sine transform of g<sub>ij</sub> − 1, and their weighted sum F(Q). A finite box rings.",
      "notes": "Two points to make with the figure: F(Q) computed from the partials equals the direct transform of G(r) — the notebook checks the two routes agree — and a transform truncated at half the box edge produces oscillations of period 2π/r_max. RMCProfile handles the truncation by convolving the calculated F(Q) with the box function (CONVOLVE ::), lecture 5. Q: \"Why does F(Q) not go to zero at high Q?\" A: It does, slowly: the thermal Gaussian in r becomes a Gaussian envelope in Q; with 0.05 Å displacements the decay is gentle over 25 Å⁻¹."
    },
    "pdf-math": {
      "level": "math", "layout": "eq",
      "title": "The transforms",
      "lead": "Real space and reciprocal space are one function seen twice; the box makes the transform finite.",
      "eqs": [
        {"label": "Faber–Ziman partial", "math": "<span class='math'>S<sub>ij</sub>(Q) − 1 = 4π ρ ∫<sub>0</sub><sup>r<sub>max</sub></sup> r<sup>2</sup> [ g<sub>ij</sub>(r) − 1 ] <span class='fn'>sin</span>(Qr)/(Qr) dr</span>"},
        {"label": "total scattering", "math": "<span class='math'>F(Q) = Σ<sub>ij</sub> c<sub>i</sub> c<sub>j</sub> b<sub>i</sub> b<sub>j</sub> [ S<sub>ij</sub>(Q) − 1 ]</span>"},
        {"label": "the other conventions", "math": "<span class='math'>D(r) = 4π r ρ G(r), &nbsp; T(r) = D(r) + 4π r ρ ( Σ c b )<sup>2</sup></span>"}
      ],
      "bullets": [
        "The integral stops at <span class='math'>r<sub>max</sub></span> ≤ half the box edge: the minimum-image convention has no pairs beyond it.",
        "Truncation is a multiplication by a box in <span class='math'>r</span>, hence a convolution by a sinc in <span class='math'>Q</span> — the ringing of the figure.",
        "The notebooks' <code>fq_from_gr</code> and <code>total_fq_from_partials</code> are these two lines; the check is that they agree."
      ],
      "notes": "Derive the sine kernel from the 3D Fourier transform of a spherically symmetric function: the angular integral of exp(iQ·r) gives sin(Qr)/(Qr). Note the factor ρ: the transform is of the pair density, not of g alone. Q: \"What sets Q_max in an experiment?\" A: The instrument: neutron time-of-flight diffractometers reach 30–50 Å⁻¹, laboratory X-rays 10–20; lower Q_max means broader peaks in r, lecture 7's business."
    },

    "mc-onemove": {
      "level": "intro", "layout": "text",
      "title": "One move, by hand",
      "lead": "Pick one atom. Displace it by a random amount up to a maximum. Recount only the pairs that atom belongs to. Compare the new histogram with the target. Keep or undo.",
      "bullets": [
        "Nothing else changes: an <em>incremental</em> histogram update touches one row of distances, which is why a move costs microseconds.",
        "The notebooks' engine <code>rmclite</code> checks that the incremental histogram stays bit-equal to a full rebuild.",
        "A closest-approach constraint can refuse the move before any histogram is touched."
      ],
      "notes": "Do it literally on the board with five atoms and a two-bin histogram: move one, cross out the old distances, write the new ones. Students who see the bookkeeping once never mistake RMC for a black box. Q: \"How large is a move?\" A: A fraction of the bond length, set per atom type by MAXIMUM_MOVES; chapter 2's exercise measures that 0.3 Å converges as well as 0.05 Å on NaCl, while 0.01 Å is slow — lecture 3 quotes it."
    },
    "mc-chi2": {
      "level": "core", "layout": "text",
      "title": "χ² and the acceptance rule",
      "lead": "The distance between the calculated and the target function is a sum of squared residuals over bins, each divided by an uncertainty σ. A move that lowers χ² is always kept; one that raises it is kept sometimes.",
      "bullets": [
        "The 'sometimes' is Metropolis: with probability exp(−Δχ²/2). It lets the box climb out of local minima and gives the box a temperature.",
        "σ is the knob that sets how far the data pull: a small σ makes every wiggle of the target — including its noise — a mandatory feature.",
        "Several data sets add their χ² terms with weights; constraints and potentials add terms of their own, exactly as RMCProfile's chi2 file lists them."
      ],
      "notes": "Connect to statistical mechanics: exp(−Δχ²/2) is a Boltzmann factor with χ²/2 playing the energy at k_BT = 1. RMCProfile's log prints χ²/dof per data set and a total; the notebooks read the same columns from the .chi2 file. Q: \"What if σ is too small?\" A: The box fits the noise and the coordinates go wild while χ² stays high; chapter 2's lesson is never to fit unbroadened, delta-sharp targets — always give the target a width."
    },
    "mc-code": {
      "level": "core", "layout": "code",
      "title": "The engine in six lines: <code>rmclite</code>",
      "lead": "The notebooks' own reverse Monte Carlo engine reuses the toolkit's grid and normalisation, so what it fits is exactly what RMCProfile tabulates.",
      "code": "import rmclite as rl\n\nbox = rl.Box.from_rmc6f(cfg)                       # the average structure, from an rmc6f\ntargets = [rl.PartialTarget(lab, r, g_truth[lab], sigma=0.2) for lab in g_truth]\nengine = rl.RmcLite(box, rmax=8.0, dr=0.02, targets=targets,\n                    constraints=[rl.ClosestApproach({\"Na-Na\": 3.0, \"Na-Cl\": 2.2, \"Cl-Cl\": 3.0})],\n                    max_move={\"Na\": 0.05, \"Cl\": 0.05}, seed=1)\nengine.run(6000)                                    # chi2 falls by more than 95 %",
      "bullets": [
        "<code>Box</code>: fractional coordinates and the lattice; <code>Histogram</code>: the incremental pair count on RMCProfile's grid.",
        "Targets: <code>PartialTarget</code>, <code>TotalGTarget</code>, <code>FqTarget</code>; constraints: <code>ClosestApproach</code>, <code>DistanceWindow</code>; a <code>BondPotential</code> adds ΔU/k<sub>B</sub>T to the rule.",
        "About 1 900 moves per second on 64 atoms in pure numpy — RMCProfile does ten times more with a G(r) data set, and the point of rmclite is to be read, not to be fast."
      ],
      "notes": "Show the code and ask what each argument is before running it. The API mirrors RMCProfile's keywords on purpose (MINIMUM_DISTANCES, MAXIMUM_MOVES, WEIGHT) so that chapter 4's .dat file reads as the same recipe. Q: \"Is rmclite RMCProfile?\" A: No — it is a clean-room teaching engine with none of the program's code; the cross-check of lecture 10 shows the two compute the same functions from the same box."
    },
    "mc-math": {
      "level": "math", "layout": "eq",
      "title": "Metropolis, with a temperature",
      "lead": "The acceptance rule is one inequality; a potential energy enters it on the same footing as the data.",
      "eqs": [
        {"label": "chi-squared", "math": "<span class='math'>χ<sup>2</sup> = Σ<sub>data</sub> Σ<sub>k</sub> [ f<sub>calc</sub>(r<sub>k</sub>) − f<sub>data</sub>(r<sub>k</sub>) ]<sup>2</sup> / σ<sup>2</sup></span>"},
        {"label": "the decision", "math": "<span class='math'>Δ = Δχ<sup>2</sup>/2 + ΔU/k<sub>B</sub>T, &nbsp; accept if Δ ≤ 0, else with probability e<sup>−Δ</sup></span>"},
        {"label": "harmonic bond term", "math": "<span class='math'>U = ½ k ( d − d<sub>0</sub> )<sup>2</sup></span>"}
      ],
      "bullets": [
        "With no data at all the rule samples the Boltzmann distribution of <span class='math'>U</span>: rmclite's test lets a harmonic bond thermalise to ⟨U⟩ = 0.78 k<sub>B</sub>T/k, the equipartition check.",
        "RMCProfile's <code>POTENTIALS ::</code> block (STRETCH, TEMPERATURE) is this term with <span class='math'>k</span> in eV/Å² and <span class='math'>T</span> in kelvin.",
        "The factor ½ on Δχ² is the convention of the original RMC papers (McGreevy & Pusztai 1988) and of RMCProfile."
      ],
      "notes": "Derive detailed balance in two lines for the data-free case: the ratio of forward and backward acceptance probabilities equals exp(−ΔU/kT), so the stationary distribution is Boltzmann's. Then add χ²/2 as an extra 'energy' and note that the data term has no temperature of its own — σ plays that role. Q: \"Why 0.78 and not 0.5?\" A: The test measures ⟨U⟩ in units of k_BT/k over a finite run with a hard closest-approach wall that truncates the Gaussian; equipartition's ½ k_BT is the untruncated limit."
    },

    "rmc-fit": {
      "level": "intro", "layout": "fig", "fig": "s07-f1",
      "title": "From the average structure to the data",
      "lead": "Start rmclite on the ideal NaCl lattice with the thermal box's partials as targets: the spikes broaden into the target peaks and χ² falls by four orders of magnitude.",
      "notes": "Read the figure as a before/after: the starting partials are the spikes of lecture 1, the fitted ones lie on the target within the noise of 216 atoms. Say where the moves went — into random displacements whose statistics match the target's width — and where they did not go: into the particular displacements of the truth box. Q: \"How long does this take?\" A: 6 000 moves, a few seconds in the notebook; RMCProfile makes the same number of moves in well under a second on this box."
    },
    "rmc-recover": {
      "level": "core", "layout": "text",
      "title": "What RMC does and does not recover",
      "lead": "The fit reproduces the <strong>pair distribution</strong>; it does not recover the <strong>coordinates</strong>. The residual against the target is as small as that of a second, independent thermal realisation — and the atoms are not where the truth put them.",
      "bullets": [
        "Chapter 2 measures it: the fitted box's partials deviate from the target no more than a fresh random realisation's; the fitted displacements are uncorrelated with the truth's.",
        "So read a refined box for its <em>distributions</em> — bond lengths, angles, coordination, displacement clouds (lecture 9) — never for atom 137.",
        "Starting point matters: start from the average structure; a random start converges to a different, equally good, box.",
        "Move size: 0.3 Å converges as well as 0.05 Å on NaCl; 0.01 Å is slow. The notebook's exercise has the numbers."
      ],
      "notes": "This is the lecture's thesis and the one thing to carry out of the course. Anticipate the objection that this makes RMC useless: it does not — a thousand distributions read off a box are a thousand more than a Rietveld fit gives; what one must not do is publish a picture of a box as if it were a structure. Q: \"Can two very different boxes fit equally well?\" A: Yes, whenever the data do not distinguish them; that is precisely why lecture 6 adds chemistry as constraints, and why lecture 9 averages an ensemble of fits."
    },
    "rmc-constraints": {
      "level": "core", "layout": "text",
      "title": "Constraints are physics",
      "lead": "A pair distribution constrains distances, not chemistry. A closest approach, a distance window, a coordination number or a bond potential is physics the data cannot say and the fit needs.",
      "bullets": [
        "Without a closest approach two atoms can overlap and still fit a broad peak; with one, every move is checked before the histogram is touched.",
        "Chapter 2's constrained fit against the same targets converges to a box whose Na–Cl distances never fall below 2.2 Å; the unconstrained one wanders.",
        "RMCProfile carries the same ideas as keywords — MINIMUM_DISTANCES, DISTANCE_WINDOW, POTENTIALS, FIXED_COORDINATION_CONSTRAINTS, BVS — lecture 6 measures each on a refined box."
      ],
      "notes": "Give the chemist's view: a bond is not a distance but a topology; a molecule that fits the PDF with the wrong connectivity is wrong. RMC has no notion of a bond unless told. Q: \"Are constraints cheating?\" A: They are prior knowledge, stated explicitly in the input file, which is more honest than the implicit priors of a parametrised model; the test is whether the fit still needs them once the data are good."
    },
    "rmc-math": {
      "level": "math", "layout": "eq",
      "title": "Why the coordinates are not recoverable",
      "lead": "The data fix pair statistics; a permutation of displacements with the same pair statistics fits as well.",
      "eqs": [
        {"label": "what the target fixes", "math": "<span class='math'>g<sub>ij</sub>(r) ∝ Σ<sub>pairs</sub> δ( r − | r<sub>a</sub> − r<sub>b</sub> | )</span>"},
        {"label": "a symmetry of the fit", "math": "<span class='math'>{ u<sub>a</sub> } → { u<sub>π(a)</sub> }  &nbsp;<span class='fn'>for any</span> π <span class='fn'>that preserves the shell statistics</span></span>"},
        {"label": "the honest residual", "math": "<span class='math'>rms( g<sub>fit</sub> − g<sub>target</sub> ) ≈ rms( g<sub>realisation 2</sub> − g<sub>target</sub> )</span>"}
      ],
      "bullets": [
        "The number of coordinates (3N) vastly exceeds the number of independent bins, and the bins are sums over all pairs.",
        "Chapter 2 measures the third line: the fit's residual against the target equals a second thermal realisation's within noise.",
        "The consequence for lecture 9: report distributions with the ensemble spread as the error bar."
      ],
      "notes": "Sketch the counting argument: 216 atoms give 648 coordinates; a partial on a 0.02 Å grid to 8 Å has 400 bins, of which most are empty or noise; three partials give perhaps a hundred informative numbers. Then show that swapping the displacements of two Na atoms that see identical shells leaves every pair distance histogram unchanged. Q: \"Does adding F(Q) or Bragg data help?\" A: They constrain the same statistics differently (Bragg fixes the average cell and the mean-square displacement); they do not label atoms."
    },

    "prep-supercell": {
      "level": "intro", "layout": "text",
      "title": "From a unit cell to a supercell",
      "lead": "RMCProfile needs a box: a cell, a list of sites with fractional coordinates, and how many times to repeat it. The toolkit's <code>build_configuration</code> turns a crystallographic description into an rmc6f file.",
      "bullets": [
        "NaCl: a = 5.64 Å, four Na and four Cl sites; 3 × 3 × 3 cells give 216 atoms in a 16.92 Å box.",
        "The rmc6f file carries the cell, the atom types in a fixed order, and each atom's fractional position with its site and cell indices — the program writes the same layout back.",
        "Bigger boxes give smoother partials and longer <span class='math'>r<sub>max</sub></span>; the shipped SF<sub>6</sub> exercise uses 4 320 atoms."
      ],
      "notes": "Show the file on screen if you can: the header, the ATOMS line, then rows. Point at the two atom-line layouts the program accepts (with and without the [1] token) — the toolkit reads both because the program writes one and the tutorials ship the other. Q: \"How big should my box be?\" A: Large enough that r_max = half the box edge exceeds the range you fit, and that the shells you care about hold hundreds of pairs; 10–20 Å boxes with thousands of atoms are typical."
    },
    "prep-fold": {
      "level": "core", "layout": "fig-right", "fig": "s12-f1",
      "title": "Folding back, averaging, exporting",
      "lead": "Fold every atom of the supercell into one unit cell and the displacement clouds of the sites appear; average the folded positions and the unit cell is back. Export to XYZ or CIF for any viewer.",
      "bullets": [
        "<code>fold_to_unit_cell</code>, <code>average_cell</code>, <code>export_xyz</code>, <code>export_cif</code> — all on the rmc6f object.",
        "The CIF's cell is the supercell (16.92 Å); the average cell is the unit cell (5.64 Å): chapter 9's exercise checks both.",
        "Fold-back is the bridge between an RMC box and a crystallographer's picture."
      ],
      "notes": "Explain why the picture on the right is the right way to look at a box: 27 copies of each site collapse onto one cloud whose shape is the site's displacement distribution, exactly what a displacement ellipsoid summarises with three numbers. Q: \"Can I refine the cell parameters too?\" A: RMCProfile keeps the box fixed during a run; the Bragg profile fit (lecture 8) is what carries the lattice information, and the box is set up to match it."
    },
    "prep-dat": {
      "level": "core", "layout": "code",
      "title": "The .dat file: keywords, blocks, flags",
      "lead": "One text file drives a run: scalars, data blocks with subordinate keywords, and bare flags. The toolkit writes a complete synthetic set in one call and keeps the three keyword forms apart.",
      "code": "rt.write_input_set(\"nacl\", workdir, cfg, gr=(r, G_data),\n                   min_dist={\"Na-Na\": 3.0, \"Na-Cl\": 2.2, \"Cl-Cl\": 3.0},\n                   max_move=0.05, time_limit_min=0.5)\n\n# the file it writes (excerpt)\n#   MINIMUM_DISTANCES :: 3.0 2.2 3.0\n#   NEUTRON_REAL_SPACE_DATA :: 1\n#     > FILENAME :: nacl_gr.dat\n#     > DATA_TYPE :: G(r)\n#     > CONVOLVE ::            <- a keyword with an empty value\n#     > NO_FITTED_OFFSET       <- a bare flag\n#   IGNORE_HISTORY_FILE ::",
      "bullets": [
        "<code>&gt; KEY :: value</code>, <code>&gt; KEY ::</code> and <code>&gt; KEY</code> are three different things to the program; a writer that drops the <code>::</code> of CONVOLVE silently disables the convolution (finding P-16).",
        "<code>IGNORE_HISTORY_FILE ::</code> is on by default: a <code>.his6f</code> left by a zero-move pass poisons the next run (P-15).",
        "MINIMUM_DISTANCES lists pairs in the order AA AB AC BB BC CC; the checker counts them."
      ],
      "notes": "Walk through the excerpt line by line and name the block structure: a top-level keyword with '::', subordinate keywords prefixed by '>', END. The two findings on the slide are real: each cost a run before the notebooks caught it, and each has a guard in the toolkit now. Q: \"Where do the weights come from?\" A: WEIGHT is 1/σ² per data set in the program's convention; the toolkit's default 0.05 for G(r) and 0.01 for F(Q) reproduce the shipped exercises' balance."
    },
    "prep-checker": {
      "level": "core", "layout": "table",
      "title": "Check before you run",
      "lead": "RMCProfile stops on a missing file with exit code 0 and waits forever for a missing .poly file. The toolkit's checker reports the mistakes the manual warns about — and the ones it does not — before the binary starts.",
      "table": {
        "head": ["code", "level", "what it catches"],
        "rows": [
          ["no-configuration", "ERROR", "no rmc6f / his6f / cfg — the program would stop with exit code 0 (P-11)"],
          ["minimum-distances-count", "ERROR", "wrong number of values for the pairs AA AB AC BB BC CC"],
          ["poly-file-missing", "ERROR", "POLYHEDRAL_RESTRAINT without its .poly — the program waits indefinitely (P-12)"],
          ["bulk-rho-missing", "ERROR", "PARTICLE_RADIUS without BULK_RHO — the program stops (P-18)"],
          ["filename-case", "WARN", "a data file that exists only with different letter case — fine on Windows, a stop on Linux (P-10)"],
          ["history-file", "WARN", "a .his6f will be read instead of the rmc6f; one from a zero-move pass makes the run crawl (P-15)"],
          ["stale-neighbour-files", "WARN", "a .neigh from a previous configuration"]
        ]
      },
      "notes": "Each row is a finding from running the shipped exercises on both builds, with a reproduction in the study repository's ledger. The exit-code-0 stop is the one that bites scripts: a pipeline sees success and no output. Q: \"Does the checker validate the physics?\" A: No — it validates the set: files present, counts right, keywords in the forms the program reads. Whether MINIMUM_DISTANCES are sensible is lecture 6."
    },
    "prep-math": {
      "level": "math", "layout": "eq",
      "title": "Synthetic data with a known answer",
      "lead": "The course's experiments are built so that the truth is known and the fit's success is measurable.",
      "eqs": [
        {"label": "truth box", "math": "<span class='math'>x<sub>a</sub> = x<sub>a</sub><sup>ideal</sup> + u<sub>a</sub>, &nbsp; u<sub>a</sub> ~ N(0, 0.05 Å) <span class='fn'>per Cartesian component, seed 0</span></span>"},
        {"label": "data", "math": "<span class='math'>G<sub>data</sub>(r<sub>k</sub>) = G<sub>truth</sub>(r<sub>k</sub>) + N(0, 0.003 barn)</span>"},
        {"label": "grid", "math": "<span class='math'>r<sub>k</sub> = k·Δr, &nbsp; Δr = 0.02 Å, &nbsp; r<sub>max</sub> = 8 Å &lt; L/2 = 8.46 Å</span>"}
      ],
      "bullets": [
        "The data file is written in RMCProfile's two-line-header layout; the program reads it back exactly (the experiment column returns our numbers to 10<sup>−4</sup>).",
        "Thresholds in the notebooks are stated relative to the noise — 'below ten times the noise' — never tuned to pass.",
        "Every later lecture reuses this box; when a lecture evaluates a keyword it uses the truth box itself as the model, so only the keyword can differ."
      ],
      "notes": "Explain the design choice on the third bullet: chapter 7's first version compared the ideal lattice with damped data and every damping 'improved' the fit because the sharp peaks shrank — the lesson was to make the model the truth so that the only difference is the correction under test. Q: \"Why noise of 0.003 barn?\" A: About 1 % of the Na–Cl peak height of the thermal G(r); real reduced data are noisier at high r, which chapter 4's thresholds anticipate."
    },

    "fit-onepass": {
      "level": "intro", "layout": "fig", "fig": "s15-f1",
      "title": "One pass: RMCProfile computes what we compute",
      "lead": "Run the program with TIME_LIMIT 0 on the ideal lattice against the synthetic data: no moves, one evaluation. Its calculated G(r) is the toolkit's, and its experiment column is our data.",
      "notes": "The point of a zero-move pass is that it is deterministic: the same inputs give the same columns on both builds, which makes it the unit of every comparison in lectures 5–8. The figure shows RMCProfile's PDF1 columns against the toolkit's function of the same box. Q: \"What is chi2 here?\" A: The residual of the ideal lattice against thermal data — large, as it should be; lecture 7 uses this number as a baseline."
    },
    "fit-refine": {
      "level": "core", "layout": "fig", "fig": "s16-f1",
      "title": "The refinement",
      "lead": "Half a minute of moves on the CUDA build: tens of thousands of moves, χ² from ten thousand to order ten, and the calculated G(r) on the data within the noise.",
      "notes": "Name what the program printed: moves generated, tested, accepted, the χ² per data set and the total, saved at the end because SAVE_PERIOD equals the time limit. Then look at the box: thermal-width peaks, coordination intact. Q: \"Why does the log print 'Time per generated move'?\" A: RMCProfile's clock is wall time — TIME_LIMIT and SAVE_PERIOD are minutes, not moves — so the number of moves a run makes depends on the machine; the notebooks quote both."
    },
    "fit-convolve": {
      "level": "core", "layout": "fig-right", "fig": "s17-f1",
      "title": "<code>CONVOLVE ::</code> and the finite box",
      "lead": "A reciprocal-space fit against F(Q) must account for the box: RMCProfile convolves its calculated F(Q) with the box function. The keyword's empty value is not optional.",
      "bullets": [
        "With CONVOLVE the calculated F(Q) carries the same ringing as data transformed from a finite r range; without it the fit chases the ripples.",
        "The experiment column of the output is the data <em>convolved</em> when CONVOLVE is on — compare like with like.",
        "A constant offset (CONSTANT_OFFSET) is the other reciprocal-space knob; the notebook compares runs with and without it."
      ],
      "notes": "This is where the lecturer explains why fitting both G(r) and F(Q) is common practice: G(r) fixes the short-range shells, F(Q) with the convolution handles the truncation honestly and adds the high-Q information the transform smears. Q: \"Why is the keyword's value empty?\" A: It is a switch written as a keyword with '::' and nothing after it — the program's own tutorial files write it so; a writer that drops the '::' turns it off silently (P-16)."
    },
    "fit-rmclite": {
      "level": "core", "layout": "fig-right", "fig": "s18-f1",
      "title": "The same data through rmclite",
      "lead": "Feed the same synthetic G(r) to the notebooks' engine: it converges to the same pair distribution, slower and in the open — every step readable.",
      "bullets": [
        "Same grid, same weights, same closest approach: the two engines are compared on their calculated functions, not on their boxes.",
        "rmclite's fit from the ideal lattice cuts χ² by four orders of magnitude on a total G(r) target as it did on partials.",
        "What differs is speed and features — RMCProfile fits Bragg profiles, EXAFS and magnetic data; rmclite fits pair functions and teaches."
      ],
      "notes": "Use the slide to summarise the relationship between the two engines once and for all: rmclite is the executable derivation of what RMCProfile does for pair distribution functions; it is not a substitute for it. Q: \"Could I publish with rmclite?\" A: You could publish a method study; for a material, use RMCProfile — the cross-check of lecture 10 tells you what the two agree on and to what precision."
    },
    "fit-math": {
      "level": "math", "layout": "eq",
      "title": "The box function",
      "lead": "Truncating the transform at r<sub>max</sub> is a multiplication in r and a convolution in Q; the fit must apply the same operation to the model.",
      "eqs": [
        {"label": "truncated transform", "math": "<span class='math'>F<sub>box</sub>(Q) = ∫ F(Q′) M(Q − Q′) dQ′, &nbsp; M(Q) = (1/π) ∫<sub>0</sub><sup>r<sub>max</sub></sup> <span class='fn'>cos</span>(Qr) dr = <span class='fn'>sin</span>(Q r<sub>max</sub>) / (π Q)</span>"},
        {"label": "what CONVOLVE does", "math": "<span class='math'>F<sub>calc</sub> → F<sub>calc</sub> ⊗ M, &nbsp; F<sub>data</sub> → F<sub>data</sub> ⊗ M</span>"},
        {"label": "the fitted quantity", "math": "<span class='math'>χ<sup>2</sup><sub>F</sub> = Σ<sub>Q</sub> [ (F<sub>calc</sub> ⊗ M)(Q) − (F<sub>data</sub> ⊗ M)(Q) ]<sup>2</sup> / σ<sup>2</sup></span>"}
      ],
      "bullets": [
        "The ripples of lecture 1's figure have period <span class='math'>2π/r<sub>max</sub></span>: 0.74 Å⁻¹ for an 8.46 Å half-box.",
        "The notebooks do not reproduce RMCProfile's F(Q) column to single precision as they do G(r): the program convolves with its own r<sub>max</sub> and grid; an F(Q) cross-check is future work.",
        "In real space the same physics appears as the R_CUTOFF keyword: below the closest approach the Fourier ripples are set to the baseline."
      ],
      "notes": "Derive the sinc kernel from the Fourier transform of a rectangle and note the two ways to be consistent: convolve the model (RMCProfile's choice) or deconvolve the data (impossible). Q: \"Why not just use a bigger box?\" A: A bigger box moves the ripples to smaller Q spacing and reduces their amplitude but never removes them; the convolution is exact for any box, which is better than approximate for a big one."
    },

    "con-why": {
      "level": "intro", "layout": "text",
      "title": "Why data are not enough",
      "lead": "A fit that reproduces G(r) can still put two chlorines where a sodium belongs, break a coordination polyhedron, or let an atom drift through a wall of neighbours. Constraints say what the data cannot.",
      "bullets": [
        "Hard constraints make a move impossible (closest approach, distance window, fixed coordination).",
        "Soft restraints penalise it (bond potentials, bond valence sums) and enter the acceptance rule as an energy.",
        "Every one of them is a keyword block in the .dat file; lecture 6 runs each for six seconds on the NaCl set and measures the refined box."
      ],
      "notes": "Give an example per bullet from a real material the students know: a closest approach for any ionic crystal, a distance window for a rigid tetrahedron in silica, a bond valence sum for a transition-metal oxide where the valence is known. Q: \"Do constraints slow the run?\" A: Hard constraints are checked before the histogram and often make runs faster by refusing hopeless moves; potentials and BVS add a term per move and cost a little."
    },
    "con-mindist": {
      "level": "core", "layout": "fig-right", "fig": "s24-f1",
      "title": "Closest approach: <code>MINIMUM_DISTANCES</code>",
      "lead": "One number per pair below which no two atoms may come. Raise the Na–Cl minimum above the inner edge of the thermal shell and the refined box cannot reach the data's peak from below.",
      "bullets": [
        "With the minimum at 2.2 Å the first shell is reproduced on both sides of 2.82 Å; at 2.75 Å it is cut off there and χ² stays two orders of magnitude higher.",
        "The program's message when it stops early — 'Check the MINIMUM_DISTANCES section' — is about the <em>count</em> of numbers, which the checker verifies first.",
        "Choose the minimum from chemistry (ionic radii, a known shortest bond), never from the data's noise floor."
      ],
      "notes": "The figure is the cleanest demonstration in the course of a constraint doing exactly what it says: a histogram truncated at the dotted line. Ask the students what a real material's G(r) would show if its true closest approach were below the constraint: a peak the fit can never reach, a permanent residual. Q: \"How do I pick the values?\" A: Slightly below the shortest bond you believe in; the run's own log prints the shortest distances it found, so a wrong choice shows as a wall in the partials."
    },
    "con-windows": {
      "level": "core", "layout": "text",
      "title": "Windows, potentials, coordination",
      "lead": "Three ways to keep the neighbours you start with. Chapter 6 runs each for six seconds and measures the box RMCProfile saved.",
      "bullets": [
        "<code>DISTANCE_WINDOW ::</code> with MNDIST/MXDIST bounds a pair from both sides and freezes the neighbour list at the start (a <code>.neigh</code> file): with the window every Na–Cl first-shell distance stays within [2.60, 3.05] Å even under 0.5 Å moves; without it, six-fold coordination is lost.",
        "<code>POTENTIALS ::</code> with STRETCH, STRETCH_SEARCH and TEMPERATURE adds a harmonic bond: a stiff 40 eV/Å² term narrows the Na–Cl shell whatever the data say.",
        "<code>FIXED_COORDINATION_CONSTRAINTS ::</code> asks that a fraction of Na keep six Cl within a distance range; the program reports 100.00 % at every print and the refined box keeps 6 : 108 within 3.2 Å."
      ],
      "notes": "Point out the one operational pitfall: the neighbour list is written once; delete the .neigh file whenever the configuration changes, or the program keeps constraining yesterday's neighbours — the checker warns about stale neighbour files. Q: \"Which should I use for a molecular crystal?\" A: A distance window per intramolecular pair, which is a rigid-topology constraint; potentials when you also know the stiffness; coordination constraints for framework atoms whose polyhedra are known."
    },
    "con-bvs": {
      "level": "core", "layout": "fig-right", "fig": "s27-f1",
      "title": "Bond valence sums",
      "lead": "A bond valence sum turns a coordination shell into a chemical check: it should equal the ion's oxidation state. RMCProfile's <code>BVS ::</code> block restrains the fit toward the nominal valences; the toolkit computes the same quantity on any box.",
      "bullets": [
        "For Na–Cl with R<sub>0</sub> = 2.15 Å and b = 0.37 Å the ideal lattice gives V(Na) = 0.981.",
        "The box refined under the BVS restraint has V(Na) = 0.995 ± 0.03 over 108 atoms, centred on +1 — the figure.",
        "The chi2 file gains a BVS column: the restraint is one more term in the total the run minimises."
      ],
      "notes": "Introduce the Brese–O'Keeffe parameters as tabulated empirical constants per cation–anion pair and note that they are the same numbers a crystallographer uses to validate a refined structure — RMC just applies them per atom, thousands of times. Q: \"Why is the ideal-lattice value not exactly 1?\" A: The tabulated R₀ comes from many structures; NaCl's bond of 2.82 Å is slightly long for it, giving 0.981 — a 2 % discrepancy that is typical, and that the restraint does not try to remove."
    },
    "con-math": {
      "level": "math", "layout": "eq",
      "title": "The restraint terms",
      "lead": "Every constraint on this lecture's slides is one of three expressions added to the acceptance rule.",
      "eqs": [
        {"label": "hard wall", "math": "<span class='math'>P<sub>accept</sub> = 0 &nbsp;<span class='fn'>if</span>&nbsp; d<sub>ab</sub> &lt; d<sup>min</sup><sub>ij</sub> &nbsp;<span class='fn'>or</span>&nbsp; d<sub>ab</sub> ∉ [ MNDIST, MXDIST ]</span>"},
        {"label": "bond potential", "math": "<span class='math'>ΔU/k<sub>B</sub>T, &nbsp; U = ½ k ( d − d<sub>0</sub> )<sup>2</sup> &nbsp;<span class='fn'>for</span> | d − d<sub>0</sub> | ≤ STRETCH_SEARCH</span>"},
        {"label": "bond valence sum", "math": "<span class='math'>V<sub>a</sub> = Σ<sub>b</sub> <span class='fn'>exp</span>[ ( R<sub>0</sub> − d<sub>ab</sub> ) / b ], &nbsp; χ<sup>2</sup><sub>BVS</sub> = w Σ<sub>a</sub> ( V<sub>a</sub> − V<sub>nominal</sub> )<sup>2</sup></span>"}
      ],
      "bullets": [
        "The wall costs nothing when it refuses: no histogram update, no χ² evaluation.",
        "STRETCH_SEARCH defines which pairs are bonds at the start — the bond list is generated once, like the neighbour list.",
        "The BVS weight multiplies a sum over atoms, so it scales with box size; RMCProfile's WEIGHTS entry is per atom type."
      ],
      "notes": "Show that all three are 'energies' in the sense of lecture 2's Metropolis rule, with the hard wall as an infinite one. Then ask which are functions of the data (none) — they are the prior, and a well-set prior lets σ be honest. Q: \"How do I know a restraint is not fighting the data?\" A: Look at the chi2 file: the data columns should fall while the restraint column stays small; a restraint column that grows is the data disagreeing with your chemistry, which is a result, not a nuisance."
    },

    "cor-instrument": {
      "level": "intro", "layout": "text",
      "title": "What the instrument does to G(r)",
      "lead": "A measured F(Q) ends at a finite Q<sub>max</sub> and is smeared by the instrument's resolution; its transform is damped at large r and its peaks are broadened. RMCProfile corrects the <em>calculated</em> function to look like the data.",
      "bullets": [
        "<code>RESOLUTION_CORRECTION</code> damps the calculated real-space function with r.",
        "<code>BROADENING_CORRECTION</code> convolves it with a Gaussian whose width grows with r.",
        "<code>PARTICLE_RADIUS</code> (with <code>BULK_RHO</code>) applies a nanoparticle shape function; <code>R_CUTOFF</code> zeroes the Fourier ripples below the closest approach.",
        "Lecture 7's rule: before trusting a formula, measure what the program applies."
      ],
      "notes": "Set the method up front: every experiment of this lecture evaluates the truth box against synthetic data at TIME_LIMIT 0 with and without a keyword, so the ratio or difference of the two calculated columns is the keyword's action, exactly, on a known function. Q: \"Why not read the formula from the manual?\" A: Because on the next slide the manual's formula is not what the program computes — and that is a finding, not a complaint."
    },
    "cor-measured": {
      "level": "core", "layout": "fig", "fig": "s29-f1",
      "title": "Damping, measured: Gaussian, not exponential",
      "lead": "The manual describes RESOLUTION_CORRECTION as exp(−r·Expo). The ratio of RMCProfile's calculated columns with and without the keyword is exp(−(α r)²/2) to 10⁻³ — PDFgui's Q<sub>damp</sub> form — and departs from the exponential by 0.25 at 8 Å.",
      "notes": "This slide is the course's demonstration of the scientific method applied to software: a documented claim, a clean measurement, a discrepancy, a reproducible record (finding P-17 in the study's ledger, draft note to the developers). Emphasise that the program's behaviour is the sensible one — the Gaussian is what a Gaussian resolution function in Q produces. Q: \"Could the measurement be wrong instead?\" A: The two runs differ only by one keyword on one box with no moves; the ratio is model-independent, and it is reproduced on the Linux build."
    },
    "cor-damped": {
      "level": "core", "layout": "fig-right", "fig": "s29-f2",
      "title": "The right damping wins",
      "lead": "Synthesise data from the truth box's G(r) damped by exp(−(0.05 r)²/2). Evaluate the truth box against them with no correction, with α = 0.05 and with α = 0.20: the right α has the lowest χ².",
      "bullets": [
        "The model is the truth box itself, so the only difference between model and data is the correction under test.",
        "Exercise 7.1 scans α over 0.02, 0.05, 0.10: the minimum sits at 0.05, and the well is not sharp — resolution parameters are best taken from a calibrant, not fitted.",
        "Convert a PDFgui Q<sub>damp</sub> directly: it is the same α."
      ],
      "notes": "Point at the peaks near 8 Å where the uncorrected model is visibly too tall, then at the corrected one on top of the data. Mention what went wrong in the first version of this experiment (the ideal lattice as model, every damping 'improving' it) — students appreciate a corrected mistake more than a clean result. Q: \"Does damping change the peak positions?\" A: No: a multiplicative envelope in r scales heights only; broadening, next slide, is what moves and smears them."
    },
    "cor-broad": {
      "level": "core", "layout": "fig-right", "fig": "s30-f1",
      "title": "Broadening: <code>BROADENING_CORRECTION</code>",
      "lead": "Finite Q-resolution broadens each peak in r by an amount growing with r: a Gaussian of σ = β r (manual Appendix F). Synthetic data broadened that way are fitted best by the same β.",
      "bullets": [
        "The toolkit does the r-dependent convolution explicitly; RMCProfile's β = 0.02 reproduces it and wins the χ² comparison by two orders of magnitude against no correction.",
        "The parameter is not PDFgui's Q<sub>broad</sub>; Appendix F relates them.",
        "At 7.6–8 Å the uncorrected peaks are visibly narrower and taller than the data's."
      ],
      "notes": "Contrast with the previous slide: damping is an envelope, broadening is a convolution; a real instrument does both, and exercise 7.2 shows that the two corrections together beat either alone on data that carry both. Q: \"Can broadening be confused with thermal motion?\" A: In a single data set, partly — both widen peaks; but thermal widths are r-independent and resolution widths grow with r, so a fit over a long r range separates them, which is one reason to fit far out."
    },
    "cor-nano": {
      "level": "core", "layout": "fig", "fig": "s31-f1",
      "title": "Nano-size: what <code>PARTICLE_RADIUS</code> actually changes",
      "lead": "Measured the same way, PARTICLE_RADIUS does not scale the peaks by a shape function. Beyond the closest approach it adds −G₀·[1 − f(r)] with f the spherical shape function of diameter 2R: the bulk baseline replaced by the envelope-weighted one, to 0.01 barn rms.",
      "notes": "Explain why that is the physically right correction for a nanoparticle box: the box's own histogram already lacks the pairs that do not fit in the particle; what a finite particle additionally lacks is the uniform background that the '−1' of g − 1 assumes. The keyword needs BULK_RHO beside it or the program stops — finding P-18, now a checker error. Q: \"Why does the difference vanish below 2.5 Å?\" A: The correction is applied beyond a short-distance cutoff (the NANO_RCUTOFF_OFF keyword's realm); below it the Fourier ripples region is left alone."
    },
    "cor-math": {
      "level": "math", "layout": "eq",
      "title": "The three corrections, as the program applies them",
      "lead": "Each was measured on the same 216-atom box at TIME_LIMIT 0; each is a line a data reduction can be matched to.",
      "eqs": [
        {"label": "damping (RESOLUTION_CORRECTION α)", "math": "<span class='math'>G<sub>calc</sub>(r) → G<sub>calc</sub>(r) · <span class='fn'>exp</span>[ −(α r)<sup>2</sup> / 2 ]</span>"},
        {"label": "broadening (BROADENING_CORRECTION β)", "math": "<span class='math'>G<sub>calc</sub>(r) → ∫ G<sub>calc</sub>(r′) <span class='fn'>N</span>( r − r′ ; σ = β r ) dr′</span>"},
        {"label": "nano-size (PARTICLE_RADIUS R, BULK_RHO ρ)", "math": "<span class='math'>G<sub>calc</sub>(r) → G<sub>calc</sub>(r) − G<sub>0</sub> [ 1 − f(r) ], &nbsp; f = 1 − 3r/2D + r<sup>3</sup>/2D<sup>3</sup>, &nbsp; D = 2R</span>"}
      ],
      "bullets": [
        "The damping is the Fourier pair of a Gaussian resolution function in <span class='math'>Q</span> of width <span class='math'>1/α</span>; the manual's exp(−r·Expo) would correspond to a Lorentzian.",
        "The Guinier shape function <span class='math'>f</span> is the fraction of pair vectors of length <span class='math'>r</span> that fit inside a sphere of diameter <span class='math'>D</span>: 1 at the origin, 5/16 at <span class='math'>D/2</span>, 0 at <span class='math'>D</span>.",
        "<span class='math'>G<sub>0</sub> = −(Σ c b)<sup>2</sup></span> is the baseline of lecture 0; for NaCl −0.4361 barn."
      ],
      "notes": "Derive the shape function as the overlap volume of two spheres of diameter D displaced by r, normalised by the sphere volume; its derivative at the origin gives the −3r/2D term that Guinier's small-angle law shares. Q: \"Which G₀ does the program use — the box's or BULK_RHO's?\" A: The measured difference matches −G₀ with the box's scattering lengths; BULK_RHO enters the normalisation of the pair density for a particle in a larger box, which the synthetic bulk box does not exercise — a limit the notebook states."
    },

    "bey-formfactor": {
      "level": "intro", "layout": "fig", "fig": "s19-f1",
      "title": "X-rays see electrons: the form factor",
      "lead": "A neutron's scattering length is a constant per isotope; an X-ray's is the atomic form factor f(Q): Z electrons at Q = 0, falling with Q. The ratio between two elements is not constant, so an X-ray F(Q) mixes the partials with Q-dependent weights.",
      "notes": "Read the figure: Na starts at 11, Cl at 17, and the dashed ratio drifts across Q because the diffuse valence electrons of Cl scatter away faster. RMCProfile takes f(Q) from a .xray file of Cromer–Mann coefficients; the toolkit computes them from the BSD-licensed periodictable tables and fits the four-Gaussian form the file needs, to 0.05 electron over 0–25 Å⁻¹. Q: \"Why do neutrons not have this problem?\" A: The nucleus is a point on the scale of the neutron's wavelength; the electron cloud is not on the X-ray's."
    },
    "bey-contrast": {
      "level": "core", "layout": "fig", "fig": "s20-f1",
      "title": "Contrast: the same box, two radiations",
      "lead": "Neutrons weigh Cl–Cl most (3.63 versus 9.58 fm); X-rays weigh Na–Cl more and the balance drifts with Q. Two data sets on one box see different partials — the reason to fit both.",
      "notes": "This is the physics behind 'neutron and X-ray total scattering are complementary': the same three partials with two different, and Q-dependent, sets of weights. Show the right panel's weights summing to one at every Q. Q: \"Which normalisation does RMCProfile use for X-rays?\" A: Its default NORMALIZATION_TYPE is ⟨f²⟩, an alternative is ⟨f⟩²; the toolkit's F(Q) uses (Σcf)² — and the next slide shows what the program's column actually agrees with."
    },
    "bey-xrayrun": {
      "level": "core", "layout": "fig-right", "fig": "s21-f1",
      "title": "An X-ray run, and what it does not confirm",
      "lead": "The X-ray block runs, reports χ², returns our data exactly in its experiment column, and its calculated column has our scale — median ratio 0.999 — but its shape agrees with ours only to a correlation of 0.90, and neither NORMALIZATION_TYPE value changes it.",
      "bullets": [
        "The neutron functions are reproduced to single precision; the X-ray F(Q) processing is not — finding N-8, a question for the mailing list, not a lowered threshold.",
        "What the notebook claims is exactly what it measured: same scale, same peak positions, partial agreement in shape.",
        "The .xray file the toolkit writes is accepted by the program; the checker validates the block."
      ],
      "notes": "Use this slide to model honesty: the check in the notebook says 'correlates at 0.85 or better — and that is all this book can claim'. Discuss what could differ: a Q-dependent convolution, the form factor evaluated at a different Q for the ⟨f²⟩ average, an r-space route. Q: \"Should I use RMCProfile for X-ray data then?\" A: Yes — the program's X-ray fits are published and validated by its authors on real data; what is open is the reproduction of its convention by an outside toolkit, which is what a cross-check is for."
    },
    "bey-bragg": {
      "level": "core", "layout": "fig", "fig": "s22-f1",
      "title": "Bragg profiles: the long-range order",
      "lead": "RMCProfile is the RMC code that fits the Bragg profile together with the PDF. The BRAGG block needs four files from a Rietveld program; on the shipped SF₆ exercise the toolkit reads them, the program evaluates the profile, and the shipped configuration reproduces it with correlation 0.998.",
      "notes": "Name the four files: the profile (.bragg, time of flight against intensity for one bank), the background coefficients (.back), the GSAS instrument parameters (.inst) and the reflection-range scale (.hkl). No synthetic set can replace a real Rietveld refinement, which is why this section uses the exercise the developers ship — read from the reader's own installation, never redistributed. Q: \"Why fit Bragg peaks at all if the PDF has everything?\" A: The PDF's long-range information is weak and damped; the Bragg profile pins the average cell and the mean-square displacements, which keeps the box from drifting while the PDF shapes the local structure."
    },
    "bey-exafs": {
      "level": "core", "layout": "fig-right", "fig": "s32-f1",
      "title": "EXAFS on the shipped exercise",
      "lead": "The EXAFS block fits the absorption fine structure χ(k) of one absorbing element, computed from the box with FEFF-style path amplitudes. The shipped SnO exercise evaluates two edges in eleven seconds at TIME_LIMIT 0 and writes k-space and r-space outputs per edge.",
      "bullets": [
        "Keywords per edge: FILENAME, TYPE(S)_OF_ABSORBING_ATOMS, START/END_POINT in k and in r, FIT_space, R_SPACING, K_POWER, ENERGY_OFFSET, WEIGHT.",
        "The k-space start and end points are k values in Å⁻¹ (3.3–13.2 in the exercise), not point indices as in the PDF blocks — the exercise reads it off the output.",
        "The absorber and scatterer lists and the path files come from the exercise's preparation step, not from RMCProfile."
      ],
      "notes": "EXAFS is element-specific where the PDF is not: it sees the environment of the absorber only, out to a few shells, which makes it the natural partner of a PDF fit for a dilute or a mixed-site element. Q: \"Why does the notebook not run a one-minute EXAFS refinement?\" A: It tried: under the exercise's weight optimisation the χ² of the EXAFS term is rescaled during the run and the before/after numbers are not comparable — an honest exercise reads the output ranges instead."
    },
    "bey-magnetic": {
      "level": "core", "layout": "text",
      "title": "Magnetic and diffuse: described, not run",
      "lead": "Two data types this course cannot reproduce with its own engine and the package ships no exercise for: the notebooks document their keyword blocks so a reader with such data knows what the program expects.",
      "bullets": [
        "<code>MAGNETISM ::</code> — FORM_FACTOR, MAGNETISM_FILE_STEM, MAGNETIC_ATOMS, MAX_SPIN_MOVEMENT, SPIN_MOVE_RATE: spins refined alongside positions against the magnetic pair distribution (Paddison & Goodwin 2012 for the idea).",
        "<code>DIFFUSE_SCATTERING3D ::</code> — a measured reciprocal-space volume against the box's, with SUPERCELL_DIMENSIONS declared so the average amplitude can be computed; costly per move.",
        "Where this leaves the course: every pair-distribution data type reproduced, X-rays reproduced in scale and partly in shape, Bragg and EXAFS run on the shipped exercises, magnetic and diffuse described from the manual."
      ],
      "notes": "Be plain about the boundary: a course that claims to run everything would be lying; one that says what it ran and what it read is a course the students can trust. Q: \"Where would I learn magnetic RMC properly?\" A: From the Spinvert and RMCProfile magnetic papers and the program's own workshop material once a magnetic exercise ships; the notebooks' chapter 8 lists the keywords so the first run has no surprises."
    },
    "bey-math": {
      "level": "math", "layout": "eq",
      "title": "X-ray weights and the normalisation question",
      "lead": "The three partials, two sets of weights; and the two conventions a data reduction must match.",
      "eqs": [
        {"label": "toolkit's X-ray F(Q)", "math": "<span class='math'>F<sub>X</sub>(Q) = Σ<sub>ij</sub> c<sub>i</sub> c<sub>j</sub> f<sub>i</sub>(Q) f<sub>j</sub>(Q) [ S<sub>ij</sub>(Q) − 1 ] / ( Σ<sub>i</sub> c<sub>i</sub> f<sub>i</sub>(Q) )<sup>2</sup></span>"},
        {"label": "the other convention", "math": "<span class='math'>… / Σ<sub>i</sub> c<sub>i</sub> f<sub>i</sub>(Q)<sup>2</sup> &nbsp; (NORMALIZATION_TYPE :: &lt;f^2&gt;, the default)</span>"},
        {"label": "Cromer–Mann form", "math": "<span class='math'>f(s) = Σ<sub>k=1..4</sub> a<sub>k</sub> <span class='fn'>exp</span>( −b<sub>k</sub> s<sup>2</sup> ) + c, &nbsp; s = Q / 4π</span>"}
      ],
      "bullets": [
        "Both normalisations make the weights sum to one at every <span class='math'>Q</span> in the (Σcf)² case and nearly so in the other; they differ by a few per cent along <span class='math'>Q</span>.",
        "The measured RMCProfile column matches neither in shape (correlation 0.90 against both), while matching the (Σcf)² scale (ratio 0.999) — so the difference is not the normalisation.",
        "The Appendix-D route treats X-ray G(r) as neutron data with <span class='math'>b → Z</span>: constant weights, an approximation the toolkit also provides."
      ],
      "notes": "Show why the two normalisations are close: for NaCl ⟨f⟩² and ⟨f²⟩ differ by the variance of f across the two elements, which is a few per cent of the mean. Then leave the open question open. Q: \"What would settle it?\" A: One sentence from the developers, or a second measurement: the calculated column against a single-element box, where every normalisation coincides and only a Q-dependent processing would remain."
    },

    "rd-statistical": {
      "level": "intro", "layout": "text",
      "title": "A refined box is a statistical object",
      "lead": "What one reads off a box must be distributions — coordination numbers, bond lengths, bond angles, displacement clouds — never the position of a particular atom. Four analyses, each checked against the answer the synthetic truth knows.",
      "bullets": [
        "<code>coordination(cfg, A, B, rmax)</code>: per-atom counts and their histogram.",
        "The bond-length distribution is the partial itself, weighted by the shell: its mean and width are the two numbers a PDF is usually asked for.",
        "<code>bond_angles(cfg, A, B, C, rmax)</code>: every B–A–C angle whose arms are within rmax.",
        "Displacement of each atom from its own ideal site, projected — the displacement cloud."
      ],
      "notes": "Return to lecture 3's thesis and turn it into practice: here are the four things a box can tell you, and here is how each is checked against the truth in the notebook. Q: \"Can I read a defect off a box?\" A: Only as a statistic — 'x % of Na have five Cl within 3.2 Å' — and only if it survives an ensemble of fits, next slides."
    },
    "rd-coordination": {
      "level": "core", "layout": "fig-right", "fig": "s36-f1",
      "title": "Coordination numbers and bond lengths",
      "lead": "In rock salt every Na keeps six Cl within 3.2 Å whatever the thermal motion: the histogram is a single bar, 6 : 108. The Na–Cl bond from the fitted box is 2.822 ± 0.074 Å against the truth's 2.822 ± 0.072 Å.",
      "bullets": [
        "Mean and width come from the Na–Cl partial weighted by r² over the first shell, the same for fit and truth.",
        "Coordination does not change in a close-packed ionic crystal; thermal motion broadens shells, it does not move atoms between them.",
        "The second shell too: twelve Na–Na neighbours within 4.3 Å for every Na (exercise 9.1)."
      ],
      "notes": "Show the two numbers side by side and point out that the width agrees within 3 % — the fit recovered the thermal width of the bond although it recovered no coordinate. Q: \"What if my box gives 5.8 average coordination?\" A: Look at the histogram, not the average: a few five- and seven-fold atoms from a too-large closest approach or move size, or a genuine defect population; the ensemble spread of the next slides tells which."
    },
    "rd-angles": {
      "level": "core", "layout": "fig", "fig": "s37-f1",
      "title": "Bond angles and displacement clouds",
      "lead": "Cl–Na–Cl angles peak at 90° and 180°, broadened by the thermal displacements; the fit's 90° peak sits at 89.9° with a spread of 2.08° against the truth's 2.02°. The right panel is every Na's displacement from its own ideal site — the cloud a displacement ellipsoid summarises.",
      "notes": "The displacement cloud's width, 0.057 Å against the truth's 0.056 Å, is the single-atom displacement the synthetic box was built with. Mention the bug this figure once carried — folding into the unit cell centred only the corner site, and the face-centred Na gave a 2 Å 'cloud' — as an example of checking every analysis against a known answer. Q: \"Why compute displacements per atom rather than fold everything?\" A: Fold-back mixes the four Na sites' clouds; the per-atom displacement from its own ideal site is the quantity a displacement parameter measures."
    },
    "rd-ensembles": {
      "level": "core", "layout": "fig", "fig": "s38-f1",
      "title": "Ensembles: several fits are better than one",
      "lead": "One fitted box carries the statistical noise of its 216 atoms. Four fits from different seeds, averaged, are closer to the target than any single fit — and the spread between them is the honest error bar of anything read off a box.",
      "notes": "RMCProfile users run several independent refinements for the same reason; the notebook's numbers: the ensemble mean's rms deviation from the target, 0.081, against the best single fit's 0.098. Q: \"How many boxes are enough?\" A: When the quantity you report stops changing with one more box, and when its spread across boxes is below the effect you claim — typically five to ten for a published distribution."
    },
    "rd-math": {
      "level": "math", "layout": "eq",
      "title": "Distributions from a box",
      "lead": "Every number on the previous slides is one of these moments.",
      "eqs": [
        {"label": "bond length from the partial", "math": "<span class='math'>⟨d⟩ = Σ<sub>shell</sub> r<sub>k</sub><sup>3</sup> g(r<sub>k</sub>) / Σ<sub>shell</sub> r<sub>k</sub><sup>2</sup> g(r<sub>k</sub>), &nbsp; σ<sub>d</sub><sup>2</sup> = Σ r<sub>k</sub><sup>2</sup> g(r<sub>k</sub>) ( r<sub>k</sub> − ⟨d⟩ )<sup>2</sup> / Σ r<sub>k</sub><sup>2</sup> g(r<sub>k</sub>)</span>"},
        {"label": "displacement from the ideal site", "math": "<span class='math'>u<sub>a</sub> = [ x<sub>a</sub> − x<sub>a</sub><sup>ideal</sup> − <span class='fn'>round</span>( x<sub>a</sub> − x<sub>a</sub><sup>ideal</sup> ) ] · L</span>"},
        {"label": "ensemble estimate", "math": "<span class='math'>ḡ = (1/N) Σ<sub>n</sub> g<sub>n</sub>, &nbsp; <span class='fn'>rms</span>( ḡ − g<sub>target</sub> ) &lt; <span class='fn'>min</span><sub>n</sub> <span class='fn'>rms</span>( g<sub>n</sub> − g<sub>target</sub> )</span>"}
      ],
      "bullets": [
        "The <span class='math'>r<sup>2</sup></span> weighting turns <span class='math'>g(r)</span> back into a pair count per shell before averaging.",
        "The round() is the minimum-image wrap in fractional coordinates; <span class='math'>L</span> the lattice matrix.",
        "Independent fits have independent noise; averaging <span class='math'>N</span> of them reduces it as <span class='math'>1/√N</span> until the systematic residual is reached."
      ],
      "notes": "Derive the first line from the definition of g: n(r) = 4πr²ρc g(r) dr is the number of pairs in the shell, so moments of the distance distribution are r²g-weighted. Q: \"Is the ensemble mean a physical box?\" A: No — averaged partials are not the partials of any box; the ensemble gives distributions and their uncertainties, and a single box gives pictures."
    },

    "ctr-crosscheck": {
      "level": "intro", "layout": "text",
      "title": "The cross-check, live, and what the numbers cost",
      "lead": "Everything the notebooks compute on their own is compared with the package's output on the package's own exercise: partials equal to 2.8×10⁻⁴ (its single precision), G(r) to 3×10⁻⁵ barn, on both builds, against recorded tolerances that were measured, not chosen.",
      "bullets": [
        "<code>upstream_adapter</code> stages a shipped exercise in a scratch directory, runs the program and compares; the records file stores tolerances, measured maxima and a provenance line — never the package's data.",
        "The smoke test reproduces the exercise's χ²/dof of 0.4201 on Windows (CUDA) and on Linux (CPU); the deterministic passes print identical numbers on both.",
        "Cost: rmclite ~1 900 moves/s on 64 atoms; RMCProfile ~20 000 moves/s with G(r) only and far fewer with an F(Q) set — the Fourier transform per move is what reciprocal space costs."
      ],
      "notes": "The cross-check is what turns a teaching toolkit into a trustworthy one: not 'our functions look right' but 'our functions equal the program's to its own precision on its own example, and here is the test that says so'. Q: \"Why not compare F(Q) too?\" A: The program convolves F(Q) with its box function on its own grid; an F(Q) cross-check needs that convention reproduced first, which is queued."
    },
    "ctr-ecosystem": {
      "level": "core", "layout": "table",
      "title": "The ecosystem",
      "lead": "RMCProfile's site lists the neighbours it considers relevant; one honest line each, no ranking.",
      "table": {
        "head": ["tool", "what it is", "relation to RMCProfile"],
        "rows": [
          ["RMC++ (Budapest)", "the general RMC code descended from RMCA, for liquids and glasses", "the common ancestor; RMCProfile added crystals, Bragg profiles and the constraint families"],
          ["HRMC (CSIRO)", "hybrid RMC with interatomic potentials", "the idea RMCProfile's POTENTIALS block adopts for specific bonds"],
          ["fullrmc", "a Python RMC engine with a modular constraint system", "a scriptable alternative; no Bragg-profile fitting"],
          ["EPSR / Dissolve (ISIS)", "empirical potential structure refinement for liquids and glasses", "data-driven potentials rather than direct moves"],
          ["DISCUS", "diffuse-scattering simulation and refinement of disordered crystals", "the rmc_to_discus export; another route to the same disorder"],
          ["PDFgui / diffpy-CMI", "small-box PDF refinement and its scriptable successor", "the average-structure-plus-parameters description RMC's big box complements"],
          ["GudrunN/X, PDFgetX3, Mantid, ADDIE", "data reduction from raw scattering to F(Q) and G(r)", "what produces the files the notebooks synthesised"],
          ["Topas4RMC, sofq_calib, rmc_tools", "RMCProfile's own Python side tools (conda, GPL)", "the surface where an outside contributor's patches can go"]
        ]
      },
      "notes": "Use the table to locate RMCProfile: big-box, crystal-aware, multi-data-type, closed-source Fortran with an open Python fringe. Q: \"Which should a beginner learn first?\" A: PDFgui for the average-structure view of the same data, then RMCProfile when the small box's parameters stop explaining the PDF — the notebooks' lecture 3 is the argument for when that happens."
    },
    "ctr-how": {
      "level": "core", "layout": "text",
      "title": "How findings become contributions",
      "lead": "RMCProfile is closed-source, so contributions are reports, reproductions and documentation — through its mailing list, under the contributor's own name. The study behind this course keeps a ledger; every entry has a run log, a file and a line.",
      "bullets": [
        "PROVEN findings from the shipped exercises: a missing input file stops the program with exit code 0 (P-11); a missing .poly makes it wait forever (P-12); a data file's letter case breaks the Linux build (P-10).",
        "Measured against the manual: the damping is Gaussian (P-17); PARTICLE_RADIUS needs BULK_RHO (P-18) — each a chapter check and a draft note to the developers.",
        "Open: the X-ray F(Q) processing (N-8) — a question, drafted, never sent by a machine.",
        "Patches go to the GPL Python tools, with tests; nothing from the package is ever redistributed."
      ],
      "notes": "Discuss the ethics briefly: reproducing a bug is a gift to the developers only if it is reproducible, polite and specific; drafting under someone else's name is neither. Q: \"Can students send findings?\" A: Yes, and this is how a scientific software community works — subscribe, reproduce, report with a minimal example; the exit-code-0 stop is a good first message."
    },
    "ctr-math": {
      "level": "math", "layout": "eq",
      "title": "Measure, don't assume: the ratio method",
      "lead": "The technique behind lecture 7's findings generalises: two deterministic evaluations of the same box, one keyword apart, isolate what the keyword does.",
      "eqs": [
        {"label": "multiplicative keyword", "math": "<span class='math'>R(r) = G<sub>calc</sub><sup>with</sup>(r) / G<sub>calc</sub><sup>without</sup>(r) &nbsp;<span class='fn'>away from zero crossings</span></span>"},
        {"label": "additive keyword", "math": "<span class='math'>Δ(r) = G<sub>calc</sub><sup>with</sup>(r) − G<sub>calc</sub><sup>without</sup>(r)</span>"},
        {"label": "the verdict", "math": "<span class='math'><span class='fn'>max</span> | R − <span class='fn'>exp</span>(−(αr)<sup>2</sup>/2) | &lt; 10<sup>−3</sup>, &nbsp; <span class='fn'>rms</span> | Δ + G<sub>0</sub>(1 − f) | &lt; 0.02 <span class='fn'>barn</span></span>"}
      ],
      "bullets": [
        "TIME_LIMIT 0 makes both evaluations deterministic; the truth box as model makes the columns smooth enough to divide.",
        "A hypothesis is a function to compare with; the number reported is the deviation, with its threshold stated before the run.",
        "The same method cross-checks the toolkit against the program: our function, its column, the maximum difference, recorded at the measured precision."
      ],
      "notes": "Close the course on method: the notebooks are one long exercise in stating a hypothesis as a function, computing the deviation, and writing down the number — with the program, with the manual, with one's own earlier mistakes. Q: \"What if the ratio is noisy?\" A: Mask the zero crossings (the notebook uses |G| > 0.05 barn) and use the truth box, whose peaks are smooth; on an ideal lattice's spikes the ratio is undefined almost everywhere."
    },

    "close-next": {
      "level": "intro", "layout": "text",
      "title": "Where to go next",
      "lead": "The notebooks are the course; the program's manual and tutorials are the reference; the mailing list is the community.",
      "bullets": [
        "Run the eleven chapters on your own machine; change the truth box (a different salt, a different displacement) and see which checks still pass.",
        "Install RMCProfile 6.7.9 under its own terms and run the shipped exercises through the toolkit's cross-check; then your own data.",
        "Read Tucker et al. 2007 (RMCProfile) and Keen 2001 (the functions); Playford et al. 2014 for a review of what RMC has found in crystals.",
        "When something in the manual and the program disagree, measure it, write it down, and tell the developers."
      ],
      "notes": "End with the reading list and the invitation. Q: \"What is the one thing to remember?\" A: A reverse Monte Carlo box reproduces distributions, not coordinates — read it for what it knows, and constrain it with what you know."
    }
  },
  "glossary": [
    ["pair distribution function (PDF)", "the distribution of interatomic distances in a sample; g_ij(r) per pair of types, G(r) the weighted total"],
    ["partial g_ij(r)", "pairs of types i and j at distance r, normalised so that a structureless gas gives 1"],
    ["Keen's G(r)", "Σ c_i c_j b_i b_j [g_ij(r) − 1] in barn; tends to −(Σcb)² at r → 0"],
    ["D(r), T(r)", "4πrρ G(r), and D(r) plus 4πrρ(Σcb)²; the other two real-space conventions RMCProfile accepts"],
    ["F(Q)", "the total scattering function in reciprocal space; the Fourier pair of G(r)"],
    ["Faber–Ziman partial S_ij(Q)", "the sine transform of g_ij(r) − 1; the reciprocal-space partial"],
    ["scattering length b", "a nucleus's neutron scattering amplitude, constant in Q; in femtometres"],
    ["form factor f(Q)", "an atom's X-ray scattering amplitude, Z electrons at Q = 0, falling with Q"],
    ["reverse Monte Carlo (RMC)", "moving atoms of a large box at random and keeping the moves that bring its calculated functions closer to the data"],
    ["Metropolis rule", "accept a move that lowers χ² always, one that raises it with probability exp(−Δχ²/2)"],
    ["χ² (chi-squared)", "the sum over bins of squared residuals between calculated and target functions divided by σ²"],
    ["σ (sigma)", "the uncertainty per bin that scales how strongly a data set pulls; effectively the data's temperature"],
    ["supercell", "the unit cell repeated n × m × l times to make the RMC box"],
    ["rmc6f", "RMCProfile's configuration file: cell, atom types, and each atom's fractional position with site and cell indices"],
    [".dat file", "the keyword file that drives a run: scalars, data blocks with subordinate keywords, flags"],
    ["TIME_LIMIT 0", "a run that evaluates the starting box against the data and makes no move; deterministic"],
    ["MINIMUM_DISTANCES", "the closest approach per pair of atom types, in the order AA AB AC BB BC CC"],
    ["DISTANCE_WINDOW", "per-pair lower and upper bounds that also freeze the neighbour list at the start"],
    ["bond valence sum", "Σ exp[(R₀ − d)/b] over an atom's neighbours; should equal the oxidation state"],
    ["CONVOLVE", "the keyword that convolves the calculated F(Q) with the box function so a truncated transform is fitted consistently"],
    ["RESOLUTION_CORRECTION", "damping of the calculated real-space function by exp(−(αr)²/2), as measured on 6.7.9"],
    ["BROADENING_CORRECTION", "convolution of the calculated function with a Gaussian of width βr"],
    ["PARTICLE_RADIUS / BULK_RHO", "the nanoparticle correction: the bulk baseline replaced by the shape-function-weighted one beyond the closest approach"],
    ["shape function f(r)", "the fraction of pair vectors of length r that fit inside a sphere of diameter D: 1 − 3r/2D + r³/2D³"],
    ["Bragg profile", "the powder diffraction pattern of the average structure; RMCProfile fits it together with the PDF"],
    ["EXAFS χ(k)", "the X-ray absorption fine structure of one absorbing element, a sum over scattering paths from its neighbours"],
    ["displacement cloud", "the distribution of an atom's displacements from its ideal site over a box; what a displacement ellipsoid summarises"],
    ["ensemble", "several independent RMC fits of the same data; their mean is the estimate and their spread the error bar"],
    ["cross-check", "comparing the toolkit's functions with RMCProfile's own output columns on the same box, to a recorded, measured tolerance"],
    ["rmclite", "the notebooks' clean-room reverse Monte Carlo engine, small enough to read"]
  ]
};
