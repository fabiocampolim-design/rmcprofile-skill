# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""scripts/watch_upstream.py — pure functions, the parser, an offline end-to-end run and
the scheduler script; no network (the three fetch seams are faked)."""

import json
import os
import shutil
import subprocess
import sys
import urllib.error

import pytest

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import watch_upstream as wu  # noqa: E402

RSS = """<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:media="http://video.search.yahoo.com/mrss/" xmlns:files="https://sourceforge.net/api/files.rdf#" version="2.0">
<channel><title>RMCProfile</title>
<item><title>/RMCProfile_V6.7.9_Windows_Serial.zip</title><link>https://sourceforge.net/x/a.zip/download</link>
<pubDate>Wed, 04 Jun 2025 18:48:10 UT</pubDate><media:content filesize="123456" url="u"/></item>
<item><title>/old/RMCProfile_V6.5.2_Linux_64.zip</title><link>https://sourceforge.net/x/b.zip/download</link>
<pubDate>Mon, 01 Jan 2018 00:00:00 UT</pubDate></item>
</channel></rss>"""


def test_parse_sourceforge_rss_reads_path_date_size():
    items = wu.parse_sourceforge_rss(RSS)
    assert [i["path"] for i in items] == ["/RMCProfile_V6.7.9_Windows_Serial.zip", "/old/RMCProfile_V6.5.2_Linux_64.zip"]
    assert items[0]["size"] == 123456 and items[1]["size"] is None
    assert items[0]["date"].startswith("Wed, 04 Jun 2025") and items[0]["url"].endswith("/download")


def test_site_entries_keys_by_kind_and_slug():
    e = wu.site_entries("posts", [{"slug": "a-post", "modified": "2026-06-15T10:00:00", "link": "L",
                                   "title": {"rendered": "A post"}}])
    assert e == [{"key": "posts/a-post", "slug": "a-post", "modified": "2026-06-15T10:00:00", "link": "L", "title": "A post"}]


def test_conda_entry_collects_versions():
    e = wu.conda_entry("rmc_tools", {"latest_version": "0.0.1", "license": "GPL", "home": "h",
                                     "files": [{"version": "0.0.1"}, {"version": "0.0.1"}, {"version": ""}]})
    assert e["versions"] == ["0.0.1"] and e["latest"] == "0.0.1" and e["license"] == "GPL"


def test_delta_new_changed_gone():
    old = [{"k": "a", "s": 1}, {"k": "b", "s": 1}, {"k": "c", "s": 1}]
    new = [{"k": "a", "s": 1}, {"k": "b", "s": 2}, {"k": "d", "s": 1}]
    d = wu.delta(old, new, "k", ("s",))
    assert [x["k"] for x in d["new"]] == ["d"]
    assert [x["k"] for x in d["changed"]] == ["b"]
    assert [x["k"] for x in d["gone"]] == ["c"]


def test_render_weekly_lists_every_feed_and_unreachable_ones():
    deltas = {f: {"new": [], "changed": [], "gone": []} for f in wu.FEEDS}
    deltas["tracker"]["changed"] = [{"url": wu.TRACKER, "status": 200}]
    deltas["conda"]["new"] = [{"package": "rmc_tools", "latest": "0.0.2", "versions": ["0.0.1", "0.0.2"]}]
    counts = {f: 1 for f in wu.FEEDS}
    md = wu.render_weekly("2026-W36", deltas, counts, {"github": "URLError: offline"}, first_run=False)
    assert md.startswith("# Upstream watch 2026-W36")
    assert "## github: unreachable — URLError: offline" in md
    assert "## tracker: 1 total; 0 new, 1 changed, 0 gone" in md and "HTTP 200" in md
    assert "rmc_tools latest 0.0.2 of 0.0.1, 0.0.2" in md
    assert "First snapshot" not in md
    assert "First snapshot" in wu.render_weekly("2026-W36", deltas, counts, {}, first_run=True)


def test_cli_parser_and_no_mode_exit_2():
    ns = wu.build_parser().parse_args(["--weekly", "--state-dir", "s", "--outdir", "o", "--timeout", "5"])
    assert ns.weekly and ns.state_dir == "s" and ns.outdir == "o" and ns.timeout == 5
    assert wu.main([]) == 2


def _fake_network(monkeypatch, tracker_status=403, fail=()):
    site = {"pages": [{"slug": "download", "modified": "2026-08-03T12:00:00", "link": "L", "title": {"rendered": "Download"}}],
            "posts": [{"slug": "p1", "modified": "2026-06-15T00:00:00", "link": "L", "title": {"rendered": "Post"}}]}

    def get_text(url, timeout=60):
        if "sourceforge" in fail:
            raise urllib.error.URLError("offline")
        return RSS

    def get_json(url, timeout=60, accept=None):
        if "wp-json" in url:
            if "site" in fail:
                raise urllib.error.URLError("offline")
            return site["pages"] if "/pages" in url else site["posts"]
        if "anaconda" in url:
            if "conda" in fail:
                raise urllib.error.URLError("offline")
            return {"latest_version": "0.0.1", "files": [{"version": "0.0.1"}], "license": "GPL", "home": "h"}
        if "api.github.com" in url:
            if "github" in fail:
                raise urllib.error.URLError("offline")
            if url.endswith("/releases/latest"):
                raise urllib.error.HTTPError(url, 404, "no release", {}, None)
            return {"pushed_at": "2026-09-01T00:00:00Z", "stargazers_count": 3}
        raise AssertionError(url)

    monkeypatch.setattr(wu, "_get_text", get_text)
    monkeypatch.setattr(wu, "_get_json", get_json)
    monkeypatch.setattr(wu, "_head_status", lambda url, timeout=60: tracker_status)
    monkeypatch.setattr(wu.time, "sleep", lambda s: None)


def test_weekly_offline_end_to_end_and_second_run_appends(tmp_path, monkeypatch):
    _fake_network(monkeypatch)
    state, out = tmp_path / "state", tmp_path / "out"
    assert wu.main(["--weekly", "--state-dir", str(state), "--outdir", str(out), "-q"]) == 0
    reports = os.listdir(out)
    assert len(reports) == 1 and reports[0].endswith(".md")
    md = (out / reports[0]).read_text(encoding="utf-8")
    assert "First snapshot" in md and "## sourceforge: 2 total; 2 new" in md and "## site: 2 total; 2 new" in md
    assert "## conda: 3 total; 3 new" in md and "## tracker: 1 total; 1 new" in md and "HTTP 403" in md
    assert (state / "state.json").exists() and [p for p in os.listdir(state / "logs") if p.startswith("watch_upstream_")]
    # the tracker opens: a changed row, appended to the same week's report, nothing overwritten
    _fake_network(monkeypatch, tracker_status=200)
    assert wu.main(["--weekly", "--state-dir", str(state), "--outdir", str(out), "-q"]) == 0
    md2 = (out / reports[0]).read_text(encoding="utf-8")
    assert md2.startswith(md) and "# Re-run" in md2
    assert "## tracker: 1 total; 0 new, 1 changed, 0 gone" in md2 and "## sourceforge: 2 total; 0 new, 0 changed, 0 gone" in md2


def test_one_unreachable_feed_keeps_the_report_exits_1_and_keeps_its_old_snapshot(tmp_path, monkeypatch, capsys):
    _fake_network(monkeypatch)
    state, out = tmp_path / "state", tmp_path / "out"
    assert wu.main(["--snapshot", "--state-dir", str(state), "-q"]) == 0
    _fake_network(monkeypatch, fail={"github"})
    rc = wu.main(["--weekly", "--state-dir", str(state), "--outdir", str(out), "-q"])
    assert rc == 1 and "github unreachable" in capsys.readouterr().err
    md = (out / os.listdir(out)[0]).read_text(encoding="utf-8")
    assert "## github: unreachable" in md and "## site: 2 total" in md
    with open(state / "state.json", encoding="utf-8") as f:
        feeds = json.load(f)["feeds"]
    assert len(feeds["github"]) == len(wu.GITHUB_NEIGHBOURS)        # the previous snapshot survived
    logs = os.listdir(state / "logs")
    assert len(logs) == 2


def test_log_dir_flag_names_the_log_directory_itself(tmp_path, monkeypatch):
    _fake_network(monkeypatch)
    logs = tmp_path / "mylogs"
    assert wu.main(["--snapshot", "--state-dir", str(tmp_path / "s"), "--log-dir", str(logs), "-q"]) == 0
    assert [p for p in os.listdir(logs) if p.startswith("watch_upstream_")]
    assert not (tmp_path / "s" / "logs").exists()


def _powershell():
    return shutil.which("powershell") or shutil.which("pwsh")


@pytest.mark.skipif(_powershell() is None, reason="no PowerShell on this host")
def test_register_watch_task_dry_run_and_version():
    path = os.path.join(ROOT, "scripts", "register_watch_task.ps1")
    with open(path, encoding="utf-8") as f:
        assert "SPDX-License-Identifier: Apache-2.0" in f.read(400)
    ps = _powershell()
    r = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", path, "-DryRun"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert "DRY-RUN" in r.stdout and "Register-ScheduledTask" in r.stdout and "watch_upstream.py" in r.stdout
    r = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", path, "-Version"],
                       capture_output=True, text=True, timeout=120)
    with open(os.path.join(ROOT, "VERSION"), encoding="utf-8") as f:
        assert r.returncode == 0 and r.stdout.strip() == "rmcprofile-skill " + f.read().strip()
