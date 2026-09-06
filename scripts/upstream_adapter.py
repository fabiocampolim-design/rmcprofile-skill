# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Cross-check rmcprofile-skill against the installed RMCProfile package.

Stages one of the package's shipped tutorial exercises in a scratch directory
(pristine inputs only; outputs removed; .poly/.fs/.sf kept), runs the binary,
and compares our partial g(r) and Keen G(r) for the resulting configuration
with the package's own _PDFpartials.csv and _PDF1.csv. Tolerances and the last
measured values live in tests/records/crosscheck_v1.json.

Usage:
    python scripts/upstream_adapter.py list
    python scripts/upstream_adapter.py crosscheck ex_1 [--home HOME] [--workdir DIR] [--timeout MIN] [--update-records]
    python scripts/upstream_adapter.py --selftest
Exit 0 when every compared quantity is within tolerance, 1 otherwise, 2 without a package,
3 when the exercise has no record yet (run with --update-records to add it).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, field

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rmcprofile_tools as rt  # noqa: E402

RECORDS = os.path.join(HERE, "..", "tests", "records", "crosscheck_v1.json")

# Outputs a run rewrites; never .poly/.fs/.sf (inputs the program waits for).
OUTPUTS = ["*.csv", "*.out", "*.his6f", "*.chi2", "chi2.dat", "chisq0.txt", "derivative.log", "weights.log",
           "weights_update.dat", "*.braggout", "hkls", "*.amp", "*.mamp", "*.log", "*eye.cfg", "error.log",
           "fort.*", "*_OUTPUT.dat", "*.neigh", "*.neighlog", "*_keep"]


@dataclass
class Exercise:
    name: str
    stem: str
    copy: list                                  # directories under tutorial/ whose contents are copied
    extra: list = field(default_factory=list)   # directories whose files are copied next to them
    outputs_to_delete: list = field(default_factory=lambda: list(OUTPUTS))
    time_limit_override: float | None = None    # minutes; None keeps the shipped value
    note: str = ""


EXERCISES = {
    "ex_1": Exercise("ex_1", "rmcsf6_190k", ["ex_1"], note="smoke test, TIME_LIMIT 0"),
    "ex_2": Exercise("ex_2", "rmcsf6_190k", ["ex_2/.rmc_start"], note="10 min refinement"),
    "ex_3": Exercise("ex_3", "rmcsf6_190k", ["ex_3/sf6"], note="10x10x10 supercell, TIME_LIMIT 0"),
    "ex_4_5K": Exercise("ex_4_5K", "srtio3_5k", ["ex_4/5K/rmc/.run"], ["ex_4/5K/data"], note="inputs live in the hidden .run/"),
    "ex_4_293K": Exercise("ex_4_293K", "srtio3_293k", ["ex_4/293K/rmc/.run"], ["ex_4/293K/data"], note="10 min refinement"),
    "ex_6_xray": Exercise("ex_6_xray", "gapo4_xray", ["ex_6/rmc/start"], note="X-ray, TIME_LIMIT 0"),
    "ex_6_neutron": Exercise("ex_6_neutron", "gapo4_neutron", ["ex_6/rmc_neutron/start"], note="filename case breaks Linux (P-10)"),
    "ex_7": Exercise("ex_7", "snao", ["ex_7/RMC"], time_limit_override=5.0, note="EXAFS; shipped TIME_LIMIT 1000 min"),
}


def stage_exercise(pkg, name, workdir):
    """Copy the pristine inputs of `name` into `workdir` (created; must not exist)."""
    ex = EXERCISES[name]
    tut = os.path.join(pkg.home, "tutorial")
    if os.path.exists(workdir):
        raise FileExistsError(workdir)
    os.makedirs(workdir)
    for rel in ex.copy:
        shutil.copytree(os.path.join(tut, rel), workdir, dirs_exist_ok=True)
    for rel in ex.extra:
        src = os.path.join(tut, rel)
        for f in os.listdir(src):
            if os.path.isfile(os.path.join(src, f)):
                shutil.copy2(os.path.join(src, f), workdir)
    for pat in ex.outputs_to_delete:
        for f in glob.glob(os.path.join(workdir, pat)):
            os.remove(f)
    if ex.time_limit_override is not None:
        dat = rt.read_dat(os.path.join(workdir, ex.stem + ".dat"))
        dat.scalars["TIME_LIMIT"] = "%.2f MINUTES" % ex.time_limit_override
        dat.write(os.path.join(workdir, ex.stem + ".dat"))
    return workdir


def crosscheck_partials(rmc6f, partials_csv):
    """max |g_ours - g_theirs| per pair label on RMCProfile's grid."""
    cfg = rt.read_rmc6f(rmc6f)
    r_csv, theirs = rt.read_partials_csv(partials_csv)
    dr = float(np.round(np.diff(r_csv).mean(), 6))
    r, ours = rt.partial_gr(cfg, rmax=r_csv[-1] + 1e-9, dr=dr)
    if len(r) != len(r_csv) or not np.allclose(r, r_csv):
        raise ValueError("grid mismatch: ours %d points to %.3f, theirs %d to %.3f" % (len(r), r[-1], len(r_csv), r_csv[-1]))
    return {lab: float(np.max(np.abs(ours[lab] - theirs[lab]))) for lab in theirs}


