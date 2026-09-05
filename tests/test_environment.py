# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
import os
import sys

from conftest import ROOT


def test_python_is_3_12_or_newer():
    assert sys.version_info >= (3, 12)


def test_scientific_stack_imports():
    import matplotlib
    import numpy
    import scipy
    assert int(numpy.__version__.split(".")[0]) >= 2
    assert scipy.__version__ and matplotlib.__version__


def test_environment_files_agree():
    with open(os.path.join(ROOT, "environment-rmcprofile.yml"), encoding="utf-8") as f:
        yml = f.read()
    with open(os.path.join(ROOT, "requirements.txt"), encoding="utf-8") as f:
        req = f.read()
    for pkg in ("numpy", "scipy", "matplotlib", "pytest", "pyflakes", "nbconvert", "ipykernel"):
        assert pkg in yml and pkg in req, pkg
    assert "name: rmcprofile" in yml
    assert "RMCPROFILE_HOME" in req          # the manual-install note must stay


def test_package_layout_when_available(package_home):
    """RMCPROFILE_HOME points at RMCProfile_package: exe/ with the binary, tutorial/ with ex_1..ex_7."""
    exe = os.path.join(package_home, "exe")
    assert os.path.isfile(os.path.join(exe, "rmcprofile.exe")) or os.path.isfile(os.path.join(exe, "rmcprofile"))
    tut = os.path.join(package_home, "tutorial")
    assert {"ex_1", "ex_2", "ex_3", "ex_4", "ex_6", "ex_7"} <= set(os.listdir(tut))
