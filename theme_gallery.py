"""Generate a visual gallery for every colour theme.

Outputs:
  output/theme_gallery/<theme>_intro.png    (1080x1920)
  output/theme_gallery/<theme>_phrase.png   (1080x1920)
  output/theme_gallery/contact_sheet.png
  output/theme_gallery/index.html
  output/theme_gallery/theme_showcase.mp4   (all themes, ~31 s)

The showcase uses the same lesson audio timings as the newest build, but it
plays one phrase slice per theme with a music bed. It is a design review asset,
not an upload.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

import config
from engine import audio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def newest_lesson() -> Path | None:
    latest = config.OUTPUT_DIR / "latest.txt"
    if latest.exists():
        candidate = Path(latest.read_text(encoding="utf-8").strip())
        if (candidate / "timeline.json").exists():
            return candidate
    folders = [p for p in config.LESSONS_DIR.glob("*") if (p / "timeline.json").exists()]
    return max(folders, key=lambda p: p.stat().st_mtime) if folders else None


def theme_timeline(base: dict, theme_id: str) -> dict:
    tl = copy.deepcopy(base)
    theme = copy.deepcopy(config.THEMES[theme_id])
    # In the gallery, phrase 1 should show the theme's signature colour, not
    # whatever world happens to sit at index 1 in the production rotation.
    signature = theme["bg"]
    secondary = theme.get("bg2", theme["worlds"][0])
    rest = [c for c in theme["worlds"] if c.lower() not in (signature.lower(), secondary.lower())]
    theme["worlds"] = [secondary, signature] + rest[:3]
    tl["theme_id"] = theme_id
    tl["theme"] = theme
    recipe = dict(tl.get("recipe") or {})
    recipe.update({"id": f"gallery-{theme_id}", "theme": theme_id})
    tl["recipe"] = recipe
    return tl


def open_page(browser, timeline: dict):
    page = browser.new_page(viewport={"width": config.VIDEO_WIDTH, "height": config.VIDEO_HEIGHT}, device_scale_factor=1)
    script = (
        "window.__TIMELINE__ = " + json.dumps(timeline, ensure_ascii=False) + ";"
        "window.__GALLERY_LABEL__ = true;"
    )
    page.add_init_script(script)
    page.goto((config.SCENE_DIR / "index.html").resolve().as_uri(), wait_until="load")
    page.wait_for_function("window.sceneReady === true", timeout=90000)
    page.evaluate("() => document.fonts.ready")
    return page


def make_stills(browser, base: dict, out_dir: Path) -> list[dict]:
    t_intro = 1.7
    first = base["phrases"][0]
    t_phrase = float(first["nat_reveal"]) + 0.9
    entries = []

    for i, (theme_id, theme) in enumerate(config.THEMES.items(), 1):
        tl = theme_timeline(base, theme_id)
        page = open_page(browser, tl)
        intro_path = out_dir / f"{theme_id}_intro.png"
        phrase_path = out_dir / f"{theme_id}_phrase.png"
        page.evaluate("t => window.seek(t)", t_intro)
        page.screenshot(path=str(intro_path), type="png")
        page.evaluate("t => window.seek(t)", t_phrase)
        page.screenshot(path=str(phrase_path), type="png")
        page.close()
        entries.append({"id": theme_id, "name": theme["name"], "intro": intro_path.name, "phrase": phrase_path.name})
        print(f"  [{i:2d}/{len(config.THEMES)}] {theme_id:8s} {theme['name']}")
    return entries


def _font(size: int, weight: str = "Bold"):
    path = config.SCENE_DIR / "fonts" / "Nunito-Variable.ttf"
    try:
        font = ImageFont.truetype(str(path), size)
        try:
            font.set_variation_by_name(weight)
        except Exception:
            pass
        return font
    except Exception:
        return ImageFont.load_default()


def make_contact_sheet(entries: list[dict], out_dir: Path) -> Path:
    cols = 5 if len(entries) > 12 else 4
    thumb_w = 250 if cols == 5 else 270
    thumb_h = 444 if cols == 5 else 480
    pad, gap, label_h, header = 22, 18, 32, 116
    rows = (len(entries) + cols - 1) // cols
    width = pad * 2 + cols * thumb_w + (cols - 1) * gap
    height = header + rows * (thumb_h + label_h) + (rows - 1) * gap + pad

    sheet = Image.new("RGB", (width, height), "#101014")
    draw = ImageDraw.Draw(sheet)
    title_font = _font(46, "Black")
    sub_font = _font(21, "Regular")

    draw.text((pad, 26), f"VELOCITY JAPANESE · {len(entries)} COLOUR THEMES", font=title_font, fill="#FFFDF6")
    draw.text((pad, 78), "Same lesson, same timings. Only the colour world changes.", font=sub_font, fill="#B9B4A8")

    for index, entry in enumerate(entries):
        col = index % cols
        row = index // cols
        x = pad + col * (thumb_w + gap)
        y = header + row * (thumb_h + label_h + gap)
        image_path = out_dir / entry["phrase"]
        image = Image.open(image_path).convert("RGB").resize((thumb_w, thumb_h), Image.LANCZOS)
        sheet.paste(image, (x, y))
        theme_font = _font(23, "Black")
        draw.text((x, y + thumb_h + 6), entry["name"].upper(), font=theme_font, fill="#FFFDF6")

    path = out_dir / "contact_sheet.png"
    sheet.save(path, "PNG")
    return path


def make_clips(showcase: Path, entries: list[dict], out_dir: Path, seconds: float) -> None:
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    for index, entry in enumerate(entries):
        out = clips_dir / f"{entry['id']}.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-ss", f"{index * seconds:.3f}", "-i", str(showcase),
                "-t", f"{seconds:.3f}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k",
                "-movflags", "+faststart", str(out),
            ],
            check=True,
        )
        entry["clip"] = f"clips/{entry['id']}.mp4"
        print(f"  clip: {out.name}")


def make_html(entries: list[dict], out_dir: Path, has_video: bool) -> Path:
    cards = []
    for entry in entries:
        theme = config.THEMES[entry["id"]]
        swatches = "".join(f'<i style="background:{c}"></i>' for c in theme["worlds"])
        clip = f'<a class="clip" href="{entry["clip"]}">▶ 2.4 s clip</a>' if entry.get("clip") else ""
        cards.append(f"""
        <section class="card">
          <div class="head"><h2>{entry['name']}</h2><span class="sw">{swatches}</span></div>
          <div class="shots">
            <img src="{entry['intro']}" alt="{entry['name']} intro" loading="lazy">
            <img src="{entry['phrase']}" alt="{entry['name']} phrase" loading="lazy">
          </div>
          <div class="meta">{entry['id']} · worlds {', '.join(theme['worlds'])}</div>
          {clip}
        </section>""")

    video = '<p><a class="btn" href="theme_showcase.mp4">▶ Watch the theme showcase</a></p>' if has_video else ""
    fulls = sorted(out_dir.glob("full_*.mp4"))
    if fulls:
        links = " · ".join(f'<a href="{p.name}">{p.stem.replace("_", " ")}</a>' for p in fulls)
        video += f'<p class="small">Full lessons: {links}</p>'
    audio_ab = out_dir / "audio_compare" / "old_vs_new.mp3"
    if audio_ab.exists():
        video += '<p class="small">Sound A/B: <a href="audio_compare/old_vs_new.mp3">old ding → new soft tap</a></p>'
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Velocity · colour themes</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #0e0e12; color: #FFFDF6; font-family: 'Nunito', system-ui, sans-serif; padding: 40px; }}
  h1 {{ font-size: 42px; margin: 0 0 8px; letter-spacing: -1px; }}
  p {{ color: #B9B4A8; margin: 0 0 26px; font-size: 18px; }}
  .grid {{ display: grid; grid-template-columns: repeat(4, 270px); gap: 26px; }}
  .card {{ background: #17171d; border: 1px solid #2a2a33; border-radius: 14px; overflow: hidden; }}
  .head {{ display: flex; align-items: center; justify-content: space-between; padding: 12px 12px 8px; gap: 8px; }}
  .head h2 {{ font-size: 15px; margin: 0; text-transform: uppercase; letter-spacing: 1px; }}
  .sw {{ display: flex; gap: 4px; }}
  .sw i {{ width: 12px; height: 12px; border-radius: 50%; border: 1px solid rgba(255,255,255,.5); }}
  .shots {{ display: flex; gap: 4px; padding: 0 8px; }}
  .shots img {{ width: 123px; height: 219px; object-fit: cover; border-radius: 6px; display: block; }}
  .meta {{ padding: 10px 12px 14px; font-size: 11px; color: #8D887E; }}
  .clip {{ display: inline-block; margin: 0 12px 14px; color: #FFB703; font-weight: 800; font-size: 12px; text-decoration: none; }}
  .small {{ font-size: 14px; color: #B9B4A8; }}
  .small a {{ color: #FFB703; text-decoration: none; font-weight: 700; }}
  .btn {{ display: inline-block; background: #FF6B35; color: #fff; padding: 12px 20px; border-radius: 999px; text-decoration: none; font-weight: 800; }}
  @media (max-width: 1250px) {{ .grid {{ grid-template-columns: repeat(2, 270px); }} }}
</style></head>
<body>
<h1>Velocity Japanese · colour themes</h1>
<p>{len(entries)} colour worlds. Same lesson, same timings. Click any image for full resolution.</p>
{video}
<div class="grid">{''.join(cards)}</div>
</body></html>"""
    path = out_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return path


