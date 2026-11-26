"""AI phrase generation with permanent no-repeat history."""

from __future__ import annotations

import json
import random
import re
import time
from datetime import datetime

import requests

import config
from config import CATEGORIES, CATEGORIES_NATIVE, HISTORY_DIR, MAX_RECENT_CATEGORIES

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"

PHRASE_KEY = config.LANGUAGE["history_key"]
LANGUAGE_NAME = config.LANGUAGE["name"]
NATIVE_NAME = config.LANGUAGE["native_name"]

_JP_RANGES = (
    ("\u3040", "\u30ff"),  # hiragana + katakana
    ("\u3400", "\u4dbf"),  # CJK extension A
    ("\u4e00", "\u9fff"),  # CJK unified ideographs
)
_VI_CHARS = set("ăâđêôơưĂÂĐÊÔƠƯáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")


def _has_japanese(text: str) -> bool:
    return any(start <= ch <= end for ch in text for start, end in _JP_RANGES)


def _valid_native(text: str) -> bool:
    if config.LANGUAGE.get("code") != "ja":
        return True
    if not _has_japanese(text):
        return False
    return not any(ch in _VI_CHARS for ch in text)


def _clean_translit(text: str) -> str:
    """Tidy AI romaji: capitalisation, punctuation spacing, split te-forms."""
    text = text.strip().strip("[]")
    if not text:
        return text
    text = re.sub(r"\b(\w+)tsu te\b", r"\1tte", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\w*[aeiou]) i\b", r"\1i", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    text = re.sub(
        r"(^|[.!?]\s+)([a-z])",
        lambda match: match.group(1) + match.group(2).upper(),
        text,
    )
    return text

# ==== FALLBACK PHRASES START ====
FALLBACK_PHRASES = [
    {"english": 'Hello, nice to meet you.', "native": "Hola, encantado de conocerte.", "transliteration": ""},
    {"english": 'Thank you very much.', "native": "Muchas gracias.", "transliteration": ""},
    {"english": 'Good morning, have a great day.', "native": "Buenos días, que tengas un gran día.", "transliteration": ""},
    {"english": 'I love learning new languages.', "native": "Me encanta aprender nuevos idiomas.", "transliteration": ""},
    {"english": 'Never give up on your dreams.', "native": "Nunca renuncies a tus sueños.", "transliteration": ""},
    {"english": 'Every day is a fresh start.', "native": "Cada día es un nuevo comienzo.", "transliteration": ""},
    {"english": 'Believe in yourself always.', "native": "Cree siempre en ti mismo.", "transliteration": ""},
    {"english": 'Small steps lead to big changes.', "native": "Los pequeños pasos llevan a grandes cambios.", "transliteration": ""},
    {"english": 'You are stronger than you think.', "native": "Eres más fuerte de lo que crees.", "transliteration": ""},
    {"english": 'Happiness is a choice, choose it.', "native": "La felicidad es una elección, elígela.", "transliteration": ""},
    {"english": 'What time is it please.', "native": "¿Qué hora es, por favor?", "transliteration": ""},
    {"english": 'Where is the train station.', "native": "¿Dónde está la estación de tren?", "transliteration": ""},
    {"english": 'How much does this cost.', "native": "¿Cuánto cuesta esto?", "transliteration": ""},
    {"english": 'Can you help me please.', "native": "¿Puedes ayudarme, por favor?", "transliteration": ""},
    {"english": 'I would like a coffee please.', "native": "Quisiera un café, por favor.", "transliteration": ""},
    {"english": 'The food is delicious today.', "native": "La comida está deliciosa hoy.", "transliteration": ""},
    {"english": 'Have a wonderful weekend.', "native": "Que tengas un buen fin de semana.", "transliteration": ""},
    {"english": 'Take care of yourself.', "native": "Cuídate.", "transliteration": ""},
    {"english": 'See you tomorrow my friend.', "native": "Hasta mañana, amigo.", "transliteration": ""},
    {"english": 'The weather is beautiful outside.', "native": "Hace un tiempo precioso fuera.", "transliteration": ""},
    {"english": 'I am very happy today.', "native": "Estoy muy feliz hoy.", "transliteration": ""},
    {"english": 'Learning a language opens new doors.', "native": "Aprender un idioma abre nuevas puertas.", "transliteration": ""},
    {"english": 'Keep practicing every single day.', "native": "Sigue practicando cada día.", "transliteration": ""},
    {"english": 'You can achieve anything you want.', "native": "Puedes lograr todo lo que quieras.", "transliteration": ""},
    {"english": 'Rest when you are tired.', "native": "Descansa cuando estés cansado.", "transliteration": ""},
]
# ==== FALLBACK PHRASES END ====


def _load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_phrase_history():
    data = _load_json(PHRASE_HISTORY_FILE, {"phrases": [], "last_updated": None})
    data.setdefault("phrases", [])
    return data


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    _save_json(PHRASE_HISTORY_FILE, data)


def is_phrase_used(english):
    english_lower = english.lower().strip()
    for p in load_phrase_history()["phrases"]:
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def _history_native(p):
    for key in (PHRASE_KEY, "vietnamese", "native", "translation", "target"):
        value = p.get(key)
        if value:
            return str(value)
    return ""


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            PHRASE_KEY: phrase["native"],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat(),
        })
    save_phrase_history(history)
    print(f"[content] Saved {len(phrases)} phrases (history total: {len(history['phrases'])})")


