# Reverse Monte Carlo with RMCProfile — the course

An undergraduate course in eleven lectures built on the companion book of
chapter notebooks (`chapters/`). **Every figure the notebooks generate — all
24 — appears in the course, in the slides and in the PDF fallback alike, under
its full notebook caption** with its figure number, section and cell; a test
fails if a figure drifts from the notebook output or goes unused. Every number
on a slide is a number a chapter cell printed.

```
course/
  deck/index.html         the slides (reveal.js, offline; open in a browser)   GENERATED
  deck/content.en.js      THE SOURCE: lectures, slide order, levels, figures, notes
  deck/figs/*.png         figures extracted from the notebooks + provenance.json  GENERATED
  slides.pdf              PDF fallback of the whole deck, one page per slide   GENERATED, committed
  handout/handout.html    A4 companion handout (syllabus, key ideas, equations,
                          glossary); handout.pdf via make_handout.py           GENERATED
  notes/LECTURER_NOTES.md every slide's notes with the anticipated question   GENERATED
  shared/                 theme.css, nav.js, loader.js + vendored reveal.js 5.2.0 (MIT)
  tools/                  extract_figures.py, build_deck.py (stdlib) · verify_deck.py,
                          build_pptx.py, make_handout.py, make_slides_pdf.py (Playwright)
```

## Syllabus

| | Lecture | Notebook |
|---|---|---|
| L0 | Welcome — why local structure: the average structure and what it leaves out, how the course runs, Keen's G(r) | §0–1 |
| L1 | Scattering and the PDF — partials, thermal broadening, G(r)/D(r)/T(r), F(Q) and the box's ringing | §1–4 |
| L2 | Monte Carlo and Metropolis — one move, χ², the acceptance rule, rmclite | §5–6 |
| L3 | Reverse Monte Carlo — from the average structure to the data; distributions, not coordinates; constraints are physics | §7–9 |
| L4 | Preparing a run — supercell and rmc6f, fold-back and export, the .dat file, the checker, synthetic data | §10–14 |
| L5 | Fitting with RMCProfile — one pass, the refinement, CONVOLVE and the box function, the same data through rmclite | §15–18 |
| L6 | Constraints as physics — closest approach, distance windows, potentials, coordination, bond valence sums | §23–27 |
| L7 | Corrections — damping measured (Gaussian), broadening, nano-size (the baseline rule) | §28–31 |
| L8 | Beyond neutrons — X-ray form factors and contrast, an honest X-ray run, Bragg profiles, EXAFS, magnetic and diffuse | §19–22, §32–34 |
| L9 | Reading a configuration — coordination, bond lengths, angles, displacement clouds, ensembles | §35–38 |
| L10 | Contributing to RMCProfile — the live cross-check and its cost, the ecosystem, findings into reports, the ratio method | §39–40 |

The deck is **flat and linear**: one slide after another in the order of
understanding, each lecture opened by a divider slide (its label, summary and
a level-coloured agenda). Within a lecture the slides run *intro → core →
math* — the chip at the top-right of every slide says which — so a first-year
audience stops after the core slides and a fourth-year audience goes on to
the equations. Every slide has lecturer notes ending with an anticipated
student question and its answer.

## Presenting

Open `deck/index.html` in any modern browser — no server, no network. No
browser at hand? `slides.pdf` is the same deck, one page per slide.

| Key | Action |
|---|---|
| `→` / `←`, clicker, space | next / previous slide — the only navigation there is |
| `Shift+→` / `Shift+←`, bottom-right buttons | jump to the next / previous lecture divider (optional) |
| click the progress bar | jump to that lecture |
| `S` | speaker view with the notes |
| `Esc` | overview grid |

PowerPoint: `python course/tools/build_pptx.py` writes a `.pptx` with one
full-bleed screenshot per slide and the notes as editable speaker notes.

## Rebuilding

The content file is the only thing to edit. From `rmcprofile-skill/`:

```bash
python course/tools/extract_figures.py     # notebook outputs -> deck/figs/*.png + provenance.json
python course/tools/build_deck.py          # content.en.js -> index.html, handout.html, LECTURER_NOTES.md
python course/tools/make_slides_pdf.py     # deck -> slides.pdf (committed; needs Playwright)
python -m pytest tests/test_course.py      # provenance fresh, outputs fresh, PDF complete, slides well-formed
```

The stdlib tools accept `--check` (exit 1 when their outputs are stale); the
suite runs those checks and counts the PDF's pages against the deck. When a
chapter is re-executed (`build/execute.py`) the figures must be re-extracted
and the PDF regenerated, or `test_course.py` says what drifted.

Optional tooling (headless Chromium; `make_slides_pdf.py` needs it too):

```bash
pip install -r course/tools/requirements.txt && python -m playwright install chromium
python course/tools/verify_deck.py         # walk every slide: console errors, overflow, screenshots
python course/tools/make_handout.py        # handout.html -> handout.pdf (gitignored)
```

## What the course contains, and does not

Nothing from the RMCProfile package: no tutorial data, no manual text beyond
short cited excerpts, no binary. Lectures 5–8 and 10 show runs of a copy the
reader installs under the developers' own terms; the figures of the shipped
exercises (Bragg, EXAFS) are plots of the program's *output* on the reader's
machine, produced by the notebook cells that ran it.