def make_showcase(browser, base: dict, out_dir: Path, seconds_per_theme: float, fps: int) -> Path:
    total_frames = int(round(len(config.THEMES) * seconds_per_theme * fps))
    silent = out_dir / "work" / "showcase_silent.mp4"
    silent.parent.mkdir(parents=True, exist_ok=True)
    video = out_dir / "theme_showcase.mp4"
    log = out_dir / "work" / "showcase_ffmpeg.log"
    first = base["phrases"][0]
    start = float(first["nat_reveal"]) + 0.6

    print(f"[showcase] {total_frames} frames · {len(config.THEMES)} themes · {seconds_per_theme}s each")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(fps), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", str(silent),
    ]
    log_handle = open(log, "wb")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log_handle)
    t0 = time.time()
    written = 0
    try:
        for ti, theme_id in enumerate(config.THEMES):
            tl = theme_timeline(base, theme_id)
            page = open_page(browser, tl)
            for f in range(int(round(seconds_per_theme * fps))):
                t = start + f / fps
                page.evaluate("t => window.seek(t)", t)
                jpg = page.screenshot(type="jpeg", quality=92)
                proc.stdin.write(jpg)
                written += 1
                if written % 60 == 0:
                    elapsed = time.time() - t0
                    print(f"  {written}/{total_frames} frames  {written/elapsed:.1f} fps")
            page.close()
            print(f"  theme {ti + 1}/{len(config.THEMES)}: {theme_id}")
        proc.stdin.close()
        code = proc.wait()
        if code != 0:
            print(log.read_text(errors="ignore")[-2000:])
            raise RuntimeError("showcase video encoding failed")
    finally:
        if proc.poll() is None:
            proc.kill()
        log_handle.close()

    duration = total_frames / fps
    music = audio.synth_music(duration + 0.2, "bright")
    wav = out_dir / "work" / "showcase_music.wav"
    audio._write_wav(wav, music)

    fade_out = max(0.0, duration - 1.2)
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(silent), "-i", str(wav),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-af", f"afade=t=in:st=0:d=0.7,afade=t=out:st={fade_out:.2f}:d=1.2",
            "-shortest", "-movflags", "+faststart", str(video),
        ],
        check=True,
    )
    size_mb = video.stat().st_size / (1024 * 1024)
    print(f"[showcase] {video.name} ({duration:.1f}s, {size_mb:.1f} MB)")
    return video


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a gallery for all colour themes")
    parser.add_argument("--lesson", type=Path, help="lesson folder (default: newest)")
    parser.add_argument("--out", type=Path, help="output folder (default: output/theme_gallery)")
    parser.add_argument("--skip-video", action="store_true", help="stills + contact sheet only")
    parser.add_argument("--seconds-per-theme", type=float, default=2.4)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--themes", help="comma separated theme ids (default: all)")
    args = parser.parse_args()

    lesson = args.lesson or newest_lesson()
    if lesson is None:
        raise SystemExit("No lesson found. Build one first: python build.py --recipe citrus-4-tight")
    base = json.loads((lesson / "timeline.json").read_text(encoding="utf-8"))
    out_dir = args.out or (config.OUTPUT_DIR / "theme_gallery")
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.themes:
        wanted = [x.strip() for x in args.themes.split(",") if x.strip()]
        unknown = [x for x in wanted if x not in config.THEMES]
        if unknown:
            raise SystemExit(f"Unknown themes: {', '.join(unknown)}")
        selected = {k: v for k, v in config.THEMES.items() if k in wanted}
    else:
        selected = dict(config.THEMES)

    # Keep the original order and allow a subset without touching config.
    global_order = list(config.THEMES.keys())
    ordered = {k: selected[k] for k in global_order if k in selected}
    original = config.THEMES
    config.THEMES = ordered
    try:
        print(f"[gallery] lesson: {lesson.name}  ·  {len(ordered)} themes")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
            entries = make_stills(browser, base, out_dir)
            contact = make_contact_sheet(entries, out_dir)
            print(f"[gallery] contact sheet: {contact}")
            has_video = not args.skip_video
            if has_video:
                video = make_showcase(browser, base, out_dir, args.seconds_per_theme, args.fps)
                print(f"[gallery] showcase: {video}")
                make_clips(video, entries, out_dir, args.seconds_per_theme)
            browser.close()
        page = make_html(entries, out_dir, has_video)
        (out_dir / "themes.json").write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[gallery] gallery: {page}")
        print(f"[gallery] open: {page.resolve().as_uri()}")
    finally:
        config.THEMES = original
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
