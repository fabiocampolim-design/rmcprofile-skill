# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Environment and physics smoke test for rmcprofile-skill.

Checks, in order:
  1. imports and versions (numpy, scipy, matplotlib)
  2. formats round trip (the toolkit's --selftest checks, in a temp dir)
  3. Keen G(r->0) for SF6 = -(sum c_i b_i)^2 = -0.2759 barn
  4. rock-salt shells: partial g(r) first shells at a/2 and a/sqrt(2), 6 Cl around Na
  5. rmclite recovery: the teaching engine's selftest (2x2x2 rock salt, 2000 moves)
  6. package smoke test when RMCPROFILE_HOME (or --home) points at RMCProfile_package:
     tutorial/ex_1 copied to a temp dir, run for at most --minutes; SKIP otherwise
  7. package cross-check: our partials and G(r) versus the smoke test's own CSVs,
     within the tolerances of tests/records/crosscheck_v1.json; SKIP without the package

Usage:
    python scripts/verify_rmcprofile.py [-q] [--home PATH] [--minutes 3]
    python scripts/verify_rmcprofile.py --version
Exit code 0 when every check passes, 1 otherwise.
"""

import argparse
import os
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rmcprofile_tools as rt  # noqa: E402


def build_parser():
    ap = argparse.ArgumentParser(prog="verify_rmcprofile", description=__doc__.splitlines()[0])
    ap.add_argument("-q", "--quiet", action="store_true", help="print only the final verdict")
    ap.add_argument("--home", default=None, help="RMCProfile_package directory (default: $RMCPROFILE_HOME)")
    ap.add_argument("--minutes", type=float, default=3.0, help="time cap for the package smoke test")
    ap.add_argument("--version", action="version", version="rmcprofile-skill %s" % rt.__version__)
    return ap


def _nacl(n=2, a=5.64):
    base = {"Na": [(0, 0, 0), (.5, .5, 0), (.5, 0, .5), (0, .5, .5)],
            "Cl": [(.5, 0, 0), (0, .5, 0), (0, 0, .5), (.5, .5, .5)]}
    atoms, frac = [], []
    for el in ("Na", "Cl"):
        for i, j, k in np.ndindex(n, n, n):
            for x, y, z in base[el]:
                atoms.append(el)
                frac.append([(x + i) / n, (y + j) / n, (z + k) / n])
    N = len(atoms)
    return rt.Rmc6f(atom_types=["Na", "Cl"], counts=[N // 2, N // 2], cell=(n * a,) * 3 + (90.0,) * 3,
                    lattice=n * a * np.eye(3), supercell=(n, n, n), density=N / (n * a) ** 3,
                    atoms=np.array(atoms, dtype=object), frac=np.array(frac),
                    site=np.arange(1, N + 1), cellidx=np.zeros((N, 3), int))


def main(argv=None):
    args = build_parser().parse_args(argv)
    all_ok = True

    def check(label, ok, detail=""):
        nonlocal all_ok
        all_ok &= bool(ok)
        if not args.quiet:
            print("[%s] %s%s" % ("PASS" if ok else "FAIL", label, (" - " + detail) if detail else ""))

    import matplotlib
    import scipy
    check("imports", True, "numpy %s, scipy %s, matplotlib %s" % (np.__version__, scipy.__version__, matplotlib.__version__))

    with tempfile.TemporaryDirectory() as tmp:
        checks = rt.selftest(tmp)
        check("formats round trip", all(c["ok"] for c in checks),
              "; ".join(c["name"] for c in checks if not c["ok"]) or "%d checks" % len(checks))

    sf6 = rt.Rmc6f(atom_types=["S", "F"], counts=[1, 6])
    g0 = -sum(rt.neutron_weights(sf6).values())
    check("Keen G(r->0) for SF6", abs(g0 + 0.2759) < 5e-4, "%.4f barn" % g0)

    cfg = _nacl(2)
    r, parts = rt.partial_gr(cfg, rmax=5.0, dr=0.02)
    p1 = r[np.nonzero(parts["Na-Cl"])[0][0]]
    p2 = r[np.nonzero(parts["Na-Na"])[0][0]]
    _, hist = rt.coordination(cfg, "Na", "Cl", 3.0)
    check("rock-salt shells", abs(p1 - 2.82) < 0.02 and abs(p2 - 3.988) < 0.02 and hist == {6: cfg.counts[0]},
          "Na-Cl %.2f, Na-Na %.3f, CN %s" % (p1, p2, hist))

    import rmclite as rl
    rl_checks = rl.selftest(tempfile.mkdtemp(prefix="rmclite-verify-"))
    check("rmclite recovery", all(c["ok"] for c in rl_checks), rl_checks[0]["detail"])

    pkg = rt.find_package(args.home)
    if pkg is None:
        if not args.quiet:
            print("[SKIP] package smoke test - set RMCPROFILE_HOME to the RMCProfile_package directory")
            print("[SKIP] package cross-check - needs the package")
    else:
        import upstream_adapter as ua
        src = os.path.join(pkg.home, "tutorial", "ex_1")
        with tempfile.TemporaryDirectory() as tmp:
            work = os.path.join(tmp, "ex_1")
            shutil.copytree(src, work)
            errs = [f for f in rt.check_input_set("rmcsf6_190k", work) if f.level == "ERROR"]
            res = rt.run_rmcprofile("rmcsf6_190k", work, pkg, timeout_min=args.minutes) if not errs else None
            ok = res is not None and res.returncode == 0 and any(o.endswith("_SQ1.csv") for o in res.outputs)
            check("package smoke test", ok, "%s (%s build), rc=%s, %.0f s, %d outputs, chi2 %s"
                  % (pkg.home, pkg.platform, res.returncode if res else "n/a", res.seconds if res else 0,
                     len(res.outputs) if res else 0, res.final_chi2.get("chi2") if res and res.final_chi2 else "n/a"))
            if ok:
                parts = ua.crosscheck_partials(os.path.join(work, "rmcsf6_190k.rmc6f"), os.path.join(work, "rmcsf6_190k_PDFpartials.csv"))
                gofr = ua.crosscheck_gofr(os.path.join(work, "rmcsf6_190k.rmc6f"), os.path.join(work, "rmcsf6_190k_PDF1.csv"))
                tol = ua.load_records()["exercises"]["ex_1"]
                check("package cross-check", max(parts.values()) <= tol["tolerance_partials"] and gofr <= tol["tolerance_gofr"],
                      "partials max %.1e, G(r) max %.1e barn (tolerances %.0e / %.0e)"
                      % (max(parts.values()), gofr, tol["tolerance_partials"], tol["tolerance_gofr"]))
            else:
                check("package cross-check", False, "smoke test did not run")

    print("verify_rmcprofile: %s" % ("ALL CHECKS PASSED" if all_ok else "FAILED"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
