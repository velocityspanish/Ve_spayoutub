"""Render the same storybook lesson in every theme and build a contact sheet.

    python storybook_palette_gallery.py
    python storybook_palette_gallery.py --generated 10
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
from storybook_set import SETS as STORYBOOK_SETS
from theme_builder import load_registry

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def newest_storybook() -> Path | None:
    folders = [p for p in config.LESSONS_DIR.glob("Storybook_*") if (p / "timeline.json").exists()]
    return max(folders, key=lambda p: p.stat().st_mtime) if folders else None


def theme_timeline(base: dict, theme_id: str, theme: dict, world_set: str = "garden") -> dict:
    tl = copy.deepcopy(base)
    t = copy.deepcopy(theme)
    signature = t["bg"]
    secondary = t.get("bg2", t["worlds"][0])
    rest = [c for c in t["worlds"] if c.lower() not in (signature.lower(), secondary.lower())]
    t["worlds"] = [secondary, signature] + rest[:3]
    tl["theme_id"] = theme_id
    tl["theme"] = t
    tl["set"] = world_set
    recipe = dict(tl.get("recipe") or {})
    recipe.update({"id": f"gallery-{theme_id}", "theme": theme_id, "style": "storybook", "set": world_set})
    tl["recipe"] = recipe
    return tl


def stills(browser, base: dict, entries: list[tuple[str, dict]], scene_dir: Path, out_dir: Path, world_set: str = "garden") -> list[dict]:
    first = base["phrases"][0]
    t = float(first["nat_reveal"]) + 0.9
    saved = []
    for i, (theme_id, theme) in enumerate(entries, 1):
        tl = theme_timeline(base, theme_id, theme, world_set)
        page = browser.new_page(viewport={"width": config.VIDEO_WIDTH, "height": config.VIDEO_HEIGHT})
        page.add_init_script("window.__TIMELINE__ = " + json.dumps(tl, ensure_ascii=False) + ";")
        page.goto((scene_dir / "index.html").resolve().as_uri(), wait_until="load")
        page.wait_for_function("window.sceneReady === true", timeout=90000)
        page.evaluate("t => window.seek(t)", t)
        path = out_dir / f"{i:02d}_{theme_id}.png"
        page.screenshot(path=str(path), type="png")
        page.close()
        saved.append({"id": theme_id, "name": theme["name"], "image": path.name, "theme": theme})
        print(f"  [{i:02d}/{len(entries)}] {theme_id:24s} {theme['name']}")
    return saved


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


def contact_sheet(entries: list[dict], out_dir: Path) -> Path:
    cols = 5
    thumb_w, thumb_h = 250, 444
    pad, gap, label_h, header = 22, 16, 42, 108
    rows = (len(entries) + cols - 1) // cols
    width = pad * 2 + cols * thumb_w + (cols - 1) * gap
    height = header + rows * (thumb_h + label_h) + (rows - 1) * gap + pad
    sheet = Image.new("RGB", (width, height), "#101014")
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 24), f"STORYBOOK PALETTE DECK · {len(entries)} PALETTES", font=_font(40), fill="#FFFDF6")
    draw.text((pad, 72), "Same world on purpose. Only the colour palette changes. Use storybook_set_gallery.py for worlds.", font=_font(20, "Regular"), fill="#B9B4A8")

    for index, entry in enumerate(entries):
        col = index % cols
        row = index // cols
        x = pad + col * (thumb_w + gap)
        y = header + row * (thumb_h + label_h + gap)
        image = Image.open(out_dir / entry["image"]).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x, y + thumb_h + 4), entry["name"].upper(), font=_font(19), fill="#FFFDF6")
        sw = entry["theme"].get("worlds", [])
        for k, color in enumerate(sw[:5]):
            draw.ellipse((x + k * 18, y + thumb_h + 27, x + k * 18 + 13, y + thumb_h + 40), fill=color, outline="#FFFDF6", width=1)
    path = out_dir / "contact_sheet.png"
    sheet.save(path, "PNG")
    return path


def gallery_html(entries: list[dict], out_dir: Path) -> Path:
    cards = []
    for entry in entries:
        sw = "".join(f'<i style="background:{c}"></i>' for c in entry["theme"].get("worlds", []))
        cards.append(f'<section class="card"><img src="{entry["image"]}" loading="lazy"><h2>{entry["name"]}</h2><div class="sw">{sw}</div><code>{entry["id"]}</code></section>')
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Storybook palettes</title>
<style>
body {{ margin:0; padding:34px; background:#0e0e12; color:#FFFDF6; font-family:system-ui,sans-serif; }}
h1 {{ margin:0 0 6px; }} p {{ color:#B9B4A8; margin:0 0 24px; }}
.grid {{ display:grid; grid-template-columns:repeat(5, 250px); gap:22px; }}
.card {{ background:#17171d; border:1px solid #2a2a33; border-radius:14px; overflow:hidden; }}
.card img {{ width:250px; height:444px; object-fit:cover; display:block; }}
h2 {{ font-size:14px; margin:10px 12px 6px; text-transform:uppercase; letter-spacing:1px; }}
.sw {{ display:flex; gap:4px; margin:0 12px 8px; }} .sw i {{ width:12px; height:12px; border-radius:50%; border:1px solid #fff8; }}
code {{ display:block; padding:0 12px 12px; font-size:10px; color:#8D887E; }}
a {{ color:#FFB703; }}
</style></head><body>
<h1>Storybook palette deck</h1>
<p>{len(entries)} palettes. Same world and timing. Worlds: run storybook_set_gallery.py.</p>
<div class="grid">{''.join(cards)}</div>
</body></html>"""
    path = out_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the storybook deck")
    parser.add_argument("--lesson", type=Path)
    parser.add_argument("--generated", type=int, default=10, help="number of generated palettes to include")
    parser.add_argument("--set", dest="world_set", choices=STORYBOOK_SETS, default="garden")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    lesson = args.lesson or newest_storybook()
    if lesson is None:
        raise SystemExit("No Storybook lesson found. Build one first.")
    base = json.loads((lesson / "timeline.json").read_text(encoding="utf-8"))
    out_dir = args.out or (config.OUTPUT_DIR / "storybook_palettes")
    out_dir.mkdir(parents=True, exist_ok=True)
    scene_dir = config.SCENE_DIRS["storybook"]

    curated = [(tid, theme) for tid, theme in config.THEMES.items()]
    generated = []
    if args.generated:
        reg = list(load_registry().items())[-args.generated:]
        generated = [(tid, {k: v for k, v in theme.items() if k != "created_at"}) for tid, theme in reg]
    entries = curated + generated
    print(f"[palettes] {len(curated)} curated + {len(generated)} generated = {len(entries)} palettes")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        saved = stills(browser, base, entries, scene_dir, out_dir, args.world_set)
        browser.close()
    (out_dir / "themes.json").write_text(json.dumps(saved, indent=2, ensure_ascii=False), encoding="utf-8")
    sheet = contact_sheet(saved, out_dir)
    page = gallery_html(saved, out_dir)
    print(f"[palettes] contact sheet: {sheet}")
    print(f"[palettes] gallery: {page}")
    print(f"[palettes] open: {page.resolve().as_uri()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
