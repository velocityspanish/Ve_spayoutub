"""Build one Velocity lesson reel end to end."""

from __future__ import annotations

import argparse
import json
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

import config
from config import CATEGORIES, CATEGORY_META
from engine import audio, content, renderer, timeline, tts

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def slugify(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")


def parse_args():
    parser = argparse.ArgumentParser(description=f"{config.BRAND} motion reel builder")
    parser.add_argument("--category", choices=CATEGORIES, help="lesson category")
    parser.add_argument("--phrases", type=int, default=5, help="number of phrases (default 5)")
    parser.add_argument("--skip-video", action="store_true", help="build phrases, audio and timeline only")
    parser.add_argument("--open", action="store_true", help="open the interactive preview when finished")
    parser.add_argument("--list-categories", action="store_true", help="print all categories and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_categories:
        for i, name in enumerate(CATEGORIES, 1):
            meta = CATEGORY_META[name]
            print(f"{i:2d}. {name} · {meta['native']} ({meta['icon']})")
        return 0

    print("=" * 74)
    print(f"  {config.BRAND} · MOTION LESSON BUILDER")
    print("=" * 74)

    category = args.category or content.get_available_category()
    meta = CATEGORY_META[category]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lesson_dir = config.LESSONS_DIR / f"{slugify(category)}_{stamp}"
    audio_dir = lesson_dir / "audio"
    work_dir = lesson_dir / "work"
    lesson_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/6] Lesson: {category} · {meta['native']}  ({meta['icon']}, {meta['accent']})")
    print(f"      Output: {lesson_dir}")

    phrases = content.generate_phrases(category, args.phrases)
    for i, phrase in enumerate(phrases, 1):
        print(f"      {i}. {phrase['english']}")
        print(f"         {phrase['native']}  [{phrase.get('transliteration', '')}]")

    print(f"\n[2/6] Voice + word clocks")
    clips = tts.synthesize_all(phrases, audio_dir)

    print(f"\n[3/6] Timeline")
    tl = timeline.build_timeline(phrases, clips, category)
    while len(phrases) > 1 and tl["duration"] > config.MAX_REEL_DURATION:
        dropped = phrases.pop()
        clips.pop()
        tl = timeline.build_timeline(phrases, clips, category)
        print(f"      Trimmed '{dropped['english']}' to stay under {config.MAX_REEL_DURATION:.0f}s")
    timeline_path = lesson_dir / "timeline.json"
    timeline_path.write_text(json.dumps(tl, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"      {tl['duration']:.1f}s · {len(tl['phrases'])} phrases · {len(tl['sfx'])} sfx cues")

    print(f"\n[4/6] Music + sound design")
    mix_path = lesson_dir / "mix.wav"
    audio.build_mix(clips, tl, mix_path)

    video_info = {}
    if args.skip_video:
        print(f"\n[5/6] Video skipped (--skip-video)")
    else:
        print(f"\n[5/6] Animated video")
        out_mp4 = lesson_dir / "final_reel.mp4"
        video_info = renderer.render_video(tl, mix_path, out_mp4, work_dir)

    print(f"\n[6/6] Preview + metadata")
    preview = renderer.write_preview(tl, mix_path)

    metadata = {
        "brand": config.BRAND,
        "handle": config.HANDLE,
        "language": config.LANGUAGE["name"],
        "category_english": category,
        "category_native": meta["native"],
        "timestamp": stamp,
        "duration": tl["duration"],
        "phrases": phrases,
        "video": video_info.get("video"),
        "thumbnail": video_info.get("thumbnail"),
        "audio": str(mix_path),
        "timeline": str(timeline_path),
        "preview": str(preview),
        "hashtags": config.HASHTAGS,
    }
    metadata_path = lesson_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    (config.OUTPUT_DIR / "latest.txt").write_text(str(lesson_dir), encoding="utf-8")

    print("\n" + "=" * 74)
    print("  LESSON COMPLETE")
    print("=" * 74)
    print(f"  Folder     : {lesson_dir}")
    print(f"  Timeline   : {timeline_path.name}")
    print(f"  Audio mix  : {mix_path.name}")
    if video_info:
        print(f"  Video      : {Path(video_info['video']).name}")
        print(f"  Thumbnail  : {Path(video_info['thumbnail']).name}")
    print(f"  Preview    : {preview}")

    if args.open:
        webbrowser.open(preview.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
