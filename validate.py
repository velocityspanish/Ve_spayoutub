"""Release gate for the sample engine.

Fails if the reel breaks the one rule that matters: never over 60 seconds.
Also catches missing metadata, wrong phrase counts and stale recipe ids.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import config
from storybook_set import SETS as STORYBOOK_SETS

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def _newest_lesson() -> Path | None:
    latest = config.OUTPUT_DIR / "latest.txt"
    if latest.exists():
        candidate = Path(latest.read_text(encoding="utf-8").strip())
        if candidate.exists():
            return candidate
    folders = [p for p in config.LESSONS_DIR.glob("*") if p.is_dir()]
    return max(folders, key=lambda p: p.stat().st_mtime) if folders else None


def _ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def _probe_loudness(path: Path) -> tuple[float | None, float | None]:
    """Integrated LUFS + true peak, measured on the final muxed file."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
        errors="ignore",
    )
    out = result.stderr or ""
    lufs = [float(x) for x in re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", out)]
    peaks = [float(x) for x in re.findall(r"Peak:\s+(-?\d+(?:\.\d+)?) dBFS", out)]
    return (lufs[-1] if lufs else None, peaks[-1] if peaks else None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the newest sample reel")
    parser.add_argument("--lesson", type=Path)
    parser.add_argument("--allow-missing-video", action="store_true")
    parser.add_argument("--skip-audio", action="store_true", help="skip the loudness/true-peak gate")
    args = parser.parse_args()

    lesson = args.lesson or _newest_lesson()
    if lesson is None:
        print("[validate] FAIL: no lesson folder found")
        return 1

    errors = []
    metadata_path = lesson / "metadata.json"
    timeline_path = lesson / "timeline.json"
    if not metadata_path.exists():
        print(f"[validate] FAIL: missing {metadata_path}")
        return 1
    if not timeline_path.exists():
        print(f"[validate] FAIL: missing {timeline_path}")
        return 1

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    duration = float(timeline.get("duration") or metadata.get("duration") or 0)
    phrase_count = len(timeline.get("phrases") or [])

    if duration <= 0:
        errors.append("timeline duration is zero")
    if duration > 60.0:
        errors.append(f"duration {duration:.2f}s exceeds the 60.00s platform limit")
    if duration > config.MAX_REEL_DURATION + 0.05:
        errors.append(f"duration {duration:.2f}s exceeds project cap {config.MAX_REEL_DURATION:.2f}s")
    if not config.MIN_PHRASES <= phrase_count <= config.MAX_PHRASES:
        errors.append(f"{phrase_count} phrases is outside {config.MIN_PHRASES}-{config.MAX_PHRASES}")
    if not timeline.get("theme"):
        errors.append("timeline has no theme")

    recipe = metadata.get("recipe") or {}
    recipe_id = str(recipe.get("id") or "")
    if recipe_id not in config.RECIPE_BY_ID and not recipe_id.startswith("manual-"):
        errors.append(f"unknown recipe id: {recipe.get('id')!r}")
    theme_id = recipe.get("theme")
    if theme_id not in config.THEMES and not (str(theme_id).startswith("gen-") and timeline.get("theme")):
        errors.append(f"unknown theme id: {theme_id!r}")
    style = metadata.get("style") or recipe.get("style") or "poster"
    if style not in config.SCENE_DIRS:
        errors.append(f"unknown style: {style!r}")
    elif not (config.scene_dir(style) / "index.html").exists():
        errors.append(f"missing scene: {config.scene_dir(style) / 'index.html'}")
    world_set = timeline.get("set") or metadata.get("set") or "garden"
    if world_set not in STORYBOOK_SETS:
        errors.append(f"unknown storybook set: {world_set!r}")

    video = Path(metadata["video"]) if metadata.get("video") else lesson / "final_reel.mp4"
    actual = 0.0
    lufs = peak = None
    if video.exists():
        actual = _ffprobe_duration(video)
        if actual <= 0:
            errors.append("ffprobe could not read the video duration")
        elif actual > 60.2:
            errors.append(f"encoded video is {actual:.2f}s (hard limit 60s)")
        if not args.skip_audio:
            lufs, peak = _probe_loudness(video)
            if lufs is None or peak is None:
                errors.append("could not measure loudness / true peak")
            else:
                if not -16.0 <= lufs <= -11.0:
                    errors.append(f"integrated loudness {lufs:.1f} LUFS outside -16..-11")
                if peak > -0.8:
                    errors.append(f"true peak {peak:.1f} dBFS is too hot for earphones")
    elif not args.allow_missing_video:
        errors.append(f"video missing: {video}")

    print("=" * 62)
    print("  SAMPLE REEL VALIDATION")
    print("=" * 62)
    print(f"  lesson     : {lesson.name}")
    print(f"  recipe     : {recipe.get('id')} · {timeline.get('theme', {}).get('name')} · {style}")
    print(f"  set        : {timeline.get('set', 'garden')}")
    print(f"  timeline   : {duration:.2f}s / {config.MAX_REEL_DURATION:.2f}s cap")
    print(f"  encoded    : {actual:.2f}s" if actual else "  encoded    : (not rendered)")
    if lufs is not None and peak is not None:
        print(f"  loudness   : {lufs:.1f} LUFS / {peak:.1f} dBTP")
    print(f"  phrases    : {phrase_count}")
    print(f"  categories : {metadata.get('category_english')} ({metadata.get('category_native')})")
    print("=" * 62)

    if errors:
        for error in errors:
            print(f"  FAIL: {error}")
        return 1
    print("  PASS: under 60 seconds, recipe and metadata are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
