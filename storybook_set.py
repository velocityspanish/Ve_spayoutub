"""Rotate the storybook visual set.

The book, Velo, the 8-animal cast and the lesson UI stay identical. Only the
world around them changes:

    garden  : sunny meadow, pond, flowers, balloon
    forest  : deep green woodland, ferns, mushrooms, fireflies
    beach   : turquoise sea, sand, palms, shells
    desert  : dunes, cacti, oasis
    snow    : snowy mountains, pines, falling snow
    jungle  : rainforest pool, waterfall, giant leaves, fireflies
    savanna : golden grass, acacia trees, watering hole
    autumn  : amber leaves, pumpkins, leaf fall
    cherry  : pink blossom, torii gate, petals
    lavender: purple lavender field, windmill
    bamboo  : misty bamboo grove, stone lantern
    market  : twilight market street, awnings, string lights, cobblestones

Every post gets a different set from a shuffled deck, so consecutive posts
never share the same world. State lives in
output/history/storybook_set_deck.json.
"""
from __future__ import annotations

import json
import random
import sys
from datetime import datetime

import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SETS = (
    "garden",
    "forest",
    "beach",
    "desert",
    "snow",
    "jungle",
    "savanna",
    "autumn",
    "cherry",
    "lavender",
    "bamboo",
    "market",
)
DEFAULT_SET = "garden"
SET_FILE = config.HISTORY_DIR / "storybook_set_deck.json"


def _load() -> dict:
    if not SET_FILE.exists():
        return {"deck": [], "recent": [], "updated": None}
    try:
        return json.loads(SET_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"deck": [], "recent": [], "updated": None}


def _save(data: dict) -> None:
    SET_FILE.parent.mkdir(parents=True, exist_ok=True)
    SET_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def next_storybook_set() -> str:
    """Deal the next set from a shuffled deck, avoiding a recent repeat."""
    data = _load()
    recent = [s for s in data.get("recent", []) if s in SETS]
    deck = [s for s in data.get("deck", []) if s in SETS]
    if not deck:
        deck = list(SETS)
        random.shuffle(deck)
        if len(deck) > 1 and deck[0] in recent[-1:]:
            deck.append(deck.pop(0))
    chosen = deck.pop(0)
    if recent and chosen == recent[-1]:
        if deck:
            deck.append(chosen)
            chosen = deck.pop(0)
        else:
            alternatives = [s for s in SETS if s != chosen]
            chosen = random.choice(alternatives)
    recent = (recent + [chosen])[-6:]
    data.update({"deck": deck, "recent": recent, "updated": datetime.now().isoformat()})
    _save(data)
    print(f"[set] {chosen} ({len(deck)} left before reshuffle)")
    return chosen


def parse_set(value: str) -> str:
    value = value.strip().lower()
    if value not in SETS:
        raise SystemExit(f"unknown set: {value}. Choose from: {', '.join(SETS)}")
    return value


def main() -> int:
    chosen = next_storybook_set()
    print(json.dumps({"set": chosen}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
