#!/usr/bin/env python3
"""QC pre-flight for the Ireland gallery shell. Exits non-zero on any failure.

The seed ships zero scenes. When a scene is added it must stay Candidate.
This script does not approve anything and does not invent word-of-day entries.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from composite_masters import CANVAS, DESCRIPTION, assert_art50

ROOT = Path(__file__).resolve().parents[1]
CANON = "https://ireland.jdvision.org/"
ART50 = (
    "AI-generated artistic interpretation from the Jason D's Vision Ireland gallery. "
    "Created with generative AI; not a photograph."
)
ENTRY_RE = re.compile(r"^IE-01-\d{3}$")
FORBIDDEN = (
    "real-time conditions",
    "photograph of",
    "captured on",
)
OUTSIDE = ("northern ireland", "belfast", "derry", "londonderry")


def main() -> None:
    errors: list[str] = []
    if DESCRIPTION != ART50:
        errors.append("Art. 50 Description line does not match the Ireland contract")

    data = json.loads((ROOT / "data.json").read_text())
    if data.get("country") != "Ireland" or data.get("code") != "IE":
        errors.append("data.json country/code is not Ireland / IE")
    if data.get("canonical") != CANON:
        errors.append("data.json canonical is not the Ireland canon")
    if data.get("ga") != "G-PDJ4WSS725":
        errors.append("data.json GA4 id is not G-PDJ4WSS725")
    if data.get("timezone") != "Europe/Dublin":
        errors.append("data.json timezone is not Europe/Dublin")
    scenes = data.get("scenes")
    if not isinstance(scenes, list):
        errors.append("data.json scenes is not a list")
        scenes = []

    wotd_path = ROOT / "tools" / "ie.json"
    if not wotd_path.is_file():
        errors.append("missing tools/ie.json")
        wotd = None
    else:
        wotd = json.loads(wotd_path.read_text())
    if wotd != []:
        errors.append("tools/ie.json must stay an empty array until Cosmo delivers entries")

    alt = ROOT / "word-of-day" / "ie.json"
    if alt.is_file() and json.loads(alt.read_text()) != []:
        errors.append("word-of-day/ie.json must stay an empty array")

    cname = (ROOT / "CNAME").read_text().strip() if (ROOT / "CNAME").is_file() else ""
    if cname != "ireland.jdvision.org":
        errors.append(f"CNAME is {cname!r}")
    if not (ROOT / ".nojekyll").is_file():
        errors.append("missing .nojekyll")

    pngs = [p for p in ROOT.rglob("*.png") if ".git" not in p.parts]
    if not scenes and pngs:
        errors.append("shell seed must not ship scene PNGs: " + ", ".join(str(p.relative_to(ROOT)) for p in pngs))

    seen: set[str] = set()
    for scene in scenes:
        entry_id = scene.get("entry_id") or ""
        if entry_id in seen:
            errors.append(f"duplicate entry id {entry_id}")
        seen.add(entry_id)
        if not ENTRY_RE.match(entry_id):
            errors.append(f"entry id is not IE-01-NNN: {entry_id!r}")
        blob = json.dumps(scene, ensure_ascii=False).lower()
        for name in OUTSIDE:
            if name in blob:
                errors.append(f"{entry_id} is outside the Republic of Ireland ({name})")
        if scene.get("approval_status") != "Candidate":
            errors.append(f"{entry_id} approval_status is not Candidate")
        for key in (
            "format_16x9_approval_status",
            "format_4x5_approval_status",
            "format_9x16_approval_status",
        ):
            if scene.get(key) == "Approved":
                errors.append(f"{entry_id} {key} was self-approved")
        folder = scene.get("folder") or scene.get("city") or ""
        for fmt, size in CANVAS.items():
            rel = scene.get(f"file_{fmt}")
            if not rel:
                continue
            path = ROOT / rel
            expected = ROOT / "assets" / "ireland" / folder / f"{entry_id.lower()}-{fmt}.png"
            if path.resolve() != expected.resolve():
                errors.append(f"{entry_id} {fmt} path is not {expected.relative_to(ROOT)}")
            if not path.is_file():
                errors.append(f"missing master {rel}")
                continue
            with Image.open(path) as im:
                if im.size != size:
                    errors.append(f"bad size {path.name} {im.size}")
            try:
                assert_art50(path)
            except SystemExit as err:
                errors.append(str(err))
        weather_path = ROOT / "evidence" / "weather" / f"{entry_id}.json"
        if scenes and not weather_path.is_file():
            errors.append(f"missing weather {entry_id}")
        elif weather_path.is_file():
            weather = json.loads(weather_path.read_text())
            if weather.get("timezone") != "Europe/Dublin":
                errors.append(f"{entry_id} weather timezone is not Europe/Dublin")
        note = ROOT / "approvals" / f"{entry_id}.md"
        if note.is_file():
            text = note.read_text()
            if re.search(r"approval_status:\s*Approved", text):
                errors.append(f"{entry_id} approval note self-approved")
            low = text.lower()
            for phrase in FORBIDDEN:
                if phrase in low:
                    errors.append(f"{entry_id} approval note contains {phrase!r}")

    html_path = ROOT / "index.html"
    if not html_path.is_file():
        errors.append("missing index.html")
        html = ""
    else:
        html = html_path.read_text()
    if html:
        if "Download 9:16" in html.split("const SCENES")[0]:
            errors.append("static markup exposes a 9:16 download")
        if ">Ireland<" not in html or 'aria-current="page"' not in html:
            errors.append("Ireland is not marked current")
        if "https://sweden.jdvision.org/" not in html:
            errors.append("Sweden gallery link missing")
        ga = set(re.findall(r"G-[A-Z0-9]+", html))
        if ga != {"G-PDJ4WSS725"}:
            errors.append(f"GA4 ids are {sorted(ga)}")
        if "var INTERVAL=4000;" not in html:
            errors.append("lightbox interval is not 4000ms")
        if CANON not in html:
            errors.append("Ireland canonical missing")
        if "flag-ie" not in html:
            errors.append("Ireland flag chip missing")
        if "linear-gradient(to right,#169B62 33.3%,#ffffff 33.3%,#ffffff 66.6%,#FF883E 66.6%)" not in html:
            errors.append("Ireland flag band missing")
        if 'id="wotd"' not in html or 'lang="ga"' not in html:
            errors.append("word-of-day band missing")
        if "avocado_v2:MAI_01" not in html:
            errors.append("narration hook missing")
        if not scenes and "const SCENES = [];" not in html:
            errors.append("empty shell did not publish an empty SCENES array")
        if '"approval_status":"Approved"' in html or '"approval_status": "Approved"' in html:
            errors.append("index.html contains an Approved scene")

    for name in ("robots.txt", "sitemap.xml"):
        path = ROOT / name
        if not path.is_file():
            errors.append(f"missing {name}")
        elif CANON not in path.read_text():
            errors.append(f"{name} does not name the Ireland canon")
    image_sitemap = ROOT / "image-sitemap.xml"
    if not image_sitemap.is_file():
        errors.append("missing image-sitemap.xml")
    else:
        image_xml = image_sitemap.read_text()
        if "<urlset" not in image_xml:
            errors.append("image-sitemap.xml is not a urlset")
        if "9x16" in image_xml:
            errors.append("image-sitemap.xml lists a 9:16 master")
        if not scenes and "<image:image>" in image_xml:
            errors.append("empty shell image sitemap must not list images")
        if "sweden.jdvision.org" in image_xml or "assets/sweden/" in image_xml:
            errors.append("image-sitemap.xml points at Sweden")

    if errors:
        print("\n".join(errors))
        raise SystemExit(f"{len(errors)} qc failures")
    print("qc preflight ok")
    print(f"scenes {len(scenes)} pngs {len(pngs)} wotd {0 if wotd == [] else 'not-empty'}")


if __name__ == "__main__":
    main()
