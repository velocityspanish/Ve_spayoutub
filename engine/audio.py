"""Procedural music + SFX and final audio mix for the lesson video."""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np

import config

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


def synth_music(duration: float, style: str = "bright") -> np.ndarray:
    n = int(duration * SR)
    out = np.zeros((n, 2), dtype=np.float64)
    if style == "chill":
        bpm = 88.0
        progression = [
            [48, 55, 59, 64],  # Cmaj7
            [45, 52, 55, 60],  # Am7
            [41, 48, 52, 57],  # Fmaj7
            [43, 50, 53, 59],  # G7
        ]
        pluck_gain = 0.105
        kick_gain = 0.34
    else:
        bpm = 104.0
        progression = [
            [48, 55, 59, 62],  # Cmaj9 colour
            [43, 50, 55, 59],  # G7
            [45, 52, 57, 60],  # Am7
            [41, 48, 53, 57],  # Fmaj7
        ]
        pluck_gain = 0.125
        kick_gain = 0.42
    beat = 60.0 / bpm
    bar = beat * 4
    eighth = beat / 2
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
            _add(out, _pluck(note, 0.85), t0, pluck_gain, pan=(-0.35 if k % 2 == 0 else 0.35))
        for k in (0, 2):
            t0 = base + k * beat
            if t0 >= duration:
                continue
            _add(out, _bass(chord[0] - 12, 0.75), t0, 0.30)
            _add(out, _kick(), t0, kick_gain)
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
    f = 700 * np.exp(-t * 14) + 240
    phase = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(phase) * np.exp(-t * 22) + 0.18 * np.sin(2 * phase) * np.exp(-t * 34)
    return sig * 0.85


def _sfx_ding() -> np.ndarray:
    """Soft marimba tap. Replaces the old 880/1320/1760 Hz bell.

    Low notes, slow mallet attack, no piercing harmonics. This is the sound
    that lands at the end of every phrase, so it has to be gentle on earphones.
    """
    dur = 0.55
    n = int(SR * dur)
    t = np.arange(n) / SR
    sig = (
        0.55 * np.sin(2 * np.pi * 392.00 * t)   # G4
        + 0.30 * np.sin(2 * np.pi * 523.25 * t)  # C5
        + 0.12 * np.sin(2 * np.pi * 659.25 * t)  # E5
    )
    env = np.exp(-t * 7.5) * (1 - np.exp(-t * 90))
    return sig * env * 0.52


def _sfx_chime() -> np.ndarray:
    dur = 1.35
    n = int(SR * dur)
    out = np.zeros(n)
    for i, note in enumerate([60, 64, 67, 72]):  # C4 E4 G4 C5
        start = int(i * 0.11 * SR)
        f = _midi(note)
        ln = n - start
        t = np.arange(ln) / SR
        bell = (np.sin(2 * np.pi * f * t) + 0.22 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 3.8)
        out[start:] += bell * 0.32
    return out


def _sfx_success() -> np.ndarray:
    dur = 1.5
    n = int(SR * dur)
    out = np.zeros(n)
    for i, note in enumerate([60, 64, 67, 72, 76]):  # C4 E4 G4 C5 E5
        start = int(i * 0.10 * SR)
        f = _midi(note)
        ln = n - start
        t = np.arange(ln) / SR
        env = np.exp(-t * 4.6) * (1 - np.exp(-t * 60))
        out[start:] += (np.sin(2 * np.pi * f * t) + 0.18 * np.sin(4 * np.pi * f * t)) * env * 0.26
    return out


def _sfx_sparkle() -> np.ndarray:
    dur = 1.0
    n = int(SR * dur)
    out = np.zeros(n)
    rng = np.random.default_rng(99)
    for i in range(7):
        start = int(rng.uniform(0, 0.65) * SR)
        f = rng.uniform(1300, 2400)
        ln = min(n - start, int(0.25 * SR))
        t = np.arange(ln) / SR
        out[start:start + ln] += np.sin(2 * np.pi * f * t) * np.exp(-t * 24) * 0.11
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


def _soften_sfx(sfx: np.ndarray, cutoff: float) -> np.ndarray:
    """Zero-phase gentle low-pass so the SFX bus is earphone-friendly."""
    n = sfx.shape[0]
    if n == 0:
        return sfx
    spec = np.fft.rfft(sfx, axis=0)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    gain = 1.0 / (1.0 + np.power(freqs / max(cutoff, 100.0), 4.0))
    spec *= gain[:, None]
    return np.fft.irfft(spec, n=n, axis=0).astype(np.float32)


def _normalize_loudness(path: Path, target_lufs: float = -13.0, true_peak: float = -1.5) -> None:
    """Normalize the finished mix so the validator gate is stable run-to-run."""
    tmp = path.with_name(path.stem + "_norm.wav")
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error", "-i", str(path),
                "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=11",
                "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp),
            ],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode == 0 and tmp.exists() and tmp.stat().st_size > 1000:
            tmp.replace(path)
            print(f"[audio] Loudness normalized to {target_lufs:.1f} LUFS / {true_peak:.1f} dBTP")
        else:
            print(f"[audio] Loudness normalization skipped: {result.stderr[:160]}")
    except Exception as exc:  # noqa: BLE001 - keep the original mix if ffmpeg fails
        print(f"[audio] Loudness normalization failed: {exc}")
    finally:
        if tmp.exists():
            tmp.unlink()


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

    music = synth_music(duration + 0.15, timeline.get("music", "bright"))
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
    sfx = _soften_sfx(sfx, config.SFX_LOWPASS_HZ) * config.SFX_MASTER

    master = narration + music.astype(np.float32) + sfx

    fade_in = int(0.25 * SR)
    master[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    fade_out = int(1.1 * SR)
    master[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]

    peak = float(np.max(np.abs(master)))
    if peak > 0.95:
        master *= 0.95 / peak
    master = np.tanh(master * 1.08) / np.tanh(1.08)
    master *= config.MASTER_GAIN

    _write_wav(out_path, master)
    _normalize_loudness(out_path)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"[audio] Mix: {out_path.name} ({duration:.1f}s, {size_mb:.1f} MB)")
    return {"duration": duration, "path": str(out_path), "peak": round(peak, 3)}
