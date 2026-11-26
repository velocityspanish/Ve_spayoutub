"""Show the next storybook worlds and colour palettes as a posting plan.

A "world" is the background scene (beach, snow, jungle, ...).
A "palette" is the colour set used on top of that world.

    python theme_plan.py --per-day 4 --days 7
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

import config
from storybook_set import SETS as STORYBOOK_SETS

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

WORLD_DECK_FILE = config.HISTORY_DIR / "storybook_set_deck.json"
PALETTE_DECK_FILE = config.HISTORY_DIR / "storybook_theme_deck.json"
PLAN_FILE = config.HISTORY_DIR / "theme_plan.md"
WORLD_PLAN_FILE = config.HISTORY_DIR / "world_plan.md"


def _load_palettes() -> dict:
    palettes = dict(config.THEMES)
    try:
        from theme_builder import load_registry

        for theme_id, theme in load_registry().items():
            palettes.setdefault(theme_id, theme)
    except Exception:
        pass
    return palettes


def _read_deck(path, valid):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return [item for item in data.get("deck", []) if item in valid]


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the upcoming storybook worlds + palettes")
    parser.add_argument("--per-day", type=int, default=4)
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    worlds = _read_deck(WORLD_DECK_FILE, set(STORYBOOK_SETS))
    if not worlds:
        worlds = list(STORYBOOK_SETS)
    palettes_all = _load_palettes()
    palettes = _read_deck(PALETTE_DECK_FILE, set(palettes_all))
    if not palettes:
        palettes = list(palettes_all)

    need = args.per_day * args.days
    world_shown = [worlds[i % len(worlds)] for i in range(need)]
    palette_shown = [palettes[i % len(palettes)] for i in range(need)]

    lines = [
        "# Storybook world plan",
        "",
        f"Generated: `{datetime.now().isoformat()}`",
        f"Worlds: **{len(worlds)} in the deck** · {args.per_day} posts/day",
        f"Palettes: **{len(palettes)} in the deck**",
        "",
        "| Day | Worlds (backgrounds) | Palettes (colours) |",
        "|---|---|---|",
    ]
    for day in range(args.days):
        start = day * args.per_day
        stop = start + args.per_day
        if start >= need:
            break
        world_cell = "<br>".join(f"**{w}**" for w in world_shown[start:stop])
        palette_cell = "<br>".join(palettes_all[p]["name"] for p in palette_shown[start:stop])
        lines.append(f"| Day {day + 1} | {world_cell} | {palette_cell} |")

    lines += [
        "",
        "## How it works",
        "",
        "- **World** = the background scene: garden, forest, beach, desert, snow, jungle, savanna, autumn, cherry, lavender, bamboo, market.",
        "- **Palette** = the colour set used for tiles, props and accents on top of that world.",
        "- Each storybook build pops the next world and the next palette independently.",
        "- World state: `output/history/storybook_set_deck.json`.",
        "- Palette state: `output/history/storybook_theme_deck.json`.",
        "- Manual world: `python build.py --recipe storybook-3 --world snow`.",
        "- Manual palette: `python build.py --recipe storybook-3 --palette mango`.",
        "- See every world: `python storybook_set_gallery.py`.",
        "- See every palette: `python storybook_palette_gallery.py`.",
        "",
    ]
    text = "\n".join(lines)
    print(text)
    PLAN_FILE.write_text(text, encoding="utf-8")
    WORLD_PLAN_FILE.write_text(text, encoding="utf-8")
    print(f"[plan] wrote {WORLD_PLAN_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
