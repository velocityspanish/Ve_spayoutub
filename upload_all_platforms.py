"""Publish the latest Velocity lesson to every connected platform."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "upload"
sys.path.insert(0, str(UPLOAD_DIR))
sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(ROOT / ".env")

import config

BRAND = config.BRAND
HANDLE = config.HANDLE
HASHTAGS = config.HASHTAGS
LANG_NAME = config.LANGUAGE["name"]

uploaders = {
    "facebook": ("upload_facebook", "upload_to_facebook"),
    "instagram": ("upload_instagram", "upload_to_instagram"),
    "youtube": ("upload_to_youtube", "upload_to_youtube"),
    "vk": ("upload_vk", "upload_to_vk"),
    "telegram": ("upload_telegram", "upload_to_telegram"),
    "twitter": ("upload_twitter", "upload_to_twitter"),
    "threads": ("upload_threads", "upload_to_threads"),
    "tiktok": ("upload_tiktok", "upload_to_tiktok"),
}

CREDS = {
    "facebook": ["FACEBOOK_ACCESS_TOKEN", "FACEBOOK_PAGE_ID"],
    "instagram": ["INSTAGRAM_ACCESS_TOKEN"],
    "youtube": ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"],
    "vk": ["VK_ACCESS_TOKEN", "VK_GROUP_ID"],
    "telegram": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID"],
    "twitter": ["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"],
    "threads": ["THREADS_ACCESS_TOKEN", "THREADS_USER_ID"],
    "tiktok": ["TIKTOK_ACCESS_TOKEN"],
}


def _env(*names):
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""

DISPLAY = {
    "facebook": "Facebook", "instagram": "Instagram", "youtube": "YouTube", "vk": "VK",
    "telegram": "Telegram", "twitter": "Twitter/X", "threads": "Threads", "tiktok": "TikTok",
}


def load_uploaders():
    funcs = {}
    for key, (module_name, func_name) in uploaders.items():
        try:
            module = __import__(module_name, fromlist=[func_name])
            funcs[key] = getattr(module, func_name)
        except Exception as exc:
            print(f"[!] {DISPLAY[key]} uploader unavailable: {exc}")
    return funcs


def find_latest_lesson(lesson: str | None) -> Path | None:
    if lesson:
        path = Path(lesson)
        if path.is_file():
            path = path.parent
        return path if (path / "final_reel.mp4").exists() else None
    candidates = list((ROOT / "output" / "lessons").glob("*/final_reel.mp4"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime).parent


def load_lesson(folder: Path) -> dict:
    meta = {}
    meta_file = folder / "metadata.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    return {
        "folder": folder,
        "video": folder / "final_reel.mp4",
        "thumbnail": folder / "thumbnail.jpg",
        "category": meta.get("category_english", LANG_NAME),
        "category_native": meta.get("category_native", ""),
        "phrases": meta.get("phrases", []),
        "hashtags": meta.get("hashtags", HASHTAGS),
        "meta": meta,
    }


def phrase_block(phrases: list, count: int) -> list[str]:
    lines = []
    for i, p in enumerate(phrases[:count], 1):
        lines.append(f"{i}. {p.get('english', '')}")
        lines.append(f"   {p.get('native', '')}")
        if p.get("transliteration"):
            lines.append(f"   [{p['transliteration']}]")
        lines.append("")
    return lines


def long_caption(lesson: dict) -> str:
    cat = lesson["category"]
    lines = [
        f"Learn {LANG_NAME} with {BRAND}!",
        "",
        f"Today's lesson: {cat}" + (f" · {lesson['category_native']}" if lesson["category_native"] else ""),
        "",
        "Repeat each phrase out loud. Then say it one more time, faster!",
        "",
    ]
    lines += phrase_block(lesson["phrases"], 5)
    lines += [
        "Save this lesson and practice tomorrow.",
        f"Follow {HANDLE} for a new {LANG_NAME} lesson every day.",
        "",
        " ".join(lesson["hashtags"]),
    ]
    return "\n".join(lines)


def short_caption(lesson: dict) -> str:
    p = lesson["phrases"]
    pairs = [f"{x.get('english', '')} = {x.get('native', '')}" for x in p[:2]]
    text = f"Learn {LANG_NAME}: {' | '.join(pairs)}"
    tags = " " + " ".join(lesson["hashtags"][:2])
    if len(text) + len(tags) > 278:
        text = text[: 278 - len(tags) - 1].rstrip(" |") + "…"
    return text + tags


def threads_caption(lesson: dict) -> str:
    lines = [f"{BRAND} · {lesson['category']}", ""]
    for p in lesson["phrases"][:3]:
        lines.append(f"{p.get('english', '')} → {p.get('native', '')}")
    lines += ["", f"New lesson every day {HANDLE}", "", " ".join(lesson["hashtags"][:5])]
    text = "\n".join(lines)
    return text[:495]


def missing_creds(platform: str) -> list[str]:
    if platform == "facebook":
        token = _env("FACEBOOK_ACCESS_TOKEN", "FB_PAGE_ACCESS_TOKEN", "FB_ACCESS_TOKEN")
        page = _env("FACEBOOK_PAGE_ID", "FB_PAGE_ID")
        return [name for name, value in (("FACEBOOK_ACCESS_TOKEN", token), ("FACEBOOK_PAGE_ID", page)) if not value]
    if platform == "instagram":
        return [] if _env("INSTAGRAM_ACCESS_TOKEN", "IG_ACCESS_TOKEN") else ["INSTAGRAM_ACCESS_TOKEN"]
    if platform == "youtube":
        return [] if all(_env(a, b) for a, b in (
            ("YT_CLIENT_ID", "YOUTUBE_CLIENT_ID"),
            ("YT_CLIENT_SECRET", "YOUTUBE_CLIENT_SECRET"),
            ("YT_REFRESH_TOKEN", "YOUTUBE_REFRESH_TOKEN"),
        )) else ["YT_CLIENT_ID"]
    if platform == "telegram":
        return [name for name, value in (
            ("TELEGRAM_BOT_TOKEN", _env("TELEGRAM_BOT_TOKEN")),
            ("TELEGRAM_CHANNEL_ID", _env("TELEGRAM_CHANNEL_ID", "TELEGRAM_CHAT_ID", "CHAT_ID")),
        ) if not value]
    return [k for k in CREDS[platform] if not os.getenv(k, "").strip()]


def upload_to_all(lesson: dict, dry_run: bool = False) -> dict:
    funcs = load_uploaders()
    caption = long_caption(lesson)
    results = {
        "timestamp": datetime.now().isoformat(),
        "video": str(lesson["video"]),
        "category": lesson["category"],
        "phrase_count": len(lesson["phrases"]),
        "attempted": [],
        "successful": [],
        "skipped": [],
        "failed": [],
        "uploads": {},
        "dry_run": dry_run,
    }

    print("=" * 78)
    print(f"{BRAND} — MULTI-PLATFORM UPLOAD")
    print("=" * 78)
    print(f"Video   : {lesson['video']}")
    print(f"Category: {lesson['category']} ({len(lesson['phrases'])} phrases)")
    print(f"Caption : {len(caption)} characters")
    print("=" * 78)

    yt_title = yt_description = yt_tags = None
    for platform in uploaders:
        name = DISPLAY[platform]
        print(f"\n{name} ...")
        results["attempted"].append(platform)

        missing = missing_creds(platform)
        if missing:
            results["skipped"].append(platform)
            results["uploads"][platform] = {"status": "skipped", "missing": missing}
            print(f"  skipped — missing: {', '.join(missing)}")
            continue
        if platform not in funcs:
            results["skipped"].append(platform)
            results["uploads"][platform] = {"status": "skipped", "reason": "module not available"}
            print("  skipped — module not available")
            continue
        if dry_run:
            results["skipped"].append(platform)
            results["uploads"][platform] = {"status": "dry-run"}
            print("  dry run — credentials present, upload not sent")
            continue

        func = funcs[platform]
        try:
            result = None
            if platform == "facebook":
                result = func(video_path=str(lesson["video"]), description=caption,
                              title=f"{LANG_NAME}: {lesson['category']}")
            elif platform == "instagram":
                result = func(video_path=str(lesson["video"]), caption=caption, is_story=False)
            elif platform == "youtube":
                if yt_title is None:
                    from upload_to_youtube import generate_video_metadata
                    yt_title, yt_description, yt_tags = generate_video_metadata(
                        lesson["category"], len(lesson["phrases"]), lesson["phrases"]
                    )
                result = func(video_path=str(lesson["video"]), title=yt_title,
                              description=yt_description, tags=yt_tags, category_id="22")
            elif platform == "vk":
                result = func(video_path=str(lesson["video"]), description=caption,
                              title=f"{LANG_NAME}: {lesson['category']}")
            elif platform == "telegram":
                result = func(video_path=str(lesson["video"]), caption=caption)
            elif platform == "twitter":
                result = func(video_path=str(lesson["video"]), caption=short_caption(lesson))
            elif platform == "threads":
                result = func(video_path=str(lesson["video"]), text=threads_caption(lesson))
            elif platform == "tiktok":
                result = func(video_path=str(lesson["video"]), description=caption)

            if result:
                results["successful"].append(platform)
                results["uploads"][platform] = result
                print("  uploaded")
            else:
                results["failed"].append(platform)
                results["uploads"][platform] = {"status": "failed", "error": "no result"}
                print("  failed — uploader returned nothing")
        except Exception as exc:
            results["failed"].append(platform)
            results["uploads"][platform] = {"status": "failed", "error": str(exc)}
            print(f"  failed — {exc}")

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(f"  Successful: {len(results['successful'])}   Failed: {len(results['failed'])}   Skipped: {len(results['skipped'])}")
    for platform in results["successful"]:
        data = results["uploads"].get(platform, {})
        vid = data.get("video_id") or data.get("id") or "ok"
        print(f"  + {DISPLAY[platform]}: {vid}")
    for platform in results["failed"]:
        err = results["uploads"][platform].get("error", "unknown")
        print(f"  x {DISPLAY[platform]}: {err[:110]}")
    if results["skipped"]:
        print(f"  - skipped: {', '.join(DISPLAY[p] for p in results['skipped'])}")

    results_dir = ROOT / "output"
    results_dir.mkdir(exist_ok=True)
    out_file = results_dir / f"upload_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults: {out_file}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Upload the latest lesson to all platforms")
    parser.add_argument("--lesson", help="lesson folder (default: newest in output/lessons)")
    parser.add_argument("--dry-run", action="store_true", help="check credentials and captions without uploading")
    parser.add_argument("--print-captions", action="store_true", help="print every caption variant and exit")
    args = parser.parse_args()

    folder = find_latest_lesson(args.lesson)
    if not folder:
        print("No rendered lesson found. Run build.py first.")
        sys.exit(1)
    lesson = load_lesson(folder)

    if args.print_captions:
        print("\n--- LONG (Facebook / Instagram / TikTok / VK / Telegram) ---\n")
        print(long_caption(lesson))
        print("\n--- TWITTER/X ---\n")
        print(short_caption(lesson))
        print("\n--- THREADS ---\n")
        print(threads_caption(lesson))
        return

    results = upload_to_all(lesson, dry_run=args.dry_run)
    if results["successful"] or (args.dry_run and results["skipped"]):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
