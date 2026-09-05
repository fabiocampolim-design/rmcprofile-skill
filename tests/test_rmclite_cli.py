# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
import glob
import json
import os
import subprocess
import sys

import numpy as np

import rmclite as rl
import rmcprofile_tools as rt
from conftest import ROOT
from test_analysis import nacl

SCRIPT = os.path.join(ROOT, "scripts", "rmclite.py")


def _run(args, cwd):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, cwd=cwd,
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})


def test_parse_min_dist():
    assert rl.parse_min_dist("Na-Na:3.0, Na-Cl:2.2") == {"Na-Na": 3.0, "Na-Cl": 2.2}


def test_synth_then_fit_round_trip(tmp_path):
    """synth writes the input's partials as targets plus a displaced copy of it;
    fit from the *average structure* (the ideal lattice, as a real RMCProfile
    run starts from a data2config supercell) toward the partials of a thermally
    displaced 'truth' must cut chi2 by > 80 % in 3000 moves."""
    cfg = nacl(2)
    ideal = tmp_path / "nacl.rmc6f"
    cfg.write(ideal)
    rng = np.random.default_rng(1)
    truth = rl.Box.from_rmc6f(cfg)
    truth.frac = (truth.frac + rng.normal(0, 0.05, truth.frac.shape) / 11.28) % 1.0
    truth.to_rmc6f(cfg).write(tmp_path / "truth.rmc6f")
    rc = rl.main(["synth", str(tmp_path / "truth.rmc6f"), "--displace", "0.05", "--rmax", "5", "--seed", "1",
                  "--outdir", str(tmp_path), "--log-dir", str(tmp_path / "logs"), "-q"])
    assert rc == 0
    assert (tmp_path / "truth_displaced.rmc6f").is_file() and (tmp_path / "truth_target_PDFpartials.csv").is_file()
    rc = rl.main(["fit", str(ideal), "--target", str(tmp_path / "truth_target_PDFpartials.csv"),
                  "--moves", "3000", "--sigma", "0.2", "--min-dist", "Na-Na:3.0,Na-Cl:2.2,Cl-Cl:3.0", "--max-move", "0.05",
                  "--seed", "2", "--outdir", str(tmp_path), "--log-dir", str(tmp_path / "logs"), "-q"])
    assert rc == 0
    h = rt.read_chi2_history(str(tmp_path / "nacl_fit.chi2"))
    assert list(h)[:4] == ["m_accepted", "m_generated", "m_tested", "chi2"]
    assert h["chi2"][-1] < 0.2 * h["chi2"][0] and h["m_generated"][-1] == 3000
    fit = rt.read_rmc6f(str(tmp_path / "nacl_fit.rmc6f"))
    assert fit.n_atoms() == 64
    r, parts = rt.read_partials_csv(str(tmp_path / "nacl_fit_PDFpartials.csv"))
    assert list(parts) == ["Na-Na", "Na-Cl", "Cl-Cl"] and np.isclose(r[0], 0.02)
    logs = glob.glob(str(tmp_path / "logs" / "rmclite_*.json"))
    assert len(logs) == 2 and json.load(open(logs[-1], encoding="utf-8"))["ok"] is True


def test_selftest_and_version(tmp_path):
    p = _run(["--selftest", "--outdir", str(tmp_path), "--log-dir", str(tmp_path / "logs"), "-q"], ROOT)
    assert p.returncode == 0, p.stdout + p.stderr
    p = _run(["--version"], ROOT)
    assert p.returncode == 0 and "rmcprofile-skill" in p.stdout
