"""Timeline assembly for the colour-block sample.

The whole reel is built against a hard duration budget (< 60 s). The builder
passes the real TTS durations in here first, then trims phrases until the
estimate fits.
"""

from __future__ import annotations

import config
from config import CATEGORY_META, PACE, RECIPE_BY_ID, THEMES


def _pace(recipe: dict) -> dict:
    return PACE.get(recipe.get("pace", "tight"), PACE["tight"])


def estimate_duration(clips: list, recipe: dict) -> float:
    """Exact duration for the current clip list, before timeline assembly."""
    p = _pace(recipe)
    intro = float(recipe.get("intro", config.INTRO_DURATION))
    outro = float(recipe.get("outro", config.OUTRO_DURATION))
    cursor = intro
    for clip in clips:
        cursor += (
            p["en_card_in"]
            + clip["en_duration"]
            + p["gap_en_native"]
            + p["native_card_lead"]
            + clip["vi_duration"]
            + p["gap_before_echo"]
            + clip["vi_duration"]
            + p["tail_hold"]
        )
    return round(cursor + outro, 3)


def build_timeline(phrases: list, audio: list, category: str, recipe: dict) -> dict:
    meta = CATEGORY_META[category]
    theme = THEMES[recipe["theme"]]
    p = _pace(recipe)
    intro = float(recipe.get("intro", config.INTRO_DURATION))
    outro = float(recipe.get("outro", config.OUTRO_DURATION))
    n = len(phrases)
    hook = config.HOOKS.get(recipe.get("hook", "count"), config.HOOKS["count"]).format(n=n)

    sfx = [
        {"t": 0.20, "kind": "pop", "gain": 0.32},
        {"t": 1.05, "kind": "chime", "gain": 0.24},
    ]
    fx = [
        {"t": 1.20, "x": 540, "y": 900, "count": 30, "power": 0.85},
    ]

    items = []
    cursor = intro

    for position, (phrase, clip) in enumerate(zip(phrases, audio)):
        start = cursor
        en_start = start + p["en_card_in"]
        en_end = en_start + clip["en_duration"]
        nat_reveal = en_end + p["gap_en_native"]
        vi_start = nat_reveal + p["native_card_lead"]
        vi_end = vi_start + clip["vi_duration"]
        vi_repeat_start = vi_end + p["gap_before_echo"]
        vi_repeat_end = vi_repeat_start + clip["vi_duration"]
        end = vi_repeat_end + p["tail_hold"]

        en_words = [
            {"t0": round(en_start + w["start"], 3), "t1": round(en_start + w["end"], 3)}
            for w in clip["en_words"]
        ]
        vi_words = [
            {"t0": round(vi_start + w["start"], 3), "t1": round(vi_start + w["end"], 3), "text": w.get("text", "")}
            for w in clip["vi_words"]
        ]
        vi_words_repeat = [
            {"t0": round(vi_repeat_start + w["start"], 3), "t1": round(vi_repeat_start + w["end"], 3), "text": w.get("text", "")}
            for w in clip["vi_words"]
        ]

        items.append({
            "index": position,
            "english": phrase["english"],
            "native": phrase["native"],
            "transliteration": phrase.get("transliteration", ""),
            "start": round(start, 3),
            "end": round(end, 3),
            "en_start": round(en_start, 3),
            "en_end": round(en_end, 3),
            "nat_reveal": round(nat_reveal, 3),
            "vi_start": round(vi_start, 3),
            "vi_end": round(vi_end, 3),
            "vi_repeat_start": round(vi_repeat_start, 3),
            "vi_repeat_end": round(vi_repeat_end, 3),
            "en_words": en_words,
            "vi_words": vi_words,
            "vi_words_repeat": vi_words_repeat,
        })

        sfx.extend([
            {"t": round(nat_reveal, 3), "kind": "pop", "gain": 0.38},
            {"t": round(vi_repeat_start, 3), "kind": "pop", "gain": 0.22},
            {"t": round(vi_repeat_end + 0.02, 3), "kind": "ding", "gain": 0.18},
        ])
        fx.append({"t": round(nat_reveal + 0.03, 3), "x": 540, "y": 900, "count": 34, "power": 0.95})
        fx.append({"t": round(vi_repeat_end + 0.04, 3), "x": 540, "y": 1180, "count": 18, "power": 0.7})
        fx.append({"t": round(start + 0.42, 3), "x": 900, "y": 300, "count": 12, "power": 0.55})

        cursor = end

    outro_start = cursor
    outro_end = outro_start + outro

    sfx.extend([
        {"t": round(outro_start + 0.20, 3), "kind": "success", "gain": 0.35},
        {"t": round(outro_start + 1.55, 3), "kind": "sparkle", "gain": 0.22},
    ])
    fx.extend([
        {"t": round(outro_start + 0.35, 3), "x": 540, "y": 760, "count": 28, "power": 0.85},
        {"t": round(outro_start + 1.65, 3), "x": 540, "y": 1040, "count": 22, "power": 0.8},
    ])

    # Prefer a short, complete phrase for the thumbnail: it reads at a glance.
    pool = items[:3] or items
    thumb = min(pool, key=lambda item: (len(item["english"]), item["index"]))
    thumb_t = round(thumb["nat_reveal"] + 0.85, 3) if items else 0.0

    return {
        "brand": config.BRAND,
        "brand_top": config.BRAND_LOCKUP_TOP,
        "brand_bottom": config.BRAND_LOCKUP_BOTTOM,
        "handle": config.HANDLE,
        "language": {
            "name": config.LANGUAGE["name"],
            "native": config.LANGUAGE["native_name"],
            "native_label": config.LANGUAGE["native_label"],
            "translit_label": config.LANGUAGE["translit_label"],
            "rtl": config.LANGUAGE.get("rtl", False),
            "char_tiles": config.LANGUAGE.get("char_tiles", False),
        },
        "category": {
            "english": category,
            "native": meta["native"],
            "icon": meta["icon"],
            "accent": meta["accent"],
        },
        "theme_id": recipe["theme"],
        "theme": theme,
        "recipe": recipe,
        "style": recipe.get("style", "poster"),
        "set": recipe.get("set", "garden"),
        "cast": recipe.get("cast") or {
            "left": "bunny",
            "pond": "frog",
            "mid": "hedgehog",
            "right": "cat",
        },
        "hook": hook,
        "music": recipe.get("music", "bright"),
        "streak": 7,
        "xp": len(items) * 10,
        "intro": {"start": 0.0, "end": intro},
        "phrases": items,
        "outro": {"start": round(outro_start, 3), "end": round(outro_end, 3)},
        "duration": round(outro_end, 3),
        "fps": config.FPS,
        "thumb_t": thumb_t,
        "sfx": sorted(sfx, key=lambda e: e["t"]),
        "fx": sorted(fx, key=lambda e: e["t"]),
    }
