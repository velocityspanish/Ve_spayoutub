"""Procedural music + SFX and final audio mix for the lesson video."""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 48000


def _midi(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def _pluck(note: int, dur: float = 0.8) -> np.ndarray:
    f = _midi(note)
    n = int(SR * dur)
    t = np.arange(n) / SR
    env = np.exp(-t * 5.0) * np.clip(t / 0.004, 0, 1)
    sig = np.sin(2 * np.pi * f * t) + 0.34 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t)
    return sig * env


def _bass(note: int, dur: float = 0.7) -> np.ndarray:
    f = _midi(note)
    n = int(SR * dur)
    t = np.arange(n) / SR
    env = np.exp(-t * 2.6) * np.clip(t / 0.012, 0, 1)
    return np.sin(2 * np.pi * f * t) * env


def _kick() -> np.ndarray:
    dur = 0.22
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = 130 * np.exp(-t * 30) + 48
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.exp(-t * 16)


def _hat(rng, dur: float = 0.05) -> np.ndarray:
    n = int(SR * dur)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = noise - np.convolve(noise, np.ones(4) / 4, mode="same")
    return noise * np.exp(-t * 90) * 0.4


def _add(out: np.ndarray, sig: np.ndarray, t0: float, gain: float = 1.0, pan: float = 0.0) -> None:
    if sig.size == 0:
        return
    i0 = int(round(t0 * SR))
    if i0 >= len(out):
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    i1 = min(len(out), i0 + len(sig))
    if i1 <= i0:
        return
    seg = np.asarray(sig[: i1 - i0], dtype=np.float64) * gain
    if out.ndim == 2:
        left = seg * (1.0 - 0.5 * max(0.0, pan))
        right = seg * (1.0 + 0.5 * min(0.0, pan))
        out[i0:i1, 0] += left
        out[i0:i1, 1] += right
    else:
        out[i0:i1] += seg


def synth_music(duration: float) -> np.ndarray:
    n = int(duration * SR)
    out = np.zeros((n, 2), dtype=np.float64)
    bpm = 92.0
    beat = 60.0 / bpm
    bar = beat * 4
    eighth = beat / 2
    progression = [
        [48, 55, 59, 64],  # Cmaj7
        [45, 52, 55, 60],  # Am7
        [41, 48, 52, 57],  # Fmaj7
        [43, 50, 53, 59],  # G7
    ]
    pattern = [0, 2, 1, 3, 2, 1, 0, 1]
    rng = np.random.default_rng(7)
    bars = int(math.ceil(duration / bar)) + 1

    for b in range(bars):
        chord = progression[b % 4]
        base = b * bar
        for k, idx in enumerate(pattern):
            t0 = base + k * eighth
            if t0 >= duration:
                continue
            note = chord[idx] + (12 if k in (2, 5) else 0)
            _add(out, _pluck(note, 0.85), t0, 0.115, pan=(-0.35 if k % 2 == 0 else 0.35))
        for k in (0, 2):
            t0 = base + k * beat
            if t0 >= duration:
                continue
            _add(out, _bass(chord[0] - 12, 0.75), t0, 0.32)
            _add(out, _kick(), t0, 0.42)
        for k in (1, 3):
            t0 = base + k * beat + eighth
            if t0 >= duration:
                continue
            _add(out, _hat(rng), t0, 0.11, pan=0.25)

    out *= 0.8
    return out.astype(np.float32)


def _sfx_pop() -> np.ndarray:
    dur = 0.18
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = 980 * np.exp(-t * 16) + 280
    phase = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(phase) * np.exp(-t * 24) + 0.35 * np.sin(2 * phase) * np.exp(-t * 40)
    return sig


def _sfx_ding() -> np.ndarray:
    dur = 0.9
    n = int(SR * dur)
    t = np.arange(n) / SR
    sig = (
        np.sin(2 * np.pi * 880 * t) * np.exp(-t * 5.5)
        + 0.55 * np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 7)
        + 0.22 * np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 9)
    )
    return sig * np.clip(t / 0.004, 0, 1)


def _sfx_chime() -> np.ndarray:
    dur = 1.5
    n = int(SR * dur)
    out = np.zeros(n)
    for i, note in enumerate([72, 76, 79, 84]):
        start = int(i * 0.1 * SR)
        f = _midi(note)
        ln = n - start
        t = np.arange(ln) / SR
        bell = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 3.6)
        out[start:] += bell * 0.45
    return out


