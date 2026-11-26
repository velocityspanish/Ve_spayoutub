"""Render QA stills for a lesson without encoding the whole video."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import config
from engine import renderer

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def newest_lesson() -> Path | None:
    latest = config.OUTPUT_DIR / "latest.txt"
    if latest.exists():
        candidate = Path(latest.read_text(encoding="utf-8").strip())
        if (candidate / "timeline.json").exists():
            return candidate
    folders = [p for p in config.LESSONS_DIR.glob("*") if (p / "timeline.json").exists()]
    return max(folders, key=lambda p: p.stat().st_mtime) if folders else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture stills from a lesson timeline")
    parser.add_argument("--lesson", type=Path, help="lesson folder (default: newest)")
    parser.add_argument("--out", type=Path, help="output folder (default: <lesson>/stills)")
    parser.add_argument("--times", help="comma separated seconds (default: intro, first native, thumbnail, outro)")
    args = parser.parse_args()

    lesson = args.lesson or newest_lesson()
    if lesson is None:
        raise SystemExit("No lesson with a timeline.json found. Build one first.")

    timeline = json.loads((lesson / "timeline.json").read_text(encoding="utf-8"))
    if args.times:
        times = [float(x.strip()) for x in args.times.split(",") if x.strip()]
    else:
        first = timeline["phrases"][0] if timeline.get("phrases") else None
        times = [1.3]
        if first:
            times.append(round(first["nat_reveal"] + 0.9, 2))
        times.append(float(timeline.get("thumb_t", 2.0)))
        times.append(round(timeline["outro"]["start"] + 2.6, 2))

    out_dir = args.out or (lesson / "stills")
    saved = renderer.capture_stills(timeline, times, out_dir)
    print(f"[stills] {len(saved)} frames -> {out_dir}")
    for path in saved:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
