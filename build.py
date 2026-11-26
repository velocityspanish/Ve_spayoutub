"""Build one storybook lesson reel.

The live bot uses the storybook recipe: three phrases, a rotating world,
a rotating colour palette and a rotating animal cast.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

import config
from config import CATEGORIES, CATEGORY_META, RECIPES
from engine import audio, content, renderer, timeline, tts
from storybook_set import SETS as STORYBOOK_SETS

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def slugify(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")


def parse_args():
    parser = argparse.ArgumentParser(description=f"{config.BRAND} storybook reel builder")
    parser.add_argument("--category", choices=CATEGORIES, help="lesson category")
    parser.add_argument("--phrases", type=int, help="override phrase count (3-5)")
    parser.add_argument("--recipe", choices=[r["id"] for r in RECIPES], help="experiment recipe id")
    parser.add_argument("--palette", "--theme", dest="theme", choices=list(config.THEMES), help="colour palette (not the world)")
    parser.add_argument("--style", choices=list(config.SCENE_DIRS), help="visual style (poster or storybook)")
    parser.add_argument("--new-theme", "--new-palette", dest="new_theme", action="store_true", help="generate a new seed-based colour palette for this build")
    parser.add_argument("--cast", help="storybook cast: left,pond,mid,right (e.g. cat,duck,panda,bunny)")
    parser.add_argument("--world", "--set", dest="world_set", choices=STORYBOOK_SETS, help="storybook world (background)")
    parser.add_argument("--skip-video", action="store_true", help="build phrases, audio and timeline only")
    parser.add_argument("--open", action="store_true", help="open the interactive preview when finished")
    parser.add_argument("--list-categories", action="store_true", help="print all categories and exit")
    parser.add_argument("--list-recipes", action="store_true", help="print experiment recipes and exit")
    parser.add_argument("--list-palettes", "--list-themes", dest="list_palettes", action="store_true", help="print all colour palettes and exit")
    parser.add_argument("--list-styles", action="store_true", help="print all visual styles and exit")
    parser.add_argument("--list-worlds", "--list-sets", dest="list_worlds", action="store_true", help="print all storybook worlds and exit")
    return parser.parse_args()


def choose_recipe(recipe_id: str | None) -> dict:
    if recipe_id:
        return config.RECIPE_BY_ID[recipe_id]
    # Production is storybook-only. The old experiment bandit could pick a
    # poster recipe, which is not what this channel publishes.
    return config.RECIPE_BY_ID["storybook-3"]


def next_storybook_theme() -> str:
    """Deal the next theme from a shuffled deck.

    13 curated themes + generated themes are shuffled together. Every storybook
    post gets a different theme until the deck is empty, then it reshuffles.
    At 3 posts/day the curated deck runs for about four days without a repeat.
    """
    try:
        from theme_builder import load_registry

        for theme_id, theme in load_registry().items():
            config.THEMES.setdefault(theme_id, theme)
    except Exception as exc:  # noqa: BLE001 - generated themes are optional
        print(f"[theme] generated themes unavailable: {exc}")

    path = config.HISTORY_DIR / "storybook_theme_deck.json"
    data = {"deck": [], "recent": [], "updated": None}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    recent = data.get("recent", [])
    deck = [t for t in data.get("deck", []) if t in config.THEMES]
    if not deck:
        deck = list(config.THEMES)
        random.shuffle(deck)
        if len(deck) > 1 and deck[0] in recent[-4:]:
            deck.append(deck.pop(0))
    theme = deck.pop(0)
    recent = (recent + [theme])[-8:]
    data.update({"deck": deck, "recent": recent, "updated": datetime.now().isoformat()})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[theme] deck: {theme} ({len(deck)} left before reshuffle)")
    return theme


def main() -> int:
    args = parse_args()

    if args.list_categories:
        for i, name in enumerate(CATEGORIES, 1):
            meta = CATEGORY_META[name]
            print(f"{i:2d}. {name} · {meta['native']} ({meta['icon']})")
        return 0

    if args.list_recipes:
        for r in RECIPES:
            print(f"{r['id']:20s} theme={r['theme']:7s} phrases={r['phrases']} pace={r['pace']:8s} hook={r['hook']}")
        return 0

    if args.list_palettes:
        for theme_id, theme in config.THEMES.items():
            print(f"{theme_id:8s} {theme['name']:14s} worlds: {', '.join(theme['worlds'])}")
        return 0

    if args.list_styles:
        for style, path in config.SCENE_DIRS.items():
            print(f"{style:10s} {path}")
        return 0

    if args.list_worlds:
        for name in STORYBOOK_SETS:
            print(name)
        return 0

    recipe = choose_recipe(args.recipe)
    if args.theme:
        recipe = {**recipe, "id": f"manual-{args.theme}", "theme": args.theme}
        print(f"[theme] manual override: {args.theme}")
    if args.style:
        recipe = {**recipe, "id": f"manual-{args.style}-{recipe['theme']}", "style": args.style}
        print(f"[style] manual override: {args.style}")
    if recipe.get("style") == "storybook" and not args.theme and not args.new_theme:
        recipe = {**recipe, "theme": next_storybook_theme()}
    if recipe.get("style") == "storybook":
        if args.world_set:
            recipe = {**recipe, "set": args.world_set}
        elif not recipe.get("set"):
            from storybook_set import next_storybook_set

            recipe = {**recipe, "set": next_storybook_set()}
        if args.cast:
            from storybook_cast import parse_cast

            recipe = {**recipe, "cast": parse_cast(args.cast)}
        elif not recipe.get("cast"):
            from storybook_cast import next_storybook_cast

            recipe = {**recipe, "cast": next_storybook_cast(recipe.get("set", "garden"))}
    if args.new_theme:
        if args.theme:
            raise SystemExit("Use either --theme or --new-theme, not both")
        from theme_builder import create_theme

        theme_id, theme = create_theme()
        config.THEMES[theme_id] = theme
        recipe = {**recipe, "theme": theme_id}
        print(f"[theme] generated: {theme_id} ({theme['name']})")
    scene_dir = config.scene_dir(recipe.get("style", "poster"))
    phrase_target = args.phrases or recipe["phrases"]
    if not config.MIN_PHRASES <= phrase_target <= config.MAX_PHRASES:
        raise SystemExit(f"--phrases must be between {config.MIN_PHRASES} and {config.MAX_PHRASES}")

    print("=" * 74)
    print(f"  {config.BRAND} · STORYBOOK REEL")
    print("=" * 74)
    print(f"  recipe: {recipe['id']}  ·  theme: {recipe['theme']}  ·  style: {recipe.get('style', 'poster')}  ·  {phrase_target} phrases")

    category = args.category or content.get_available_category()
    meta = CATEGORY_META[category]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lesson_dir = config.LESSONS_DIR / f"{slugify(category)}_{stamp}"
    audio_dir = lesson_dir / "audio"
    work_dir = lesson_dir / "work"
    lesson_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/6] Lesson: {category} · {meta['native']}  ({meta['icon']})")
    print(f"      Output: {lesson_dir}")

    phrases = content.generate_phrases(category, phrase_target)
    if len(phrases) < config.MIN_PHRASES:
        raise SystemExit(
            f"Only {len(phrases)} fresh phrases available; need at least {config.MIN_PHRASES}. "
            "Add fallback phrases or retry the content API."
        )
    clips = tts.synthesize_all(phrases, audio_dir)

    print(f"\n[2/6] Duration budgeting (hard cap {config.MAX_REEL_DURATION:.1f}s)")
    while len(phrases) > config.MIN_PHRASES:
        estimate = timeline.estimate_duration(clips[: len(phrases)], recipe)
        if estimate <= config.MAX_REEL_DURATION:
            break
        dropped = phrases.pop()
        print(f"      -{estimate:.1f}s > cap · dropped '{dropped['english']}'")
    estimate = timeline.estimate_duration(clips[: len(phrases)], recipe)
    print(f"      planned: {estimate:.1f}s · {len(phrases)} phrases")

    if estimate > config.MAX_REEL_DURATION:
        raise SystemExit(
            f"Even {len(phrases)} phrases run {estimate:.1f}s (cap {config.MAX_REEL_DURATION:.1f}s). "
            "Shorten the phrase set or use a tighter pace."
        )

    print(f"\n[3/6] Timeline")
    tl = timeline.build_timeline(phrases, clips[: len(phrases)], category, recipe)
    tl["estimate"] = estimate
    timeline_path = lesson_dir / "timeline.json"
    timeline_path.write_text(json.dumps(tl, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"      {tl['duration']:.1f}s · {len(tl['phrases'])} phrases · {len(tl['sfx'])} sfx cues")

    print(f"\n[4/6] Music + sound design")
    mix_path = lesson_dir / "mix.wav"
    audio.build_mix(clips[: len(phrases)], tl, mix_path)

    video_info = {}
    if args.skip_video:
        print(f"\n[5/6] Video skipped (--skip-video)")
    else:
        print(f"\n[5/6] Animated video")
        out_mp4 = lesson_dir / "final_reel.mp4"
        video_info = renderer.render_video(tl, mix_path, out_mp4, work_dir, scene_dir=scene_dir)

    print(f"\n[6/6] Preview + metadata")
    preview = renderer.write_preview(tl, mix_path, scene_dir=scene_dir)

    metadata = {
        "brand": config.BRAND,
        "handle": config.HANDLE,
        "language": config.LANGUAGE["name"],
        "category_english": category,
        "category_native": meta["native"],
        "timestamp": stamp,
        "duration": tl["duration"],
        "duration_cap": config.MAX_REEL_DURATION,
        "recipe": recipe,
        "style": recipe.get("style", "poster"),
        "theme": tl["theme"],
        "set": tl.get("set"),
        "cast": tl.get("cast"),
        "hook": tl["hook"],
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
    print(f"  Duration   : {tl['duration']:.1f}s / {config.MAX_REEL_DURATION:.1f}s cap")
    print(f"  Recipe     : {recipe['id']} ({tl['theme']['name']} · {tl.get('style', 'poster')})")
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
