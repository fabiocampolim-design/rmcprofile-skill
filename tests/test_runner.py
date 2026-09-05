# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Package locator and runner. The fake-package tests run everywhere; the real
run needs RMCPROFILE_HOME and a copy of the package's own smoke test (ex_1)."""

import os
import shutil
import stat
import sys

import pytest

import rmcprofile_tools as rt


def _fake_package(root, platform):
    exe = root / "exe"
    exe.mkdir(parents=True)
    (root / "tutorial").mkdir()
    if platform == "windows":
        (exe / "rmcprofile.exe").write_text("", encoding="utf-8")
        (exe / "cygwin_libs").mkdir()
        (exe / "cuda_lib").mkdir()
    else:
        p = exe / "rmcprofile"
        p.write_text("#!/bin/sh\necho fake\n", encoding="utf-8")
        p.chmod(p.stat().st_mode | stat.S_IXUSR)
        (exe / "libs").mkdir()
    return root


def test_find_package_from_argument_and_env(tmp_path, monkeypatch):
    home = _fake_package(tmp_path / "pkg", "windows" if os.name == "nt" else "linux")
    monkeypatch.delenv("RMCPROFILE_HOME", raising=False)
    assert rt.find_package() is None
    pkg = rt.find_package(str(home))
    assert pkg.home == str(home) and os.path.isfile(pkg.binary)
    monkeypatch.setenv("RMCPROFILE_HOME", str(home))
    assert rt.find_package().home == str(home)
    assert rt.find_package(str(tmp_path / "nowhere")) is None


def test_package_env_matches_the_setup_scripts(tmp_path):
    home = _fake_package(tmp_path / "pkg", "windows")
    env = rt.package_env(rt.Package(str(home), "windows", str(home / "exe" / "rmcprofile.exe"), ""))
    assert env["RMCPROFILE_DIR"] == str(home)
    assert env["PATH"].startswith(os.pathsep.join([str(home / "exe"), str(home / "exe" / "cygwin_libs"),
                                                   str(home / "exe" / "cuda_lib")]))
    home2 = _fake_package(tmp_path / "pkg2", "linux")
    env = rt.package_env(rt.Package(str(home2), "linux", str(home2 / "exe" / "rmcprofile"), ""))
    libs = str(home2 / "exe" / "libs")
    assert env["PGPLOT_DIR"] == libs and env["LD_LIBRARY_PATH"] == libs and env["LIBRARY_PATH"] == libs
    assert env["RMCProfile_PATH"] == str(home2) and env["PATH"].endswith(str(home2 / "exe"))


@pytest.mark.skipif(sys.platform == "win32", reason="shell-script fake binary")
def test_run_collects_log_outputs_and_final_chi2(tmp_path):
    home = _fake_package(tmp_path / "pkg", "linux")
    script = home / "exe" / "rmcprofile"
    script.write_text("#!/bin/sh\necho running $1\nprintf 'm_accepted m_generated chi2\\n 1 2 0.5\\n' > $1.chi2\necho done\n",
                      encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    (work / "s.dat").write_text("TITLE :: x\nEND ::\n", encoding="utf-8")
    res = rt.run_rmcprofile("s", work, rt.find_package(str(home)), timeout_min=1)
    assert res.returncode == 0 and res.seconds >= 0
    assert os.path.isfile(res.log_path) and "running s" in open(res.log_path, encoding="utf-8").read()
    assert "s.chi2" in res.outputs
    assert res.final_chi2 == {"m_accepted": 1, "m_generated": 2, "chi2": 0.5}


def test_real_smoke_test_when_package_available(package_home, tmp_path):
    """The package's own smoke test (tutorial/ex_1) in a scratch copy; its
    TIME_LIMIT is 0 (one pass), a few seconds on either build."""
    src = os.path.join(package_home, "tutorial", "ex_1")
    work = tmp_path / "ex_1"
    shutil.copytree(src, work)
    assert [f.code for f in rt.check_input_set("rmcsf6_190k", work) if f.level == "ERROR"] == []
    res = rt.run_rmcprofile("rmcsf6_190k", work, rt.find_package(package_home), timeout_min=3)
    assert res.returncode == 0, open(res.log_path, encoding="utf-8").read()[-2000:]
    assert any(o.endswith("_SQ1.csv") for o in res.outputs)
    assert res.final_chi2 and res.final_chi2["chi2"] == pytest.approx(0.4201, abs=1e-4)
