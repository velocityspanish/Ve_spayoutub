"""Timeline assembly: scene timings, karaoke word clocks, SFX and confetti cues."""

from __future__ import annotations

import config
from config import CATEGORY_META


def build_timeline(phrases: list, audio: list, category: str) -> dict:
    meta = CATEGORY_META[category]

    sfx = [
        {"t": 0.25, "kind": "pop", "gain": 0.55},
        {"t": 0.95, "kind": "whoosh", "gain": 0.45},
        {"t": 1.95, "kind": "chime", "gain": 0.55},
        {"t": 2.92, "kind": "success", "gain": 0.5},
    ]
    fx = [
        {"t": 2.96, "x": 540, "y": 1010, "count": 44, "power": 1.05},
    ]

    items = []
    cursor = config.INTRO_DURATION

    for phrase, clip in zip(phrases, audio):
        start = cursor
        en_start = start + config.EN_CARD_IN
        en_end = en_start + clip["en_duration"]
        nat_reveal = en_end + config.GAP_EN_NATIVE
        vi_start = nat_reveal + config.NATIVE_CARD_LEAD
        vi_end = vi_start + clip["vi_duration"]
        vi_repeat_start = vi_end + config.GAP_BEFORE_REPEAT
        vi_repeat_end = vi_repeat_start + clip["vi_duration"]
        end = vi_repeat_end + config.TAIL_HOLD

        en_words = [
            {"t0": round(en_start + w["start"], 3), "t1": round(en_start + w["end"], 3)}
            for w in clip["en_words"]
        ]
        vi_words = [
            {"t0": round(vi_start + w["start"], 3), "t1": round(vi_start + w["end"], 3)}
            for w in clip["vi_words"]
        ]
        vi_words_repeat = [
            {"t0": round(vi_repeat_start + w["start"], 3), "t1": round(vi_repeat_start + w["end"], 3)}
            for w in clip["vi_words"]
        ]

        items.append({
            "index": clip["index"],
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
            {"t": round(start + 0.03, 3), "kind": "whoosh", "gain": 0.32},
            {"t": round(nat_reveal, 3), "kind": "pop", "gain": 0.6},
            {"t": round(vi_repeat_start, 3), "kind": "pop", "gain": 0.42},
            {"t": round(vi_repeat_end + 0.03, 3), "kind": "ding", "gain": 0.5},
        ])
        fx.append({"t": round(nat_reveal + 0.04, 3), "x": 540, "y": 940, "count": 38, "power": 1.0})

        cursor = end

    outro_start = cursor
    outro_end = outro_start + config.OUTRO_DURATION

    sfx.extend([
        {"t": round(outro_start + 0.25, 3), "kind": "success", "gain": 0.72},
        {"t": round(outro_start + 2.05, 3), "kind": "sparkle", "gain": 0.55},
    ])
    fx.extend([
        {"t": round(outro_start + 0.4, 3), "x": 540, "y": 780, "count": 30, "power": 0.9},
        {"t": round(outro_start + 2.15, 3), "x": 540, "y": 1030, "count": 24, "power": 0.85},
    ])

    thumb_index = 1 if len(items) > 1 else 0
    thumb_t = round(items[thumb_index]["nat_reveal"] + 0.95, 3) if items else 0.0

    return {
        "brand": config.BRAND,
        "brand_top": config.BRAND_LOCKUP_TOP,
        "brand_bottom": config.BRAND_LOCKUP_BOTTOM,
        "handle": config.HANDLE,
        "mascot": config.MASCOT_NAME,
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
        "streak": 7,
        "xp": len(items) * 10,
        "intro": {"start": 0.0, "end": config.INTRO_DURATION},
        "phrases": items,
        "outro": {"start": round(outro_start, 3), "end": round(outro_end, 3)},
        "duration": round(outro_end, 3),
        "fps": config.FPS,
        "thumb_t": thumb_t,
        "sfx": sorted(sfx, key=lambda e: e["t"]),
        "fx": sorted(fx, key=lambda e: e["t"]),
    }
