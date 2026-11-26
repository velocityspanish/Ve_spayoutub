"""Seed-based colour theme builder.

13 curated themes are the safe set. This module generates new themes when you
want a colour world that is not in the curated deck.

    python theme_builder.py --count 5
    python build.py --recipe storybook-3 --new-theme
"""

from __future__ import annotations

import argparse
import colorsys
import json
import random
import sys
from datetime import datetime
from pathlib import Path

import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

REGISTRY = config.HISTORY_DIR / "generated_themes.json"

ADJECTIVES = [
    "Sunny", "Jolly", "Breezy", "Cosmic", "Tiny", "Happy", "Wild", "Golden",
    "Minty", "Coral", "Electric", "Dreamy", "Lucky", "Fizzy", "Bright",
]
NOUNS = [
    "Jungle", "Harbor", "Planet", "Meadow", "Candy", "Ocean", "Garden",
    "Sky", "Market", "Island", "Comet", "Picnic", "Lagoon", "Festival",
]


def _hsl(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l, s)
    return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"


def generate_theme(seed: int | None = None) -> tuple[str, dict]:
    """Return (theme_id, theme). The palette is a balanced 5-hue set."""
    if seed is None:
        seed = random.randrange(1, 10_000_000)
    rnd = random.Random(seed)
    h = rnd.randrange(0, 360)
    bg = _hsl(h, 0.72, 0.47)
    bg2 = _hsl(h + 38, 0.80, 0.60)
    card = _hsl(h + 12, 0.32, 0.97)
    ink = _hsl(h, 0.58, 0.13)
    colors = [
        _hsl(h + 180, 0.82, 0.56),
        _hsl(h + 60, 0.84, 0.57),
        _hsl(h + 300, 0.78, 0.60),
        _hsl(h + 120, 0.72, 0.52),
        _hsl(h + 240, 0.78, 0.58),
    ]
    words = f"{rnd.choice(ADJECTIVES)} {rnd.choice(NOUNS)}"
    theme_id = f"gen-{seed}-{rnd.randrange(100, 999)}"
    theme = {
        "name": words,
        "bg": bg,
        "bg2": bg2,
        "card": card,
        "ink": ink,
        "colors": colors,
        "worlds": [bg, bg2, colors[0], colors[1], colors[2]],
    }
    return theme_id, theme


def load_registry() -> dict:
    if not REGISTRY.exists():
        return {}
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_theme(theme_id: str, theme: dict) -> None:
    data = load_registry()
    data[theme_id] = {**theme, "created_at": datetime.now().isoformat()}
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def create_theme(seed: int | None = None) -> tuple[str, dict]:
    theme_id, theme = generate_theme(seed)
    save_theme(theme_id, theme)
    return theme_id, theme


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate colour themes")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--no-save", action="store_true")
    args = parser.parse_args()
    for i in range(args.count):
        seed = args.seed + i if args.seed is not None else None
        theme_id, theme = generate_theme(seed)
        if not args.no_save:
            save_theme(theme_id, theme)
        print(f"{theme_id:24s} {theme['name']:18s} bg={theme['bg']}  colors={' '.join(theme['colors'])}")
    print(f"\nregistry: {REGISTRY}" if not args.no_save else "\nnot saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
