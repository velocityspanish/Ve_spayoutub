"""Build a storybook-style lesson from an existing lesson's voice track.

Useful for design iteration when the TTS provider is rate-limiting. It takes the
first N phrases and clips from a lesson that already has audio, rebuilds the
timeline with the storybook recipe and renders the new scene.

    python storybook_preview.py --source output/lessons/Greetings_... --render
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import config
from engine import audio, renderer, timeline
from storybook_set import SETS as STORYBOOK_SETS

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def _duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a storybook lesson from an existing voice track")
    parser.add_argument("--source", type=Path, required=True, help="lesson folder with audio/ and timeline.json")
    parser.add_argument("--phrases", type=int, default=3)
    parser.add_argument("--palette", "--theme", dest="theme", choices=list(config.THEMES), help="colour palette (not the world)")
    parser.add_argument("--cast", help="storybook cast: left,pond,mid,right (e.g. cat,duck,panda,bunny)")
    parser.add_argument("--world", "--set", dest="world_set", choices=STORYBOOK_SETS, help="storybook world (background)")
    parser.add_argument("--render", action="store_true", help="encode the full MP4")
    args = parser.parse_args()

    source = args.source
    source_tl = json.loads((source / "timeline.json").read_text(encoding="utf-8"))
    source_meta = json.loads((source / "metadata.json").read_text(encoding="utf-8"))
    count = min(args.phrases, len(source_tl["phrases"]), 5)
    recipe = config.RECIPE_BY_ID["storybook-3"]
    if args.theme:
        recipe = {**recipe, "theme": args.theme}
    if args.world_set:
        from storybook_set import parse_set

        recipe = {**recipe, "set": parse_set(args.world_set)}
    else:
        from storybook_set import next_storybook_set

        recipe = {**recipe, "set": next_storybook_set()}
    if args.cast:
        from storybook_cast import parse_cast

        recipe = {**recipe, "cast": parse_cast(args.cast)}
    else:
        from storybook_cast import next_storybook_cast

        recipe = {**recipe, "cast": next_storybook_cast(recipe.get("set", "garden"))}
    phrases = []
    clips = []

    for i in range(count):
        p = source_tl["phrases"][i]
        en_path = source / "audio" / f"en_{i}.mp3"
        vi_path = source / "audio" / f"vi_{i}.mp3"
        if not en_path.exists() or not vi_path.exists():
            raise SystemExit(f"missing audio for phrase {i}: {en_path} / {vi_path}")
        phrases.append({
            "english": p["english"],
            "native": p["native"],
            "transliteration": p.get("transliteration", ""),
        })
        clips.append({
            "index": i,
            "english": p["english"],
            "native": p["native"],
            "transliteration": p.get("transliteration", ""),
            "en_path": en_path,
            "vi_path": vi_path,
            "en_duration": _duration(en_path),
            "vi_duration": _duration(vi_path),
            "en_words": [
                {"start": w["t0"] - p["en_start"], "end": w["t1"] - p["en_start"]}
                for w in p["en_words"]
            ],
            "vi_words": [
                {"start": w["t0"] - p["vi_start"], "end": w["t1"] - p["vi_start"]}
                for w in p["vi_words"]
            ],
        })

    category = source_meta.get("category_english") or source_tl["category"]["english"]
    tl = timeline.build_timeline(phrases, clips, category, recipe)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = config.LESSONS_DIR / f"Storybook_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "timeline.json").write_text(json.dumps(tl, indent=2, ensure_ascii=False), encoding="utf-8")

    mix_path = out_dir / "mix.wav"
    audio.build_mix(clips, tl, mix_path)
    scene_dir = config.scene_dir("storybook")

    video = None
    thumb = None
    if args.render:
        info = renderer.render_video(tl, mix_path, out_dir / "final_reel.mp4", out_dir / "work", scene_dir=scene_dir)
        video = info["video"]
        thumb = info["thumbnail"]

    preview = renderer.write_preview(tl, mix_path, scene_dir=scene_dir)
    first = tl["phrases"][0]
    second = tl["phrases"][1] if len(tl["phrases"]) > 1 else first
    stills = renderer.capture_stills(
        tl,
        [
            1.7,
            first["nat_reveal"] + 0.9,
            first["vi_repeat_start"] + 0.7,
            second["nat_reveal"] + 0.9,
            tl["outro"]["start"] + 2.6,
        ],
        out_dir / "stills",
        scene_dir=scene_dir,
    )

    metadata = {
        "brand": config.BRAND,
        "handle": config.HANDLE,
        "language": config.LANGUAGE["name"],
        "category_english": category,
        "category_native": source_meta.get("category_native"),
        "timestamp": stamp,
        "duration": tl["duration"],
        "duration_cap": config.MAX_REEL_DURATION,
        "recipe": recipe,
        "style": "storybook",
        "theme": tl["theme"],
        "set": tl.get("set"),
        "cast": tl.get("cast"),
        "phrases": phrases,
        "video": video,
        "thumbnail": thumb,
        "audio": str(mix_path),
        "timeline": str(out_dir / "timeline.json"),
        "preview": str(preview),
        "hashtags": config.HASHTAGS,
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    (config.OUTPUT_DIR / "latest.txt").write_text(str(out_dir), encoding="utf-8")

    print(f"[storybook] {out_dir}")
    print(f"[storybook] {tl['duration']:.1f}s · {len(phrases)} phrases · {tl['theme']['name']}")
    print(f"[storybook] set: {tl.get('set', 'garden')}")
    print(f"[storybook] cast: " + " ".join(f"{slot}={tl['cast'][slot]}" for slot in ('left', 'pond', 'mid', 'right')))
    for path in stills:
        print(f"  still: {path}")
    if video:
        print(f"  video: {video}")
    print(f"  preview: {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
