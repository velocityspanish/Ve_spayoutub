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
# Kept fresh and Japanese-only. The live bot normally uses the AI generator;
# this list is the offline safety net when the API is unavailable.
FALLBACK_PHRASES = [
    {"english": "I am a little tired today.", "native": "今日は少し疲れています。", "transliteration": "Kyō wa sukoshi tsukarete imasu."},
    {"english": "Please speak a little slower.", "native": "もう少しゆっくり話してください。", "transliteration": "Mō sukoshi yukkuri hanashite kudasai."},
    {"english": "I forgot my umbrella.", "native": "傘を忘れました。", "transliteration": "Kasa o wasuremashita."},
    {"english": "The train is late today.", "native": "今日は電車が遅れています。", "transliteration": "Kyō wa densha ga okurete imasu."},
    {"english": "This street is very quiet.", "native": "この通りはとても静かです。", "transliteration": "Kono tōri wa totemo shizuka desu."},
    {"english": "Let's take a short break.", "native": "少し休みましょう。", "transliteration": "Sukoshi yasumimashō."},
    {"english": "I like this song a lot.", "native": "この歌がとても好きです。", "transliteration": "Kono uta ga totemo suki desu."},
    {"english": "Please turn down the volume.", "native": "音量を下げてください。", "transliteration": "Onryō o sagete kudasai."},
    {"english": "I will call you tomorrow.", "native": "明日電話します。", "transliteration": "Ashita denwa shimasu."},
    {"english": "It might rain this afternoon.", "native": "午後は雨が降るかもしれません。", "transliteration": "Gogo wa ame ga furu kamoshiremasen."},
    {"english": "The food here is delicious.", "native": "ここの料理はおいしいです。", "transliteration": "Koko no ryōri wa oishii desu."},
    {"english": "I need to buy a ticket.", "native": "切符を買わなければなりません。", "transliteration": "Kippu o kawanakereba narimasen."},
    {"english": "How long does it take by train?", "native": "電車でどのくらいかかりますか？", "transliteration": "Densha de dono kurai kakarimasu ka?"},
    {"english": "Please wait a moment.", "native": "少々お待ちください。", "transliteration": "Shōshō omachi kudasai."},
    {"english": "I don't understand yet.", "native": "まだよく分かりません。", "transliteration": "Mada yoku wakarimasen."},
    {"english": "Can you say that again?", "native": "もう一度言ってもらえますか？", "transliteration": "Mō ichido itte moraemasu ka?"},
    {"english": "I am looking for a hotel.", "native": "ホテルを探しています。", "transliteration": "Hoteru o sagashite imasu."},
    {"english": "This is my first time here.", "native": "ここに来るのは初めてです。", "transliteration": "Koko ni kuru no wa hajimete desu."},
    {"english": "Let's meet in front of the station.", "native": "駅の前で会いましょう。", "transliteration": "Eki no mae de aimashō."},
    {"english": "I will be back soon.", "native": "すぐ戻ります。", "transliteration": "Sugu modorimasu."},
    {"english": "Thank you for your help.", "native": "助けてくれてありがとうございます。", "transliteration": "Tasukete kurete arigatō gozaimasu."},
    {"english": "Please take care of yourself.", "native": "お体に気をつけてください。", "transliteration": "Okarada ni ki o tsukete kudasai."},
    {"english": "I am glad to hear that.", "native": "それを聞いてうれしいです。", "transliteration": "Sore o kiite ureshii desu."},
    {"english": "That sounds like a good idea.", "native": "それはいい考えですね。", "transliteration": "Sore wa ii kangae desu ne."},
    {"english": "I will try my best.", "native": "頑張ります。", "transliteration": "Ganbarimasu."},
    {"english": "Don't worry too much.", "native": "あまり心配しないでください。", "transliteration": "Amari shinpai shinaide kudasai."},
    {"english": "We can do it together.", "native": "一緒にできますよ。", "transliteration": "Issho ni dekimasu yo."},
    {"english": "The weather is nice today.", "native": "今日はいい天気ですね。", "transliteration": "Kyō wa ii tenki desu ne."},
    {"english": "I want to learn more Japanese.", "native": "もっと日本語を学びたいです。", "transliteration": "Motto nihongo o manabitai desu."},
    {"english": "Please write it down for me.", "native": "書いてもらえますか？", "transliteration": "Kaite moraemasu ka?"},
    {"english": "I am sorry I am late.", "native": "遅れてすみません。", "transliteration": "Okurete sumimasen."},
    {"english": "Where can I find a pharmacy?", "native": "薬局はどこにありますか？", "transliteration": "Yakkyoku wa doko ni arimasu ka?"},
    {"english": "This bag is too expensive.", "native": "このかばんは高すぎます。", "transliteration": "Kono kaban wa takasugimasu."},
    {"english": "Do you have this in another color?", "native": "これの別の色はありますか？", "transliteration": "Kore no betsu no iro wa arimasu ka?"},
    {"english": "I would like some water, please.", "native": "お水をお願いします。", "transliteration": "Omizu o onegaishimasu."},
    {"english": "The bill, please.", "native": "お会計をお願いします。", "transliteration": "Okaikei o onegaishimasu."},
    {"english": "I am allergic to peanuts.", "native": "ピーナッツアレルギーがあります。", "transliteration": "Pīnattsu arerugī ga arimasu."},
    {"english": "Please call an ambulance.", "native": "救急車を呼んでください。", "transliteration": "Kyūkyūsha o yonde kudasai."},
    {"english": "My wallet was stolen.", "native": "財布を盗まれました。", "transliteration": "Saifu o nusumaremashita."},
    {"english": "May I sit here?", "native": "ここに座ってもいいですか？", "transliteration": "Koko ni suwatte mo ii desu ka?"},
    {"english": "I am here on vacation.", "native": "休暇で来ました。", "transliteration": "Kyūka de kimashita."},
    {"english": "Could you take a photo of us?", "native": "写真を撮ってもらえますか？", "transliteration": "Shashin o totte moraemasu ka?"},
    {"english": "Which one is popular?", "native": "どれが人気ですか？", "transliteration": "Dore ga ninki desu ka?"},
    {"english": "I will have the same thing.", "native": "同じものをお願いします。", "transliteration": "Onaji mono o onegaishimasu."},
    {"english": "It was a lot of fun today.", "native": "今日はとても楽しかったです。", "transliteration": "Kyō wa totemo tanoshikatta desu."},
    {"english": "Let's go home together.", "native": "一緒に帰りましょう。", "transliteration": "Issho ni kaerimashō."},
    {"english": "Good luck with your work.", "native": "お仕事頑張ってください。", "transliteration": "Oshigoto ganbatte kudasai."},
    {"english": "I hope you feel better soon.", "native": "早く良くなりますように。", "transliteration": "Hayaku yoku narimasu yō ni."},
    {"english": "Congratulations on your success.", "native": "成功おめでとうございます。", "transliteration": "Seikō omedetō gozaimasu."},
    {"english": "Thank you for the wonderful gift.", "native": "素敵なプレゼントをありがとうございます。", "transliteration": "Suteki na purezento o arigatō gozaimasu."},
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
