# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""rmclite's calculated functions are RMCProfile's by construction: the same
histogram on the same grid. Prove it on the package's smoke-test files, and
show that rmclite started *on* that configuration against its own partials
sits at chi2 = 0 and stays there when every move is rejected by the data."""

import json
import os

import numpy as np

import rmclite as rl
import rmcprofile_tools as rt
from conftest import ROOT


def test_rmclite_histogram_equals_rmcprofile_partials(package_home):
    d = os.path.join(package_home, "tutorial", "ex_1")
    cfg = rt.read_rmc6f(os.path.join(d, "rmcsf6_190k.rmc6f"))
    r_csv, theirs = rt.read_partials_csv(os.path.join(d, "rmcsf6_190k_PDFpartials.csv"))
    h = rl.Histogram(rl.Box.from_rmc6f(cfg), rmax=r_csv[-1] + 1e-9, dr=0.02)
    ours = h.g()
    assert np.allclose(h.r, r_csv)
    with open(os.path.join(ROOT, "tests", "records", "crosscheck_v1.json"), encoding="utf-8") as f:
        rec = json.load(f)["rmclite"]["ex_1"]
    for lab in theirs:
        assert np.max(np.abs(ours[lab] - theirs[lab])) < rec["partials_tolerance"], lab
    x, calc, _ = rt.read_csv_pair(os.path.join(d, "rmcsf6_190k_PDF1.csv"))
    w = rt.neutron_weights(cfg)
    G = sum(w[lab] * (ours[lab] - 1.0) for lab in ours)
    assert np.max(np.abs(G - calc)) < rec["gofr_tolerance"]


def test_rmclite_on_the_package_configuration_starts_near_zero(package_home):
    d = os.path.join(package_home, "tutorial", "ex_1")
    cfg = rt.read_rmc6f(os.path.join(d, "rmcsf6_190k.rmc6f"))
    r_csv, theirs = rt.read_partials_csv(os.path.join(d, "rmcsf6_190k_PDFpartials.csv"))
    eng = rl.RmcLite(rl.Box.from_rmc6f(cfg), r_csv[-1] + 1e-9, 0.02,
                     [rl.PartialTarget(lab, r_csv, theirs[lab], sigma=0.01) for lab in theirs],
                     constraints=[rl.ClosestApproach({"S-S": 4.0, "S-F": 1.2, "F-F": 1.8})],
                     max_move={"S": 0.05, "F": 0.1}, seed=0)
    chi0 = eng.chi2
    assert chi0 < 1.0                       # single-precision residue of the package's CSV, over 3 x 441 points
    st = eng.run(300)
    assert eng.chi2 <= chi0 + 1e-9 and st.generated == 300
