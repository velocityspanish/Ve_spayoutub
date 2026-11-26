"""Rotate the storybook guest cast.

Velo stays in every video as the brand mascot. The four garden guests are dealt
from role-aware pools so each post feels like a new little world without
becoming random noise:

    left  : bunny, cat, panda, lion, elephant, giraffe, ...
    pond  : frog, duck, or a land animal standing by the water
    mid   : hedgehog, penguin, panda, owl, monkey, ...
    right : cat, bunny, lion, elephant, ...

Each world also has its own preferred cast. Snow gets the polar bear, reindeer
and owl; savanna gets the lion, elephant, giraffe and zebra; desert gets the
camel; forest gets the deer and owl; jungle gets the monkey.

At 3-4 posts/day the recent-cast memory prevents an obvious repeat. State lives
in output/history/storybook_cast.json.
"""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime

import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SLOTS = ("left", "pond", "mid", "right")
DEFAULT_CAST = {"left": "bunny", "pond": "frog", "mid": "hedgehog", "right": "cat"}
CAST_CHOICES = {
    "left": (
        "bunny", "cat", "panda", "lion", "elephant", "giraffe",
        "zebra", "polar", "reindeer", "monkey", "camel", "deer",
    ),
    "pond": ("frog", "duck", "zebra", "camel", "deer", "giraffe"),
    "mid": (
        "hedgehog", "penguin", "panda", "owl", "monkey", "deer",
        "zebra", "lion", "elephant", "giraffe", "polar", "reindeer", "camel",
    ),
    "right": (
        "cat", "bunny", "lion", "elephant", "giraffe",
        "zebra", "polar", "reindeer", "monkey", "camel", "deer", "owl",
    ),
}

# Each world gets a cast that belongs there. The picker still avoids duplicate
# animals and falls back to the full pool if a preferred slot is taken.
WORLD_CASTS = {
    "garden": {
        "left": ("bunny", "cat"),
        "pond": ("frog", "duck"),
        "mid": ("hedgehog", "panda"),
        "right": ("bunny", "cat"),
    },
    "forest": {
        "left": ("deer",),
        "pond": ("frog",),
        "mid": ("owl",),
        "right": ("bunny",),
    },
    "beach": {
        "left": ("cat", "panda", "bunny"),
        "pond": ("duck", "frog"),
        "mid": ("penguin", "panda"),
        "right": ("cat", "bunny", "panda"),
    },
    "desert": {
        "left": ("camel", "hedgehog"),
        "pond": ("duck", "frog"),
        "mid": ("hedgehog", "camel"),
        "right": ("cat", "camel"),
    },
    "snow": {
        "left": ("polar",),
        "pond": ("penguin",),
        "mid": ("owl",),
        "right": ("reindeer",),
    },
    "jungle": {
        "left": ("monkey", "panda"),
        "pond": ("frog", "duck"),
        "mid": ("panda", "monkey"),
        "right": ("bunny", "monkey"),
    },
    "savanna": {
        "left": ("lion", "elephant", "giraffe"),
        "pond": ("frog",),
        "mid": ("elephant", "giraffe", "zebra"),
        "right": ("giraffe", "elephant", "lion"),
    },
    "autumn": {
        "left": ("deer", "bunny"),
        "pond": ("duck", "frog"),
        "mid": ("owl", "hedgehog"),
        "right": ("deer", "bunny"),
    },
    "cherry": {
        "left": ("bunny", "panda"),
        "pond": ("frog", "duck"),
        "mid": ("penguin", "panda"),
        "right": ("cat", "bunny"),
    },
    "lavender": {
        "left": ("bunny", "cat"),
        "pond": ("duck", "frog"),
        "mid": ("hedgehog", "panda"),
        "right": ("bunny", "cat"),
    },
    "bamboo": {
        "left": ("panda", "bunny", "cat"),
        "pond": ("frog", "duck"),
        "mid": ("penguin", "panda"),
        "right": ("cat", "bunny"),
    },
    "market": {
        "left": ("cat", "bunny"),
        "pond": ("duck", "frog"),
        "mid": ("panda", "hedgehog"),
        "right": ("cat", "bunny"),
    },
}
CAST_FILE = config.HISTORY_DIR / "storybook_cast.json"
VALID_ANIMALS = {name for options in CAST_CHOICES.values() for name in options}


def signature(cast: dict) -> str:
    return "-".join(cast[slot] for slot in SLOTS)


def _load() -> dict:
    if not CAST_FILE.exists():
        return {"recent": [], "updated": None}
    try:
        return json.loads(CAST_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"recent": [], "updated": None}


def _save(data: dict) -> None:
    CAST_FILE.parent.mkdir(parents=True, exist_ok=True)
    CAST_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _pick(world_set: str = "garden") -> dict:
    pools = WORLD_CASTS.get(world_set, CAST_CHOICES)
    used: set[str] = set()
    cast: dict[str, str] = {}
    for slot in SLOTS:
        options = [name for name in pools.get(slot, CAST_CHOICES[slot]) if name not in used]
        if not options:
            options = [name for name in CAST_CHOICES[slot] if name not in used]
        if not options:
            options = list(CAST_CHOICES[slot])
        name = random.choice(options)
        cast[slot] = name
        used.add(name)
    return cast


def next_storybook_cast(world_set: str = "garden") -> dict:
    """Return the next cast for a world and remember it so it does not repeat."""
    data = _load()
    recent = data.get("recent", [])
    chosen = None
    for _ in range(40):
        candidate = _pick(world_set)
        if signature(candidate) not in recent[-6:]:
            chosen = candidate
            break
    if chosen is None:
        last_sig = recent[-1] if recent else None
        for _ in range(80):
            candidate = _pick(world_set)
            if signature(candidate) != last_sig:
                chosen = candidate
                break
    if chosen is None:
        chosen = _pick(world_set)

    recent = (recent + [signature(chosen)])[-12:]
    data.update({"recent": recent, "updated": datetime.now().isoformat()})
    _save(data)
    print(
        f"[cast] {world_set}: "
        + " ".join(f"{slot}={chosen[slot]}" for slot in SLOTS)
        + f" ({len(recent)} recent casts)"
    )
    return chosen


def parse_cast(value: str) -> dict:
    """Parse --cast left,pond,mid,right (for manual previews)."""
    names = [part.strip().lower() for part in value.split(",") if part.strip()]
    if len(names) != len(SLOTS):
        raise SystemExit("--cast needs four animals: left,pond,mid,right")
    unknown = [name for name in names if name not in VALID_ANIMALS]
    if unknown:
        raise SystemExit(
            f"unknown cast animal(s): {', '.join(unknown)}. "
            f"Choose from: {', '.join(sorted(VALID_ANIMALS))}"
        )
    return dict(zip(SLOTS, names))


def main() -> int:
    cast = next_storybook_cast()
    print(json.dumps(cast, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
