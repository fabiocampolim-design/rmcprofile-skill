# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Shared fixtures. Run from rmcprofile-skill/:  python -m pytest tests

Package-bound tests need RMCPROFILE_HOME (the RMCProfile_package directory that
holds exe/ and tutorial/); they skip without it."""

import os
import sys

import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


@pytest.fixture(scope="session")
def repo_root():
    return ROOT


@pytest.fixture(scope="session")
def package_home():
    home = os.environ.get("RMCPROFILE_HOME")
    if not home or not os.path.isdir(os.path.join(home, "exe")):
        pytest.skip("RMCPROFILE_HOME not set to an RMCProfile_package directory")
    return home
