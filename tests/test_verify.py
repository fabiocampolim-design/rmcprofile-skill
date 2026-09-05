# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
import os
import subprocess
import sys

from conftest import ROOT

VERIFY = os.path.join(ROOT, "scripts", "verify_rmcprofile.py")


def test_verify_passes_without_package(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "RMCPROFILE_HOME"}
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run([sys.executable, VERIFY], capture_output=True, text=True, cwd=str(tmp_path), env=env)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "[PASS] imports" in p.stdout
    assert "[PASS] formats round trip" in p.stdout
    assert "[PASS] Keen G(r->0) for SF6" in p.stdout
    assert "[PASS] rock-salt shells" in p.stdout
    assert "[SKIP] package smoke test" in p.stdout
    assert p.stdout.rstrip().endswith("verify_rmcprofile: ALL CHECKS PASSED")


def test_verify_version_flag():
    p = subprocess.run([sys.executable, VERIFY, "--version"], capture_output=True, text=True)
    assert p.returncode == 0 and "rmcprofile-skill" in p.stdout
