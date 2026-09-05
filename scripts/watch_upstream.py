# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Weekly upstream watch for RMCProfile (playbook S8 / rule 23).

RMCProfile has no public source repository reachable from here (code.ornl.gov answers
403 by network range), so the watch reads the surfaces that are documented and public:

  sourceforge   the project's file listing (RSS of sourceforge.net/projects/rmcprofile)
  site          every page and post of rmcprofile.ornl.gov through its WordPress REST API
                (id, slug, modified) -- the download page, change log, posts, tools
  conda         the versions of the GPL side tools on the anaconda.org channel apw247
                (rmc_tools, sofq_calib, topas4rmc)
  github        the neighbouring open-source tools (fullrmc, diffpy, DISCUS, Dissolve,
                ADDIE, Mantid): last push and latest release
  tracker       the reachability of the issue tracker (HTTP status of code.ornl.gov):
                a change from 403 means the door opened

--snapshot   record the current state (JSON) in --state-dir
--weekly     fetch, compare with the previous snapshot, write <outdir>/YYYY-WW.md
             (a second run in the same week appends a section, never overwrites), then snapshot

Usage (from rmcprofile-skill/):
    python scripts/watch_upstream.py --weekly
    python scripts/watch_upstream.py --snapshot --state-dir ../forum/upstream-watch
Requests are anonymous with a descriptive User-Agent, one feed at a time. Every run writes
one audit log under <state-dir>/logs/, on failure too. Exit 0 ok, 1 a feed was unreachable
(the report still lists the feeds that answered), 2 usage error.
"""

import argparse
import datetime
import json
import os
import platform
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
STUDY_ROOT = os.path.normpath(os.path.join(ROOT, ".."))
sys.path.insert(0, HERE)
from rmcprofile_tools import __version__  # noqa: E402

USER_AGENT = "rmcprofile-skill watch (study project; reads public listings only)"
SOURCEFORGE_RSS = "https://sourceforge.net/projects/rmcprofile/rss?path=/"
SITE = "https://rmcprofile.ornl.gov"
SITE_KINDS = ("pages", "posts")
CONDA_CHANNEL = "apw247"
CONDA_PACKAGES = ("rmc_tools", "sofq_calib", "topas4rmc")
GITHUB_NEIGHBOURS = ("bachiraoun/fullrmc", "diffpy/diffpy.cmi", "diffpy/diffpy.pdfgui",
                     "tproffen/DiffuseCode", "disorderedmaterials/dissolve", "neutrons/addie",
                     "mantidproject/mantid")
TRACKER = "https://code.ornl.gov/general/rmcprofile"
FEEDS = ("sourceforge", "site", "conda", "github", "tracker")
_NS = {"media": "http://video.search.yahoo.com/mrss/", "files": "https://sourceforge.net/api/files.rdf#"}


# ------------------------------------------------------------- network seams ---

def _open(url, timeout, accept=None):
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout)


def _get_text(url, timeout=60):
    with _open(url, timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def _get_json(url, timeout=60, accept="application/json"):
    with _open(url, timeout, accept) as r:
        return json.loads(r.read().decode("utf-8"))


def _head_status(url, timeout=60):
    """HTTP status of a GET without following the body; an HTTP error is a status too."""
    try:
        with _open(url, timeout) as r:
            return r.status
    except urllib.error.HTTPError as exc:
        return exc.code


# ------------------------------------------------------------------- feeds ---

def parse_sourceforge_rss(text):
    """[{path, date, size, url}] from the project's file-listing RSS."""
    root = ET.fromstring(text)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        media = item.find("media:content", _NS)
        size = media.get("filesize") if media is not None else None
        out.append({"path": title, "date": (item.findtext("pubDate") or "").strip(),
                    "size": int(size) if size and size.isdigit() else None,
                    "url": (item.findtext("link") or "").strip()})
    return out


def fetch_sourceforge(timeout):
    return parse_sourceforge_rss(_get_text(SOURCEFORGE_RSS, timeout))


def site_entries(kind, payload):
    """[{key, slug, modified, title, link}] from a WordPress REST listing."""
    out = []
    for p in payload:
        title = p.get("title", {})
        out.append({"key": f"{kind}/{p.get('slug', '')}", "slug": p.get("slug", ""),
                    "modified": p.get("modified", ""), "link": p.get("link", ""),
                    "title": title.get("rendered", "") if isinstance(title, dict) else str(title)})
    return out


