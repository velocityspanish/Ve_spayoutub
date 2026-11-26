"""Edge TTS synthesis with word-boundary timings for karaoke highlighting."""

from __future__ import annotations

import asyncio
import re
import subprocess
import unicodedata
from pathlib import Path

import edge_tts
import numpy as np

import config

SR = 48000
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_JP_KKS = None
_JP_JANOME = None
_JP_PUNCT_POS = "記号"
_JP_PREFIX_POS = "接頭詞"
_JP_NOUN_POS = "名詞"
_JP_VERB_POS = "動詞"
_JP_ADJ_POS = "形容詞"
_JP_AUX_POS = "助動詞"
_JP_PARTICLE_POS = "助詞"
_JP_DEMONSTRATIVE_POS = "連体詞"
_JP_SURU = ("し", "する", "され", "さ")
_JP_ADVERB_MERGE = ("よろしく", "どうぞ")
_JP_SMALL_KANA = "ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮ"
_JP_NOUN_NO_MERGE = {
    "今日", "明日", "昨日", "今年", "来年", "去年", "今週", "来週", "先週",
    "今月", "来月", "先月", "毎日", "毎週", "毎朝", "毎晩", "今", "私", "僕",
    "君", "人", "物", "事", "時", "前", "後", "上", "下", "中", "外", "間",
}
_JP_PARTICLE_SUFFIXES = (
    "から", "まで", "より", "だけ", "しか", "でも", "など", "くらい", "ほど",
    "ばかり", "ながら", "ので", "のに", "けど", "けれど", "し", "て", "は",
    "が", "を", "に", "で", "と", "も", "の", "へ", "や", "か", "ね", "よ",
    "な", "さ",
)


def _is_punct(token: str) -> bool:
    return bool(_PUNCT.fullmatch(token))


def _is_kanji_or_katakana(ch: str) -> bool:
    return (
        "\u3400" <= ch <= "\u4dbf"
        or "\u4e00" <= ch <= "\u9fff"
        or "\u30a0" <= ch <= "\u30ff"
    )


def _ends_with_particle(text: str) -> bool:
    return text.endswith(_JP_PARTICLE_SUFFIXES)


def _jp_tiles_pykakasi(text: str) -> list:
    """Fallback segmentation when Janome is unavailable."""
    global _JP_KKS
    if _JP_KKS is None:
        try:
            from pykakasi import kakasi
        except Exception:
            return []
        _JP_KKS = kakasi()
    tokens = [t["orig"] for t in _JP_KKS.convert(text) if t["orig"].strip()]
    if not tokens:
        return [text.strip()] if text.strip() else []

    words = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if _is_punct(tok):
            if words:
                words[-1] += tok
            else:
                words.append(tok)
            i += 1
            continue
        if tok in ("お", "ご") and i + 1 < len(tokens) and not _is_punct(tokens[i + 1]):
            words.append(tok + tokens[i + 1])
            i += 2
            continue
        if words and tok.endswith(("ましょう", "ください", "します", "いたします")):
            words[-1] += tok
            i += 1
            continue
        words.append(tok)
        i += 1
    return words


