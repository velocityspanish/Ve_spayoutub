"""Pick a phrase-reveal frame from a rendered lesson for use as a video cover."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

COVER_WINDOW = (20.0, 40.0)
COVER_TARGET = 30.0


def _timeline_path(video_path: Path) -> Path:
    return video_path.parent / "timeline.json"


def load_timeline(video_path) -> dict:
    path = _timeline_path(Path(video_path))
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def pick_cover_time(video_path) -> float:
    """Moment where one phrase is shown in full: English, native tiles and romanization."""
    tl = load_timeline(video_path)
    duration = float(tl.get("duration") or 0.0)

    candidates = []
    for phrase in tl.get("phrases", []):
        try:
            if phrase.get("vi_repeat_end") is not None:
                # tail hold after the repeat: every element is fully visible, no highlight
                when = float(phrase["vi_repeat_end"]) + 0.55
            else:
                when = float(phrase.get("nat_reveal", 0.0)) + 1.1
        except (TypeError, ValueError):
            continue
        candidates.append(when)

    if candidates:
        low, high = COVER_WINDOW
        in_window = [t for t in candidates if low <= t <= high]
        pool = in_window or candidates
        best = min(pool, key=lambda t: abs(t - COVER_TARGET))
        if duration:
            best = min(best, max(1.0, duration - 1.5))
        return round(max(0.5, best), 3)

    if duration:
        return round(max(5.0, min(duration * 0.45, duration - 1.5)), 3)
    return 0.0


def extract_cover_frame(video_path, out_path=None) -> Path | None:
    """Write a JPEG frame at the chosen phrase moment; returns None when unavailable."""
    video = Path(video_path)
    if not video.exists():
        return None
    when = pick_cover_time(video)
    target = Path(out_path) if out_path else video.parent / "cover.jpg"
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{when:.3f}", "-i", str(video),
             "-frames:v", "1", "-q:v", "2", str(target)],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as exc:
        print(f"[cover] Frame extraction failed: {exc}")
        return None
    if result.returncode != 0 or not target.exists() or target.stat().st_size == 0:
        print(f"[cover] ffmpeg could not grab frame at {when:.2f}s: {result.stderr[:200]}")
        return None
    print(f"[cover] Captured phrase frame at {when:.2f}s -> {target.name}")
    return target


def thumb_offset_ms(video_path) -> int | None:
    """Offset for Instagram's thumb_offset parameter (milliseconds)."""
    tl = load_timeline(video_path)
    if not tl:
        return None
    when = pick_cover_time(video_path)
    duration = float(tl.get("duration") or 0.0)
    limit = (duration - 0.5) * 1000 if duration else when * 1000
    return int(max(0, min(when * 1000, limit)))