def fetch_site(timeout):
    out = []
    for kind in SITE_KINDS:
        url = f"{SITE}/wp-json/wp/v2/{kind}?per_page=100&_fields=id,slug,modified,link,title"
        out += site_entries(kind, _get_json(url, timeout))
        time.sleep(0.5)
    return out


def conda_entry(pkg, payload):
    versions = sorted({f.get("version", "") for f in payload.get("files", [])} - {""})
    return {"package": pkg, "latest": payload.get("latest_version", ""), "versions": versions,
            "license": payload.get("license", ""), "home": payload.get("home", "")}


def fetch_conda(timeout):
    out = []
    for pkg in CONDA_PACKAGES:
        out.append(conda_entry(pkg, _get_json(f"https://api.anaconda.org/package/{CONDA_CHANNEL}/{pkg}", timeout)))
        time.sleep(0.5)
    return out


def fetch_github(timeout):
    out = []
    for repo in GITHUB_NEIGHBOURS:
        d = _get_json(f"https://api.github.com/repos/{repo}", timeout, "application/vnd.github+json")
        try:
            rel = _get_json(f"https://api.github.com/repos/{repo}/releases/latest", timeout, "application/vnd.github+json")
        except urllib.error.HTTPError:
            rel = {}
        out.append({"repo": repo, "pushed_at": d.get("pushed_at", ""), "stars": d.get("stargazers_count", 0),
                    "release": rel.get("tag_name", ""), "released_at": rel.get("published_at", "")})
        time.sleep(1.0)
    return out


def fetch_tracker(timeout):
    return [{"url": TRACKER, "status": _head_status(TRACKER, timeout)}]


FETCHERS = {"sourceforge": fetch_sourceforge, "site": fetch_site, "conda": fetch_conda,
            "github": fetch_github, "tracker": fetch_tracker}
KEYS = {"sourceforge": "path", "site": "key", "conda": "package", "github": "repo", "tracker": "url"}
STAMPS = {"sourceforge": ("date", "size"), "site": ("modified",), "conda": ("latest", "versions"),
          "github": ("pushed_at", "release"), "tracker": ("status",)}


# ------------------------------------------------------------------- delta ---

def delta(old, new, key, stamps):
    """Split `new` into new / changed / gone relative to `old` by `key`; `stamps` are the
    fields whose change counts as a change."""
    o = {x[key]: x for x in old}
    n = {x[key]: x for x in new}
    out = {"new": [x for k, x in n.items() if k not in o],
           "changed": [x for k, x in n.items() if k in o and any(x.get(s) != o[k].get(s) for s in stamps)],
           "gone": [x for k, x in o.items() if k not in n]}
    return out


def _line(feed, x):
    if feed == "sourceforge":
        return f"{x['path']} ({x.get('date', '')[:16]}, {x.get('size') or '?'} B)"
    if feed == "site":
        return f"{x['key']} — {x.get('title', '')} (modified {x.get('modified', '')[:10]}) {x.get('link', '')}"
    if feed == "conda":
        return f"{x['package']} latest {x.get('latest', '?')} of {', '.join(x.get('versions', []))}"
    if feed == "github":
        return f"{x['repo']} pushed {x.get('pushed_at', '')[:10]}, release {x.get('release') or '-'} ({x.get('released_at', '')[:10]})"
    return f"{x['url']} → HTTP {x.get('status')}"


def render_weekly(week, deltas, counts, errors, first_run):
    lines = [f"# Upstream watch {week}", "",
             f"Sources: SourceForge file listing, {SITE} (WordPress API), anaconda.org/{CONDA_CHANNEL}, "
             f"GitHub neighbours, the tracker's HTTP status. Checked {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%MZ}."
             + (" First snapshot: every item counts as new." if first_run else ""), ""]
    for feed in FEEDS:
        if feed in errors:
            lines += [f"## {feed}: unreachable — {errors[feed]}", ""]
            continue
        d = deltas[feed]
        lines.append(f"## {feed}: {counts[feed]} total; {len(d['new'])} new, {len(d['changed'])} changed, {len(d['gone'])} gone")
        shown = 0
        for bucket in ("new", "changed", "gone"):
            for x in d[bucket]:
                if shown >= 25:
                    break
                lines.append(f"- [{bucket}] {_line(feed, x)}")
                shown += 1
        rest = sum(len(d[b]) for b in ("new", "changed", "gone")) - shown
        if rest > 0:
            lines.append(f"- … {rest} more (see the snapshot)")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------- state ---

