# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
from nbbuild import md, code

# Chapter 0. ``__CHAPTER_LIST__`` is filled in by build/assemble.py.
CELLS = [
md(r"""
# Reverse Monte Carlo with RMCProfile — from the pair distribution function to a refined box

**An executed tour of Reverse Monte Carlo modelling of total scattering data: the functions,
the algorithm, the files, the constraints and the corrections — every figure generated live,
every claim checked, every RMCProfile run made on data this book synthesises itself.**

Total scattering measures the pair distribution function of a material — the average of every
interatomic distance — and Reverse Monte Carlo (RMC) builds a box of atoms whose distances
reproduce it. [RMCProfile](https://rmcprofile.ornl.gov/) (Tucker *et al.* 2007) is the program
that does this for crystalline materials, fitting neutron and X-ray total scattering, Bragg
profiles, EXAFS and magnetic data at once. This book walks from Keen's correlation functions
(chapter 1) through the algorithm in a small clean-room engine, `rmclite` (chapter 2), to real
RMCProfile refinements driven from Python (chapters 4–7), and ends with what one does with a
refined box (chapter 9).

RMCProfile is closed-source and distributed by its authors under their own terms; **nothing
from it is in this repository**. The chapters that run it find *your* installation through
`RMCPROFILE_HOME` and print `[SKIP]` where it is absent; every input they feed it is written
here from a synthetic structure, so the outputs you see are ours.

The book is shipped as **one notebook per chapter** (this folder); each runs on its own.
Section numbers (§1–40), figure numbers and cross-references are global, so "§14" means
section 14 wherever it lives.

**Contents**

__CHAPTER_LIST__

### How to run this

One-time setup (Windows / miniconda; a `.sh` twin exists for Linux, macOS and WSL):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_rmcprofile_windows.ps1
```

This creates the conda env `rmcprofile` (Python 3.12, numpy 2, scipy, matplotlib, nbconvert)
and registers the Jupyter kernel **`Python 3.12 (rmcprofile)`** (`rmcprofile-mc`) that every
chapter is pinned to. Verify with `python scripts/verify_rmcprofile.py`. To run the RMCProfile
cells, download the 6.7.9 package from rmcprofile.ornl.gov/download/, unpack it, and set
`RMCPROFILE_HOME` to its `RMCProfile_package` directory before starting Jupyter. Chapter 5 also
wants the `periodictable` package for X-ray form factors (`pip install periodictable`).
Running the whole book takes a few minutes on a laptop; the RMCProfile refinements are capped
at half a minute each. The last cell of this chapter is the setup cell every chapter starts
with — run it here to check the kernel.
"""),

md(r"""
### Conventions used throughout

- **Units.** Ångström for distances, Å⁻¹ for Q, femtometres for scattering lengths, barn for
  G(r) and F(Q) (1 barn = 100 fm²), Å⁻³ for the number density ρ₀ — the manual's conventions.
- **Functions** (Keen 2001; chapter 1): partial $g_{ij}(r)$; total
  $G(r) = \sum_{ij} c_i c_j b_i b_j\,[g_{ij}(r) - 1]$ with the sum over both orderings;
  $D(r) = 4\pi r \rho_0 G(r)$; $T(r) = D(r) + 4\pi r\rho_0 (\sum_i c_i b_i)^2$;
  $F(Q) = \rho_0 \int 4\pi r^2 G(r)\,\sin Qr/(Qr)\,dr$. The r → 0 limit
  $G(0) = -(\sum_i c_i b_i)^2$ is the sanity check of every G(r) in this book.
- **The r grid** is RMCProfile's: $r_k = k\,\Delta r$ with bins centred on $r_k$, so that our
  partials equal the program's `_PDFpartials.csv` (to its single precision).
- **Toolkit.** `rt` is `scripts/rmcprofile_tools.py` (formats, checker, runner, analysis),
  `rl` is `scripts/rmclite.py` (the teaching engine), `ua` is `scripts/upstream_adapter.py`
  (the cross-check). `PKG` is the RMCProfile package found through `RMCPROFILE_HOME`, or
  `None`; `skip_without_package()` prints `[SKIP]` and returns True where a cell needs it.
- Every section that makes a quantitative claim ends with an inline check that prints **PASS**
  or **FAIL**. A clean run has zero FAILs; the last cell of every chapter counts them.
"""),
]

# The setup cell every chapter starts with. build/assemble.py substitutes
# ``__FIG_OFFSET__`` and ``__CHAPTER__``.
SETUP_TEMPLATE = r"""
# ---- shared setup: this cell is identical in every chapter of the book ----------
import os
import sys
import time
import tempfile
import warnings

import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML

# the toolkit lives in scripts/ at the repository root (chapters/ is one level down);
# build/execute.py --outdir runs a copy elsewhere and names the root in RMCPROFILE_SKILL_ROOT
for _cand in ("scripts", os.path.join("..", "scripts"),
              os.path.join(os.environ.get("RMCPROFILE_SKILL_ROOT", ""), "scripts")):
    if os.path.isfile(os.path.join(_cand, "rmcprofile_tools.py")):
        sys.path.insert(0, os.path.abspath(_cand))
        break
import rmcprofile_tools as rt
import rmclite as rl
import upstream_adapter as ua

plt.rcParams.update({"figure.dpi": 100, "figure.figsize": (7.0, 4.0), "axes.grid": True,
                     "grid.alpha": 0.3, "font.size": 10})
warnings.filterwarnings("ignore", category=RuntimeWarning)

_CHECKS = {"pass": 0, "fail": 0}
_FIG = {"n": __FIG_OFFSET__}               # figure numbers run through the whole book
PKG = rt.find_package()                     # the user's RMCProfile package, or None
WORK = tempfile.mkdtemp(prefix="rmcbook-")  # scratch directory for the runs of this chapter

def check(label, ok, detail=""):
    '''Inline physics check; prints PASS/FAIL and tallies for the final summary.'''
    ok = bool(ok)
    _CHECKS["pass" if ok else "fail"] += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    return ok

def skip_without_package(what="this cell"):
    '''True (and a [SKIP] line) when RMCProfile is not installed; the cell then does nothing.'''
    if PKG is None:
        print(f"[SKIP] {what} — set RMCPROFILE_HOME to your RMCProfile_package directory")
        return True
    return False

def caption(text):
    '''Numbered caption rendered directly below the figure it describes.'''
    _FIG["n"] += 1
    display(HTML(
        f"<div style='max-width:780px;margin:2px 0 14px 12px;font-size:0.92em;"
        f"color:#444;border-left:3px solid #bbb;padding-left:10px'>"
        f"<b>Figure {_FIG['n']}.</b> {text}</div>"))

def show(fig):
    '''Display a figure and close it (keeps the notebook small).'''
    plt.show()
    plt.close(fig)

print("rmcprofile-skill", rt.__version__, "| numpy", np.__version__, "| RMCProfile package:",
      (PKG.platform + " build") if PKG else "not set", "| __CHAPTER__")
t_chapter_start = time.time()
"""


def setup_cell(label, fig_offset):
    return code(SETUP_TEMPLATE.replace("__FIG_OFFSET__", str(fig_offset)).replace("__CHAPTER__", label))