def get_available_category():
    data = _load_json(RECENT_CATEGORIES_FILE, {"recent_categories": [], "last_updated": None})
    recent = data.get("recent_categories", [])
    available = [c for c in CATEGORIES if c not in recent]
    if not available:
        recent = recent[-5:]
        available = [c for c in CATEGORIES if c not in recent]
        print("[rotation] Reset recent categories")
    selected = random.choice(available)
    recent.append(selected)
    data["recent_categories"] = recent[-MAX_RECENT_CATEGORIES:]
    data["last_updated"] = datetime.now().isoformat()
    _save_json(RECENT_CATEGORIES_FILE, data)
    print(f"[rotation] Category: {selected} ({len(available)} available)")
    return selected


def _normalize_phrase(item):
    if not isinstance(item, dict):
        return None
    english = str(item.get("english", "")).strip()
    native = str(
        item.get(PHRASE_KEY)
        or item.get("native")
        or item.get("vietnamese")
        or item.get("translation")
        or ""
    ).strip()
    translit = str(item.get("transliteration") or item.get("romanization") or item.get("romaji") or "").strip()
    if not english or not native:
        return None
    if len(english.split()) > 16:
        return None
    if "/" in native or "|" in native:
        native = native.split("/")[0].split("|")[0].strip()
    if not _valid_native(native):
        return None
    if config.LANGUAGE.get("code") == "ja" and not translit:
        return None
    item_tiles = item.get("tiles")
    out = {
        "english": english.replace("  ", " ").strip(),
        "native": native.strip(),
        "transliteration": _clean_translit(translit),
    }
    if isinstance(item_tiles, list) and item_tiles and all(isinstance(t, str) and t.strip() for t in item_tiles):
        out["tiles"] = [t.strip() for t in item_tiles]
    return out


def _history_keys(history):
    used_en = set()
    used_nat = set()
    for p in history.get("phrases", []):
        en = str(p.get("english", "")).lower().strip()
        nat = _history_native(p).lower().strip()
        if en:
            used_en.add(en)
        if nat:
            used_nat.add(nat)
    return used_en, used_nat


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE[category_english]
    history = load_phrase_history()
    used_en, used_nat = _history_keys(history)
    recent_english = [
        p["english"] for p in history["phrases"] if p.get("category") == category_english
    ][-30:]

    models = [config.AI_MODEL]
    if "gemini-fast" not in models:
        models.append("gemini-fast")

    if config.POLLINATIONS_API_KEY:
        for attempt in range(5):
            model = models[0] if attempt < 3 else models[-1]
            try:
                phrases = _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model)
                unique = []
                for item in phrases:
                    p = _normalize_phrase(item)
                    if not p:
                        continue
                    key_en = p["english"].lower().strip()
                    key_nat = p["native"].lower().strip()
                    if key_en in used_en or key_nat in used_nat:
                        continue
                    if any(key_en == u["english"].lower().strip() for u in unique):
                        continue
                    used_en.add(key_en)
                    used_nat.add(key_nat)
                    unique.append(p)
                    if len(unique) >= num_phrases:
                        break
                if len(unique) >= num_phrases:
                    add_phrases_to_history(unique[:num_phrases], category_english)
                    return unique[:num_phrases]
                print(f"[content] Attempt {attempt + 1}: only {len(unique)} fresh phrases (need {num_phrases})")
            except Exception as exc:  # noqa: BLE001 - network boundary
                print(f"[content] Attempt {attempt + 1} failed ({model}): {exc}")
            time.sleep(1.5 * (attempt + 1))
    else:
        print("[content] No POLLINATIONS_API_KEY, using fallback phrases")

    fresh_fallback = []
    for p in FALLBACK_PHRASES:
        if p["english"].lower().strip() in used_en or p["native"].lower().strip() in used_nat:
            continue
        fresh_fallback.append(p)
    if not fresh_fallback:
        raise RuntimeError("Phrase API unavailable and no unused fallback phrases left; refusing to reuse phrases")
    chosen = fresh_fallback[:num_phrases]
    if len(chosen) < num_phrases:
        print(f"[content] Only {len(chosen)} fresh fallback phrases; building a shorter lesson")
    add_phrases_to_history(chosen, category_english)
    return chosen


def _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model=None):
    avoid = ""
    if recent_english:
        avoid = "\nDo NOT reuse any of these phrases:\n" + "\n".join(f"- {p}" for p in recent_english)

    prompt = f"""Create {num_phrases * 6} unique {category_english} phrases for English speakers learning {LANGUAGE_NAME}.
{avoid}

Rules:
1. Keep every phrase short and natural (4-11 words in English).
2. Use natural commas for TTS breathing pauses.
3. Each phrase must be speakable in 2-4 seconds.
4. Write natural {LANGUAGE_NAME} in {NATIVE_NAME}. One translation only, no slashes.
5. The native field must contain the target language only. Never return English, Japanese, Chinese, Korean, Vietnamese, or another language.
6. Transliteration is a friendly pronunciation guide for English speakers (not IPA).
7. Vary the sentence patterns and emotions. No duplicates.
8. Phrases must feel like real everyday language, not textbook filler.
9. The English must be idiomatic and complete. Avoid filler endings and literal word-for-word translations.

Return ONLY a JSON array:
[{{"english": "...", "native": "...", "transliteration": "..."}}]"""

    response = requests.post(
        "https://gen.pollinations.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.POLLINATIONS_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model or config.AI_MODEL,
            "messages": [
                {"role": "system", "content": f"You are a {LANGUAGE_NAME} teacher creating short, natural, varied bilingual phrases. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": min(0.95 + attempt * 0.02, 1.0),
        },
        timeout=90,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()

    if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0].strip()

    start = content.find("[")
    end = content.rfind("]")
    if start >= 0 and end > start:
        content = content[start:end + 1]

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("AI did not return a JSON array")
    return data