def load_previous(state_dir):
    p = os.path.join(state_dir, "state.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_state(state_dir, data):
    os.makedirs(state_dir, exist_ok=True)
    with open(os.path.join(state_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


def fetch_all(timeout):
    """({feed: items}, {feed: error text}) — one feed failing does not stop the others."""
    data, errors = {}, {}
    for feed in FEEDS:
        try:
            data[feed] = FETCHERS[feed](timeout)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, ET.ParseError) as exc:
            errors[feed] = f"{type(exc).__name__}: {exc}"
    return data, errors


def write_report(outdir, week, md):
    """Write <outdir>/<week>.md; a second run in the same week appends a dated section."""
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{week}.md")
    if os.path.exists(path):
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            f.write(f"\n\n---\n\n# Re-run {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%MZ}\n\n"
                    + md.split("\n", 1)[1])
        return path, "appended"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    return path, "written"


def audit(log_dir, argv, extra):
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc)
    rec = {"tool": "watch_upstream", "version": __version__, "argv": list(argv),
           "utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "python": platform.python_version(),
           "platform": platform.platform()}
    rec.update(extra)
    stem = os.path.join(log_dir, f"watch_upstream_{now:%Y%m%dT%H%M%S}{now.microsecond:06d}Z_{os.getpid()}")
    path, n = stem + ".json", 0
    while os.path.exists(path):           # Windows' clock ticks every ~1-15 ms: two runs of one process can share a stamp
        n += 1
        path = f"{stem}_{n}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, default=str)
    return path


# --------------------------------------------------------------------- cli ---

def build_parser():
    ap = argparse.ArgumentParser(prog="watch_upstream", description=__doc__.splitlines()[0])
    ap.add_argument("--weekly", action="store_true", help="fetch, compare with the previous snapshot, write the report, snapshot")
    ap.add_argument("--snapshot", action="store_true", help="record the current state only")
    ap.add_argument("--state-dir", default=os.path.join(STUDY_ROOT, "forum", "upstream-watch"),
                    help="where the snapshot and logs live (default <study>/forum/upstream-watch)")
    ap.add_argument("--outdir", default=os.path.join(STUDY_ROOT, "docs", "watch"),
                    help="where weekly reports go (default <study>/docs/watch)")
    ap.add_argument("--log-dir", default=None, help="audit-log directory (default <state-dir>/logs)")
    ap.add_argument("--timeout", type=int, default=60, help="seconds per request (default 60)")
    ap.add_argument("-q", "--quiet", action="store_true", help="print only the verdict")
    ap.add_argument("--version", action="version", version=f"rmcprofile-skill {__version__}")
    return ap


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(argv)
    if not (args.weekly or args.snapshot):
        build_parser().print_help()
        return 2
    log_dir = args.log_dir or os.path.join(args.state_dir, "logs")
    week = datetime.date.today().strftime("%G-W%V")
    extra = {"week": week}
    prev = load_previous(args.state_dir)
    data, errors = fetch_all(args.timeout)
    extra["errors"] = errors
    extra["counts"] = {f: len(v) for f, v in data.items()}
    if args.weekly:
        deltas = {f: delta((prev or {}).get("feeds", {}).get(f, []), data[f], KEYS[f], STAMPS[f]) for f in data}
        md = render_weekly(week, deltas, extra["counts"], errors, first_run=prev is None)
        path, how = write_report(args.outdir, week, md)
        extra["written"] = path
        extra["report"] = how
        extra["moved"] = {f: {b: len(d[b]) for b in d} for f, d in deltas.items()}
    # keep the previous snapshot of a feed that did not answer, so a transient failure
    # does not turn next week's whole listing into "new"
    feeds = dict((prev or {}).get("feeds", {}))
    feeds.update(data)
    save_state(args.state_dir, {"taken": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "feeds": feeds})
    log = audit(log_dir, argv, extra)
    if errors:
        for f, e in errors.items():
            print(f"watch_upstream: {f} unreachable: {e}", file=sys.stderr)
    if not args.quiet:
        print(json.dumps({k: v for k, v in extra.items() if k != "errors"}, default=str))
    print(f"watch_upstream {'OK' if not errors else 'PARTIAL'} (log {log})")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
