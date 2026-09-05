# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fabio Campolim
"""Build the README gallery from the executed chapters.

For every chapter in ``assemble.CHAPTERS`` the first figure (the first ``image/png``
output) is written to ``docs/figures/<file stem>.png`` and a Markdown table of the
figures with their captions replaces the block between ``<!-- gallery:start -->`` and
``<!-- gallery:end -->`` in ``README.md``. Chapters without an executed figure are
skipped with a log line, never invented.

    python build/gallery.py            # rewrite docs/figures and the README block
    python build/gallery.py --check    # exit 1 if the README block is stale
"""
import argparse
import base64
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import CHAPTERS, ROOT, CHAPTERS_DIR  # noqa: E402
from buildlog import AuditLog  # noqa: E402

log = AuditLog("gallery", ROOT, dry=True)
FIG_DIR = os.path.join(ROOT, "docs", "figures")
README = os.path.join(ROOT, "README.md")
START, END = "<!-- gallery:start -->", "<!-- gallery:end -->"


def first_figure(nb_path):
    """(png bytes, caption text) of the first figure in an executed notebook, or None."""
    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        png, caption = None, ""
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            if png is None and "image/png" in data:
                png = base64.b64decode("".join(data["image/png"]))
            if "text/markdown" in data:
                txt = "".join(data["text/markdown"])
                m = re.search(r"\*(.+?)\*", txt, re.S)
                caption = (m.group(1) if m else txt).strip()
        if png is not None:
            return png, caption
    return None


def build(check=False):
    rows = []
    for ch in CHAPTERS:
        stem = os.path.splitext(ch.file)[0]
        nb_path = os.path.join(ROOT, CHAPTERS_DIR, ch.file)
        if not os.path.isfile(nb_path):
            log.warn(f"{ch.file}: not built, skipped")
            continue
        fig = first_figure(nb_path)
        if fig is None:
            log.info(f"{ch.file}: no figure, skipped")
            continue
        png, caption = fig
        rel = f"docs/figures/{stem}.png"
        if not check:
            os.makedirs(FIG_DIR, exist_ok=True)
            with open(os.path.join(ROOT, rel), "wb") as f:
                f.write(png)
        caption = re.sub(r"\s+", " ", caption)
        rows.append(f"| [{ch.title}](chapters/{ch.file}) | ![{ch.title}]({rel}) | {caption} |")
    block = "\n".join([START, "| Chapter | Figure | Caption |", "|---|---|---|", *rows, END])
    with open(README, encoding="utf-8") as f:
        text = f.read()
    if START not in text or END not in text:
        log.error("README.md has no gallery markers")
        return 1
    new = text[: text.index(START)] + block + text[text.index(END) + len(END):]
    if check:
        if new != text:
            log.error("README gallery is stale — run build/gallery.py")
            return 1
        log.info(f"README gallery up to date ({len(rows)} figures)")
        return 0
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    log.info(f"wrote {len(rows)} figures to docs/figures and the README gallery")
    return 0


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the README gallery block is stale")
    return ap


def main(argv=None):
    return build(check=build_parser().parse_args(argv).check)


if __name__ == "__main__":
    sys.exit(main())
