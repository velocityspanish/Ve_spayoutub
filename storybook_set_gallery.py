"""Render the storybook visual sets and build a contact sheet.

    python storybook_set_gallery.py
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

import config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SCENARIOS = [
    ("Garden", "garden", "duo", {"left": "bunny", "pond": "frog", "mid": "hedgehog", "right": "cat"}),
    ("Forest", "forest", "forest", {"left": "deer", "pond": "frog", "mid": "owl", "right": "cat"}),
    ("Beach", "beach", "ocean", {"left": "cat", "pond": "duck", "mid": "penguin", "right": "bunny"}),
    ("Desert", "desert", "mango", {"left": "camel", "pond": "duck", "mid": "hedgehog", "right": "cat"}),
    ("Snow", "snow", "cobalt", {"left": "polar", "pond": "penguin", "mid": "owl", "right": "reindeer"}),
    ("Jungle", "jungle", "forest", {"left": "monkey", "pond": "frog", "mid": "panda", "right": "cat"}),
    ("Savanna", "savanna", "sunset", {"left": "lion", "pond": "frog", "mid": "elephant", "right": "giraffe"}),
    ("Autumn", "autumn", "mango", {"left": "deer", "pond": "duck", "mid": "owl", "right": "cat"}),
    ("Cherry", "cherry", "rose", {"left": "bunny", "pond": "frog", "mid": "penguin", "right": "cat"}),
    ("Lavender", "lavender", "grape", {"left": "bunny", "pond": "duck", "mid": "hedgehog", "right": "cat"}),
    ("Bamboo", "bamboo", "forest", {"left": "panda", "pond": "frog", "mid": "penguin", "right": "cat"}),
    ("Market", "market", "sunset", {"left": "cat", "pond": "duck", "mid": "panda", "right": "bunny"}),
]


def newest_storybook() -> Path | None:
    folders = [p for p in config.LESSONS_DIR.glob("Storybook_*") if (p / "timeline.json").exists()]
    return max(folders, key=lambda p: p.stat().st_mtime) if folders else None


def _font(size: int, weight: str = "Black"):
    try:
        font = ImageFont.truetype(str(config.SCENE_DIRS["storybook"] / "fonts" / "Nunito-Variable.ttf"), size)
        try:
            font.set_variation_by_name(weight)
        except Exception:
            pass
        return font
    except Exception:
        return ImageFont.load_default()


def render_sets(base: dict, out_dir: Path) -> list[dict]:
    first = base["phrases"][0]
    t = float(first["nat_reveal"]) + 0.9
    saved = []
    scene_dir = config.SCENE_DIRS["storybook"]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        for i, (label, world_set, theme_id, cast) in enumerate(SCENARIOS, 1):
            tl = copy.deepcopy(base)
            tl["set"] = world_set
            tl["cast"] = cast
            tl["theme_id"] = theme_id
            tl["theme"] = config.THEMES[theme_id]
            recipe = dict(tl.get("recipe") or {})
            recipe.update({"id": f"set-{i}", "set": world_set, "theme": theme_id, "cast": cast})
            tl["recipe"] = recipe
            page = browser.new_page(viewport={"width": config.VIDEO_WIDTH, "height": config.VIDEO_HEIGHT})
            page.add_init_script("window.__TIMELINE__ = " + json.dumps(tl, ensure_ascii=False) + ";")
            page.goto((scene_dir / "index.html").resolve().as_uri(), wait_until="load")
            page.wait_for_function("window.sceneReady === true", timeout=90000)
            page.evaluate("t => window.seek(t)", t)
            path = out_dir / f"{i:02d}_{world_set}_{theme_id}.png"
            page.screenshot(path=str(path), type="png")
            page.close()
            saved.append({
                "label": label,
                "set": world_set,
                "theme": config.THEMES[theme_id]["name"],
                "cast": cast,
                "image": path.name,
            })
            print(f"  [{i:02d}/{len(SCENARIOS)}] {label:14s} {world_set:7s} {theme_id:8s}")
        browser.close()
    return saved


def contact_sheet(entries: list[dict], out_dir: Path) -> Path:
    cols = 4
    thumb_w, thumb_h = 250, 444
    pad, gap, label_h, header = 22, 16, 68, 108
    rows = (len(entries) + cols - 1) // cols
    width = pad * 2 + cols * thumb_w + (cols - 1) * gap
    height = header + rows * (thumb_h + label_h) + (rows - 1) * gap + pad
    sheet = Image.new("RGB", (width, height), "#101014")
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 24), f"STORYBOOK WORLDS · {len(entries)} WORLDS", font=_font(40), fill="#FFFDF6")
    draw.text((pad, 72), "Same book. Different worlds. Different animal casts.", font=_font(20, "Regular"), fill="#B9B4A8")

    for index, entry in enumerate(entries):
        col = index % cols
        row = index // cols
        x = pad + col * (thumb_w + gap)
        y = header + row * (thumb_h + label_h + gap)
        image = Image.open(out_dir / entry["image"]).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x, y + thumb_h + 5), entry["label"].upper(), font=_font(19), fill="#FFFDF6")
        detail = f"{entry['set'].upper()} · {entry['theme'].upper()}"
        draw.text((x, y + thumb_h + 29), detail, font=_font(13, "Regular"), fill="#B9B4A8")
        cast = " · ".join(entry["cast"][slot] for slot in ("left", "pond", "mid", "right"))
        draw.text((x, y + thumb_h + 46), cast.upper(), font=_font(12, "Regular"), fill="#7F7A72")
    path = out_dir / "contact_sheet.png"
    sheet.save(path, "PNG")
    return path


def scene_sheet(entries: list[dict], out_dir: Path) -> Path:
    """Crop the lower half of every frame so the worlds are easy to compare."""
    cols = 4
    thumb_w, thumb_h = 250, 190
    pad, gap, label_h, header = 22, 16, 44, 96
    rows = (len(entries) + cols - 1) // cols
    width = pad * 2 + cols * thumb_w + (cols - 1) * gap
    height = header + rows * (thumb_h + label_h) + (rows - 1) * gap + pad
    sheet = Image.new("RGB", (width, height), "#101014")
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 22), f"WORLD SCENES · {len(entries)} BACKGROUNDS", font=_font(38), fill="#FFFDF6")
    draw.text((pad, 66), "Bottom of frame only. Same book, different world and animals.", font=_font(18, "Regular"), fill="#B9B4A8")

    for index, entry in enumerate(entries):
        col = index % cols
        row = index // cols
        x = pad + col * (thumb_w + gap)
        y = header + row * (thumb_h + label_h + gap)
        image = Image.open(out_dir / entry["image"]).convert("RGB")
        image = image.crop((0, 1120, 1080, 1920)).resize((thumb_w, thumb_h), Image.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x, y + thumb_h + 5), entry["label"].upper(), font=_font(16), fill="#FFFDF6")
        draw.text((x, y + thumb_h + 24), entry["theme"].upper(), font=_font(11, "Regular"), fill="#B9B4A8")
    path = out_dir / "world_scenes.png"
    sheet.save(path, "PNG")
    return path


def gallery_html(entries: list[dict], out_dir: Path) -> Path:
    cards = []
    for entry in entries:
        cast = " · ".join(entry["cast"][slot] for slot in ("left", "pond", "mid", "right"))
        cards.append(
            f'<section class="card"><img src="{entry["image"]}" loading="lazy">'
            f'<h2>{entry["label"]}</h2><p>{entry["set"].upper()} · {entry["theme"]}</p>'
            f'<code>{cast}</code></section>'
        )
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Storybook worlds</title>
<style>
body {{ margin:0; padding:34px; background:#0e0e12; color:#FFFDF6; font-family:system-ui,sans-serif; }}
h1 {{ margin:0 0 6px; }} .lead {{ color:#B9B4A8; margin:0 0 24px; }}
.grid {{ display:grid; grid-template-columns:repeat(4, 250px); gap:22px; }}
.card {{ background:#17171d; border:1px solid #2a2a33; border-radius:14px; overflow:hidden; }}
.card img {{ width:250px; height:444px; object-fit:cover; display:block; }}
h2 {{ font-size:14px; margin:10px 12px 2px; text-transform:uppercase; letter-spacing:1px; }}
p {{ margin:0 12px 4px; font-size:11px; color:#B9B4A8; }}
code {{ display:block; padding:0 12px 12px; font-size:10px; color:#7F7A72; }}
</style></head><body>
<h1>Storybook worlds</h1>
<p class="lead">{len(entries)} different worlds. The book and timing are shared; the world and animal cast are not.</p>
<div class="grid">{''.join(cards)}</div>
</body></html>"""
    path = out_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the storybook visual sets")
    parser.add_argument("--lesson", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    lesson = args.lesson or newest_storybook()
    if lesson is None:
        raise SystemExit("No Storybook lesson found. Build one first.")
    base = json.loads((lesson / "timeline.json").read_text(encoding="utf-8"))
    out_dir = args.out or (config.OUTPUT_DIR / "storybook_worlds")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[worlds] lesson: {lesson.name}")
    saved = render_sets(base, out_dir)
    (out_dir / "sets.json").write_text(json.dumps(saved, indent=2), encoding="utf-8")
    sheet = contact_sheet(saved, out_dir)
    scenes = scene_sheet(saved, out_dir)
    page = gallery_html(saved, out_dir)
    print(f"[worlds] contact sheet: {sheet}")
    print(f"[worlds] scene sheet: {scenes}")
    print(f"[worlds] gallery: {page}")
    print(f"[worlds] open: {page.resolve().as_uri()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