def _jp_tiles(text: str) -> list:
    """Segment Japanese into readable word/phrase tiles with Janome POS hints.

    Particles and auxiliaries attach to the word they belong to, so a phrase
    never renders as a row of single-character boxes. If Janome is missing we
    fall back to pykakasi; if both are missing the scene uses one phrase tile.
    """
    global _JP_JANOME
    if _JP_JANOME is None:
        try:
            from janome.tokenizer import Tokenizer

            _JP_JANOME = Tokenizer()
        except Exception:
            return _jp_tiles_pykakasi(text)

    try:
        raw = [
            (token.surface, token.part_of_speech.split(",")[0])
            for token in _JP_JANOME.tokenize(text)
            if token.surface.strip()
        ]
    except Exception:
        return _jp_tiles_pykakasi(text)
    if not raw:
        return [text.strip()] if text.strip() else []

    # Pass 1: attach punctuation, and bind prefixes to the following word.
    chunks = []
    i = 0
    while i < len(raw):
        surface, pos = raw[i]
        if pos == _JP_PUNCT_POS:
            if chunks:
                chunks[-1]["text"] += surface
            else:
                chunks.append({"text": surface, "pos": pos})
            i += 1
            continue
        if pos == _JP_PREFIX_POS and i + 1 < len(raw) and raw[i + 1][1] != _JP_PUNCT_POS:
            chunks.append({"text": surface + raw[i + 1][0], "pos": raw[i + 1][1]})
            i += 2
            continue
        chunks.append({"text": surface, "pos": pos})
        i += 1

    # Pass 2: particles, auxiliaries, te-form verbs and suru-verbs stay together.
    merged = []
    for chunk in chunks:
        surface, pos = chunk["text"], chunk["pos"]
        if merged:
            prev = merged[-1]
            merge = pos in (_JP_PARTICLE_POS, _JP_AUX_POS)
            if pos == _JP_VERB_POS and prev["text"].endswith(("て", "で")):
                merge = True
            if prev["text"].endswith("っ") and not _is_punct(surface):
                merge = True
            if pos == _JP_VERB_POS and surface in _JP_SURU and prev["pos"] == _JP_NOUN_POS:
                merge = True
            if pos == _JP_NOUN_POS and prev["pos"] == _JP_DEMONSTRATIVE_POS:
                merge = True
            if pos == _JP_NOUN_POS and prev["pos"] == _JP_NOUN_POS:
                if (
                    prev["text"]
                    and surface
                    and _is_kanji_or_katakana(surface[0])
                    and prev["text"] not in _JP_NOUN_NO_MERGE
                    and not _ends_with_particle(prev["text"])
                ):
                    merge = True
            if prev["text"] in _JP_ADVERB_MERGE:
                merge = True
            if surface.startswith("ござ") and prev["text"] in ("ありがとう", "おめでとう"):
                merge = True
            if prev["text"].endswith("かも") and surface.startswith("しれ"):
                merge = True
            if prev["text"].endswith("なければ") and surface.startswith("なり"):
                merge = True
            if prev["text"].endswith("お待ち") and surface.startswith("ください"):
                merge = True
            if merge and prev["text"] and not _is_punct(prev["text"][-1]):
                prev["text"] += surface
                if pos in (_JP_NOUN_POS, _JP_VERB_POS, _JP_ADJ_POS):
                    prev["pos"] = pos
                continue
        merged.append({"text": surface, "pos": pos})

    # Pass 3: a trailing の binds to the noun after it.
    bound = []
    i = 0
    while i < len(merged):
        chunk = merged[i]
        if chunk["text"].endswith("の") and i + 1 < len(merged) and merged[i + 1]["pos"] == _JP_NOUN_POS:
            bound.append({"text": chunk["text"] + merged[i + 1]["text"], "pos": _JP_NOUN_POS})
            i += 2
            continue
        bound.append(chunk)
        i += 1

    # Pass 4: never leave a one-character tile if it can join a neighbour.
    out = []
    i = 0
    while i < len(bound):
        surface = bound[i]["text"]
        if len(surface) == 1 and not _is_punct(surface):
            if i + 1 < len(bound):
                out.append(surface + bound[i + 1]["text"])
                i += 2
                continue
            if out and not _is_punct(out[-1][-1]):
                out[-1] += surface
                i += 1
                continue
        out.append(surface)
        i += 1

    # Pass 5: repair rare tokenizer splits inside a single word.
    repaired = []
    for tile in out:
        if repaired and tile and (tile[0] in _JP_SMALL_KANA or tile[0] == "ー"):
            repaired[-1] += tile
            continue
        if repaired and repaired[-1].endswith("っ") and not _is_punct(tile[0]):
            repaired[-1] += tile
            continue
        repaired.append(tile)
    return [tile for tile in repaired if tile.strip()]


def _norm(text: str) -> str:
    return _PUNCT.sub("", text).strip().lower()