def _fit_type(dat_path):
    """FIT_TYPE (else DATA_TYPE) of the first real-space data block of a .dat, 'G(r)' by default."""
    if not dat_path or not os.path.isfile(dat_path):
        return "G(r)"
    dat = rt.read_dat(dat_path)
    for b in dat.blocks:
        if b.name.endswith("REAL_SPACE_DATA"):
            return (b.get("FIT_TYPE") or b.get("DATA_TYPE") or "G(r)").strip()
    return "G(r)"


def crosscheck_gofr(rmc6f, pdf_csv, dat_path=None):
    """max |ours - theirs| against the 'RMC' column of _PDF1.csv / _GofR.csv, in the function
    the exercise fits: G(r) (barn), D(r) = 4 pi r rho G(r) or T(r) = D(r) + 4 pi r rho (sum c b)^2
    (Keen 2001), read from the .dat's FIT_TYPE (0.5.5: the SnO exercise fits D(r) and read 3.6
    'in G(r)' — 4e-5 in D(r))."""
    cfg = rt.read_rmc6f(rmc6f)
    x, calc, _ = rt.read_csv_pair(pdf_csv)
    dr = float(np.round(np.diff(x).mean(), 6))
    r, parts = rt.partial_gr(cfg, rmax=x[-1] + 1e-9, dr=dr)
    _, G = rt.total_gr(r, parts, cfg)
    # the PDF column starts where the data start (SnO: r = 1.40 A), not at r = dr: pick our
    # values on the CSV's own points, r_k = k dr -> index k - 1 (0.5.5, ex_7)
    k = np.round(x / dr).astype(int)
    if k.min() < 1 or k.max() > len(r) or not np.allclose(r[k - 1], x, atol=1e-6):
        raise ValueError("grid mismatch: CSV r from %.3f to %.3f step %.4f is not on r_k = k dr" % (x[0], x[-1], dr))
    ours = G[k - 1]
    kind = _fit_type(dat_path).upper().replace(" ", "")
    if kind.startswith("D(R)") or kind.startswith("T(R)"):
        ours = 4 * np.pi * x * cfg.density * ours
        if kind.startswith("T(R)"):
            n = float(sum(cfg.counts))
            sum_cb = sum(k_ / n * rt.NEUTRON_B[t] for t, k_ in zip(cfg.atom_types, cfg.counts))
            ours = ours + 4 * np.pi * x * cfg.density * (sum_cb ** 2) * rt.BARN_PER_FM2
    return float(np.max(np.abs(ours - calc)))


def run_and_crosscheck(pkg, name, workdir, timeout_min=None):
    ex = EXERCISES[name]
    res = rt.run_rmcprofile(ex.stem, workdir, pkg, timeout_min=timeout_min)
    out = {"exercise": name, "stem": ex.stem, "returncode": res.returncode, "seconds": res.seconds,
           "outputs": res.outputs, "final_chi2": res.final_chi2, "partials": {}, "gofr": None}
    cfg_path = os.path.join(workdir, ex.stem + ".rmc6f")
    parts_csv = os.path.join(workdir, ex.stem + "_PDFpartials.csv")
    pdf_csv = os.path.join(workdir, ex.stem + "_PDF1.csv")
    # a configuration our reader refuses (the shipped GaPO4 neutron start declares 576 atoms and
    # holds 575, P-22) is a finding to report, not a traceback that ends the audit (0.5.5)
    try:
        if os.path.isfile(parts_csv):
            out["partials"] = crosscheck_partials(cfg_path, parts_csv)
        if os.path.isfile(pdf_csv):
            out["gofr"] = crosscheck_gofr(cfg_path, pdf_csv, os.path.join(workdir, ex.stem + ".dat"))
            out["gofr_type"] = _fit_type(os.path.join(workdir, ex.stem + ".dat"))
    except ValueError as exc:
        out["error"] = str(exc)
    return out


def load_records():
    with open(RECORDS, encoding="utf-8") as f:
        return json.load(f)