def _sfx_success() -> np.ndarray:
    dur = 1.6
    n = int(SR * dur)
    out = np.zeros(n)
    for i, note in enumerate([72, 76, 79, 84, 88]):
        start = int(i * 0.085 * SR)
        f = _midi(note)
        ln = n - start
        t = np.arange(ln) / SR
        env = np.exp(-t * 4.2) * np.clip(t / 0.003, 0, 1)
        out[start:] += (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * env * 0.35
    return out


def _sfx_sparkle() -> np.ndarray:
    dur = 1.1
    n = int(SR * dur)
    out = np.zeros(n)
    rng = np.random.default_rng(99)
    for i in range(7):
        start = int(rng.uniform(0, 0.7) * SR)
        f = rng.uniform(1700, 3300)
        ln = min(n - start, int(0.25 * SR))
        t = np.arange(ln) / SR
        out[start:start + ln] += np.sin(2 * np.pi * f * t) * np.exp(-t * 22) * 0.22
    return out


def _sfx_whoosh() -> np.ndarray:
    dur = 0.45
    n = int(SR * dur)
    rng = np.random.default_rng(11)
    noise = rng.standard_normal(n)
    smooth = np.convolve(noise, np.ones(32) / 32, mode="same")
    band = noise - smooth
    t = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    sig = band * env * 1.5
    pan = np.linspace(-0.8, 0.8, n)
    left = sig * (1.0 - 0.5 * np.maximum(pan, 0))
    right = sig * (1.0 + 0.5 * np.minimum(pan, 0))
    return np.stack([left, right], axis=1)


def make_sfx(kind: str) -> np.ndarray:
    if kind == "pop":
        return _sfx_pop()
    if kind == "ding":
        return _sfx_ding()
    if kind == "chime":
        return _sfx_chime()
    if kind == "success":
        return _sfx_success()
    if kind == "sparkle":
        return _sfx_sparkle()
    if kind == "whoosh":
        return _sfx_whoosh()
    return _sfx_pop()


def _decode(path: Path) -> np.ndarray:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True,
    )
    if result.returncode != 0:
        return np.zeros((int(0.1 * SR), 2), dtype=np.float32)
    data = np.frombuffer(result.stdout, dtype="<f4")
    if data.size % 2:
        data = data[:-1]
    return data.reshape(-1, 2).astype(np.float32)


def _place(out: np.ndarray, sig: np.ndarray, t0: float, gain: float = 1.0) -> None:
    if sig.ndim == 1:
        _add(out, sig, t0, gain)
    else:
        i0 = int(round(t0 * SR))
        if i0 >= len(out):
            return
        i1 = min(len(out), i0 + len(sig))
        if i1 <= i0:
            return
        out[i0:i1] += sig[: i1 - i0].astype(np.float32) * gain


def _write_wav(path: Path, audio: np.ndarray) -> None:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())


def build_mix(clips: list, timeline: dict, out_path: Path) -> dict:
    duration = float(timeline["duration"])
    n = int((duration + 0.15) * SR)

    narration = np.zeros((n, 2), dtype=np.float32)
    for clip, item in zip(clips, timeline["phrases"]):
        _place(narration, _decode(clip["en_path"]), item["en_start"])
        native = _decode(clip["vi_path"])
        _place(narration, native, item["vi_start"])
        if item.get("vi_repeat_start"):
            _place(narration, native, item["vi_repeat_start"])

    peak = float(np.max(np.abs(narration))) or 1.0
    narration *= 0.92 / peak

    music = synth_music(duration + 0.15)
    if len(music) < n:
        music = np.pad(music, ((0, n - len(music)), (0, 0)))
    music = music[:n]

    env = np.max(np.abs(narration), axis=1)
    smooth = int(0.18 * SR)
    env = np.convolve(env, np.ones(smooth) / smooth, mode="same")
    env = env / (float(env.max()) + 1e-9)
    duck = 1.0 - 0.62 * np.clip(env * 1.35, 0, 1)
    music = music * duck[:, None] * 0.30

    sfx = np.zeros((n, 2), dtype=np.float32)
    for event in timeline.get("sfx", []):
        _place(sfx, make_sfx(event["kind"]), event["t"], event.get("gain", 0.5))

    master = narration + music.astype(np.float32) + sfx

    fade_in = int(0.25 * SR)
    master[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    fade_out = int(1.1 * SR)
    master[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]

    peak = float(np.max(np.abs(master)))
    if peak > 0.95:
        master *= 0.95 / peak
    master = np.tanh(master * 1.08) / np.tanh(1.08)

    _write_wav(out_path, master)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"[audio] Mix: {out_path.name} ({duration:.1f}s, {size_mb:.1f} MB)")
    return {"duration": duration, "path": str(out_path), "peak": round(peak, 3)}