def _audio_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def _audio_peak(path: Path) -> float:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout:
        return 0.0
    data = np.frombuffer(result.stdout, dtype="<f4")
    return float(np.max(np.abs(data))) if data.size else 0.0


async def _synth_once(text: str, voice: str, out_path: Path, rate: str, pitch: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    boundaries = []
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            boundaries.append({
                "text": chunk["text"],
                "start": chunk["offset"] / 1e7,
                "duration": chunk["duration"] / 1e7,
            })
    if len(audio) < 500:
        raise RuntimeError("TTS returned empty audio")
    out_path.write_bytes(bytes(audio))
    return boundaries


async def _try_voice(text: str, voice: str, out_path: Path, rate: str, pitch: str, semaphore, attempts: int):
    last_error = None
    for attempt in range(attempts):
        try:
            if semaphore:
                async with semaphore:
                    boundaries = await _synth_once(text, voice, out_path, rate, pitch)
            else:
                boundaries = await _synth_once(text, voice, out_path, rate, pitch)
            duration = _audio_duration(out_path)
            peak = _audio_peak(out_path)
            if duration > 0.2 and peak > 0.01:
                return boundaries, duration
            raise RuntimeError(f"invalid audio (duration {duration:.2f}s, peak {peak:.3f})")
        except Exception as exc:  # noqa: BLE001 - network boundary
            last_error = exc
            print(f"  [tts] retry {attempt + 1}/{attempts} for {voice}: {exc}")
            await asyncio.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"voice {voice} failed after {attempts} attempts: {last_error}")


async def _synth_with_retry(text: str, voices: list[str], out_path: Path, rate: str, pitch: str, semaphore=None):
    combos = [(voice, rate, pitch) for voice in dict.fromkeys(voices)]
    primary = voices[0]
    if rate not in ("+0%", "0%") or pitch not in ("+0Hz", "0Hz"):
        combos.append((primary, "+0%", "+0Hz"))
    last_error = None
    for voice, voice_rate, voice_pitch in combos:
        try:
            return await _try_voice(text, voice, out_path, voice_rate, voice_pitch, semaphore, attempts=3)
        except Exception as exc:  # noqa: BLE001 - try the next voice/setting
            last_error = exc
            print(f"  [tts] {voice} ({voice_rate}, {voice_pitch}) unavailable: {exc}")
    raise RuntimeError(f"All voices failed for text: {text[:60]!r} ({last_error})")


def map_word_timings(text: str, boundaries: list, duration: float, split_chars: bool = False, words: list | None = None) -> list:
    if words is None:
        if split_chars:
            words = []
            for ch in text:
                if ch.isspace():
                    continue
                if unicodedata.category(ch).startswith(("P", "S")) and words:
                    words[-1] += ch
                else:
                    words.append(ch)
        else:
            words = text.split()
    else:
        words = list(words)
    if not words:
        return []

    clean = [b for b in boundaries if _norm(b["text"])]
    if len(clean) == len(words) and all(_norm(b["text"]) == _norm(w) for b, w in zip(clean, words)):
        return [
            {
                "start": round(max(0.0, b["start"]), 3),
                "end": round(min(duration, b["start"] + b["duration"]), 3),
                "text": w,
            }
            for b, w in zip(clean, words)
        ]

    speech_start = clean[0]["start"] if clean else 0.06
    speech_end = max((b["start"] + b["duration"]) for b in clean) if clean else duration * 0.92
    speech_end = min(max(speech_start + 0.2, speech_end), duration)
    span = speech_end - speech_start
    weights = [max(1, len(w)) for w in words]
    total = sum(weights)
    out = []
    cursor = speech_start
    for w, weight in zip(words, weights):
        share = (weight / total) * span
        out.append({"start": round(cursor, 3), "end": round(min(speech_end, cursor + share), 3), "text": w})
        cursor += share
    return out


def _gtts_sync(text: str, out_path: Path, lang_code: str):
    from gtts import gTTS
    gTTS(text=text, lang=lang_code).save(str(out_path))