def save_records(rec):
    with open(RECORDS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")


def within_tolerance(result, rec):
    """True/False against the exercise's record; None when there is no record for it (an
    exercise never recorded is not a failure — 0.5.5, after every exercise but ex_1 read
    'False' on the 6.8.0-rc.1 audit). G(r) is compared only when the run produced a PDF
    column (an X-ray-only exercise has none)."""
    e = rec["exercises"].get(result["exercise"])
    if e is None:
        return None
    if result.get("error") or not result["partials"]:
        return False
    ok = max(result["partials"].values()) <= e["tolerance_partials"]
    if result["gofr"] is not None:
        ok = ok and result["gofr"] <= e["tolerance_gofr"]
    return ok


def _audit(log_dir, argv, ok, extra):
    os.makedirs(log_dir, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%dT%H%M%S%f")
    with open(os.path.join(log_dir, "upstream_adapter_%s.json" % stamp), "w", encoding="utf-8") as f:
        json.dump({"tool": "upstream_adapter", "version": rt.__version__, "argv": list(argv), "ok": bool(ok), **extra}, f, indent=2)


def _nacl(n=2, a=5.64):
    """Rock-salt NaCl supercell for the selftest (the adapter must not import from tests/)."""
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


def selftest(outdir):
    """The cross-check must be exact on our own pdf-command output."""
    os.makedirs(outdir, exist_ok=True)
    cfg = _nacl(2)
    p = os.path.join(outdir, "selftest.rmc6f")
    cfg.write(p)
    rc = rt.main(["pdf", p, "--rmax", "5", "--outdir", outdir, "--log-dir", os.path.join(outdir, "logs"), "-q"])
    checks = [{"name": "pdf command", "ok": rc == 0, "detail": ""}]
    d = crosscheck_partials(p, os.path.join(outdir, "selftest_PDFpartials.csv"))
    checks.append({"name": "partials exact on our own CSV", "ok": max(d.values()) < 1e-8, "detail": "%.1e" % max(d.values())})
    g = crosscheck_gofr(p, os.path.join(outdir, "selftest_GofR.csv"))
    checks.append({"name": "G(r) exact on our own CSV", "ok": g < 1e-8, "detail": "%.1e" % g})
    return checks


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--outdir", default="out", help="where selftest files are written")
    common.add_argument("--log-dir", default="logs", help="where the JSON audit log is written")
    common.add_argument("-q", "--quiet", action="store_true", help="print only the verdict")
    ap = argparse.ArgumentParser(prog="upstream_adapter", description=__doc__.splitlines()[0], parents=[common])
    ap.add_argument("--version", action="version", version="rmcprofile-skill %s" % rt.__version__)
    ap.add_argument("--selftest", action="store_true", help="cross-check our own pdf output against itself (exact)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list", help="list the exercises the adapter knows", parents=[common])
    c = sub.add_parser("crosscheck", help="stage, run and cross-check one shipped exercise", parents=[common])
    c.add_argument("exercise", choices=sorted(EXERCISES))
    c.add_argument("--home", default=None, help="RMCProfile_package directory (default: $RMCPROFILE_HOME)")
    c.add_argument("--workdir", default=None, help="scratch directory (default: a fresh temp dir)")
    c.add_argument("--timeout", type=float, default=None, help="kill the run after this many minutes")
    c.add_argument("--update-records", action="store_true",
                   help="write the measured maxima into tests/records/crosscheck_v1.json")
    return ap


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(argv)
    if args.selftest:
        checks = selftest(args.outdir)
        ok = all(c["ok"] for c in checks)
        if not args.quiet:
            for c in checks:
                print("[%s] %s%s" % ("PASS" if c["ok"] else "FAIL", c["name"], (" - " + c["detail"]) if c["detail"] else ""))
        _audit(args.log_dir, argv, ok, {"checks": checks})
        print("upstream_adapter selftest: %s" % ("ALL CHECKS PASSED" if ok else "FAILED"))
        return 0 if ok else 1
    if args.cmd == "list":
        for name, ex in EXERCISES.items():
            print("%-13s stem=%-13s from %s%s  %s" % (name, ex.stem, "+".join(ex.copy),
                                                     (" +" + "+".join(ex.extra)) if ex.extra else "", ex.note))
        return 0
    if args.cmd == "crosscheck":
        pkg = rt.find_package(args.home)
        if pkg is None:
            print("ERROR: no RMCProfile package: pass --home or set RMCPROFILE_HOME")
            return 2
        work = args.workdir or os.path.join(tempfile.mkdtemp(prefix="rmc-crosscheck-"), args.exercise)
        stage_exercise(pkg, args.exercise, work)
        res = run_and_crosscheck(pkg, args.exercise, work, timeout_min=args.timeout)
        rec = load_records()
        ok = within_tolerance(res, rec)
        if not args.quiet:
            print("%s: rc=%s %.0f s chi2=%s" % (args.exercise, res["returncode"], res["seconds"],
                                             res["final_chi2"].get("chi2") if res["final_chi2"] else "n/a"))
            for lab, v in res["partials"].items():
                print("  partial %-6s max|diff| = %.2e" % (lab, v))
            print("  %-13s max|diff| = %s" % (res.get("gofr_type", "G(r)"), "%.2e" % res["gofr"] if res["gofr"] is not None else "n/a"))
            if res.get("error"):
                print("  reader error: %s" % res["error"])
            print("  within tolerance: %s (work dir %s)" % ("no record for this exercise (add it with --update-records)" if ok is None else ok, work))
        if args.update_records and res["partials"]:
            e = rec["exercises"].setdefault(args.exercise, {"stem": res["stem"], "tolerance_partials": 1e-3, "tolerance_gofr": 1e-4})
            e["measured"] = {"partials": res["partials"], "gofr": res["gofr"]}
            e["provenance"] = "RMCProfile %s %s build, %s" % (pkg.version_hint or "6.7.9", pkg.platform, _dt.date.today().isoformat())
            save_records(rec)
        _audit(args.log_dir, argv, bool(ok), {"result": res, "workdir": work})
        return 3 if ok is None else (0 if ok else 1)
    build_parser().print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