def _mms_sync(text: str, out_path: Path, lang_code: str):
    from engine.mms_tts import generate_mms_audio
    generate_mms_audio(text, out_path, lang_code)


async def _synth_native(text: str, out_path: Path, semaphore):
    lang = config.LANGUAGE
    engine = lang.get("native_engine", "edge")
    lang_code = lang.get("native_lang_code", lang["code"])

    if engine == "edge":
        return await _synth_with_retry(
            text,
            [lang["native_voice"], lang.get("native_fallback_voice", "")],
            out_path, lang["native_rate"], lang["native_pitch"], semaphore,
        )

    last_error = None
    providers = [engine] + [p for p in ("mms", "gtts") if p != engine]
    for provider in providers:
        for attempt in range(2):
            try:
                fn = _gtts_sync if provider == "gtts" else _mms_sync
                await asyncio.to_thread(fn, text, out_path, lang_code)
                duration = _audio_duration(out_path)
                peak = _audio_peak(out_path)
                if duration > 0.2 and peak > 0.01:
                    return [], duration
                raise RuntimeError(f"invalid audio (duration {duration:.2f}s, peak {peak:.3f})")
            except Exception as exc:  # noqa: BLE001 - provider boundary
                last_error = exc
                print(f"  [tts] {provider} attempt {attempt + 1} failed: {exc}")
                await asyncio.sleep(1.5 * (attempt + 1))

    if lang.get("native_voice"):
        try:
            return await _synth_with_retry(
                text,
                [lang["native_voice"], lang.get("native_fallback_voice", "")],
                out_path, lang["native_rate"], lang["native_pitch"], semaphore,
            )
        except Exception as exc:  # noqa: BLE001 - last resort
            last_error = exc
    raise RuntimeError(f"All native TTS providers failed for text: {text[:60]!r} ({last_error})")


async def _synth_phrase(index: int, phrase: dict, audio_dir: Path, semaphore):
    lang = config.LANGUAGE
    en_path = audio_dir / f"en_{index}.mp3"
    vi_path = audio_dir / f"vi_{index}.mp3"

    # Sequential per phrase: Edge TTS throttles when many websockets open at once.
    en_bounds, en_dur = await _synth_with_retry(
        phrase["english"],
        [lang["english_voice"], lang.get("english_fallback_voice", "en-US-GuyNeural")],
        en_path, lang["english_rate"], lang["english_pitch"], semaphore,
    )

    vi_bounds, vi_dur = await _synth_native(phrase["native"], vi_path, semaphore)
    tiles = phrase.get("tiles")
    if not tiles and lang["code"] == "ja":
        tiles = _jp_tiles(phrase["native"])

    return {
        "index": index,
        "english": phrase["english"],
        "native": phrase["native"],
        "transliteration": phrase.get("transliteration", ""),
        "en_path": en_path,
        "vi_path": vi_path,
        "en_duration": en_dur,
        "vi_duration": vi_dur,
        "en_words": map_word_timings(phrase["english"], en_bounds, en_dur),
        "vi_words": map_word_timings(phrase["native"], vi_bounds, vi_dur,
                                     split_chars=bool(lang.get("char_tiles")),
                                     words=tiles),
    }


def synthesize_all(phrases: list, audio_dir: Path) -> list:
    audio_dir.mkdir(parents=True, exist_ok=True)
    lang = config.LANGUAGE
    print(f"[tts] Synthesizing {len(phrases)} phrases with {lang['english_voice']} + {lang['native_voice']}")

    async def run():
        semaphore = asyncio.Semaphore(2)
        tasks = [_synth_phrase(i, p, audio_dir, semaphore) for i, p in enumerate(phrases)]
        return await asyncio.gather(*tasks)

    results = asyncio.run(run())
    for r in results:
        print(f"  {r['index'] + 1}. EN {r['en_duration']:.2f}s | NATIVE {r['vi_duration']:.2f}s | {r['english']}")
    return results
