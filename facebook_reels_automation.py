"""
Facebook Reels Automation - Bilingual English/Spanish Content Generator
IMPROVED VERSION: Better backgrounds, English categories, no repeats, Velocity Spanish branding
"""

import os
import sys
import json
import random
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

# Directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"

for d in [OUTPUT_DIR, IMAGES_DIR, AUDIO_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

# Video settings (9:16 vertical)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# English category names (for American/European learners)
CATEGORIES_ENGLISH = [
    "Motivation", "Love", "Success", "Wisdom", "Happiness",
    "Self Improvement", "Gratitude", "Friendship", "Hope", "Creativity",
    "Inner Peace", "Confidence", "Perseverance", "Inspiration", "Positive Life",
    "Courage", "Kindness", "Patience", "Forgiveness", "Strength",
    "Joy", "Balance", "Growth", "Purpose", "Mindfulness",
]

# Spanish translations for display
CATEGORIES_SPANISH = {
    "Motivation": "Motivación",
    "Love": "Amor",
    "Success": "Éxito",
    "Wisdom": "Sabiduría",
    "Happiness": "Felicidad",
    "Self Improvement": "Superación",
    "Gratitude": "Gratitud",
    "Friendship": "Amistad",
    "Hope": "Esperanza",
    "Creativity": "Creatividad",
    "Inner Peace": "Paz Interior",
    "Confidence": "Confianza",
    "Perseverance": "Perseverancia",
    "Inspiration": "Inspiración",
    "Positive Life": "Vida Positiva",
    "Courage": "Coraje",
    "Kindness": "Amabilidad",
    "Patience": "Paciencia",
    "Forgiveness": "Perdón",
    "Strength": "Fortaleza",
    "Joy": "Alegría",
    "Balance": "Equilibrio",
    "Growth": "Crecimiento",
    "Purpose": "Propósito",
    "Mindfulness": "Conciencia Plena",
}

# Edge TTS voices
ENGLISH_VOICE = "en-US-GuyNeural"
SPANISH_VOICE = "es-ES-AlvaroNeural"

# Phrase history file (NEVER delete this!)
PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"


# ============== PHRASE HISTORY MANAGEMENT (Prevent Repeats) ==============

def load_phrase_history():
    """Load all previously generated phrases"""
    if PHRASE_HISTORY_FILE.exists():
        try:
            with open(PHRASE_HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print(f"[history] ✅ Loaded history from: {PHRASE_HISTORY_FILE}")
            print(f"[history] 📊 File contains {len(data.get('phrases', []))} phrases, {len(data.get('used_english', []))} unique entries")
            
            # Migrate old format: populate used_english from phrases if missing
            if "used_english" not in data and "phrases" in data:
                data["used_english"] = [p.get("english", "").lower().strip() for p in data["phrases"] if p.get("english")]
                print(f"[history] 🔄 Migrated {len(data['used_english'])} phrases to new format")
                # Save migrated format
                save_phrase_history(data)
            
            return data
        except Exception as e:
            print(f"[history] ⚠️ Error loading history: {e}")
            return {"phrases": [], "used_english": [], "last_updated": None}
    
    print(f"[history] ⚠️ No history file found at: {PHRASE_HISTORY_FILE}")
    print(f"[history] 📝 Creating new empty history")
    return {"phrases": [], "used_english": [], "last_updated": None}


def save_phrase_history(data):
    """Save phrase history"""
    data["last_updated"] = datetime.now().isoformat()
    # Keep only last 3000 phrases to avoid file bloat while ensuring no repeats
    if "used_english" in data:
        data["used_english"] = data["used_english"][-3000:]
    if "phrases" in data:
        data["phrases"] = data["phrases"][-3000:]
    with open(PHRASE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_phrase_similarity(phrase1, phrase2):
    """Calculate word-based Jaccard similarity between two phrases"""
    words1 = set(phrase1.lower().split())
    words2 = set(phrase2.lower().split())
    
    if len(words1) == 0 or len(words2) == 0:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    return intersection / union if union > 0 else 0.0


def is_phrase_used(english_phrase, similarity_threshold=0.55):
    """
    Check if phrase was already generated using both exact and fuzzy matching.
    
    similarity_threshold: 0.55 means if 55% of words overlap, it's considered a duplicate.
    Lower = stricter detection.
    """
    history = load_phrase_history()
    english_clean = english_phrase.lower().strip()
    used_phrases = history.get("used_english", [])
    
    # Check for exact match first (fast)
    if english_clean in used_phrases:
        return True
    
    # For short phrases (< 4 words), do substring check
    if len(english_clean.split()) < 4:
        for used in used_phrases:
            if english_clean in used.lower() or used.lower() in english_clean:
                return True
    
    # Fuzzy matching for all phrases
    for used in used_phrases:
        similarity = calculate_phrase_similarity(english_clean, used)
        if similarity >= similarity_threshold:
            return True
    
    return False


def add_phrases_to_history(phrases, category):
    """Add new phrases to history with duplicate prevention - ROBUST"""
    history = load_phrase_history()
    
    phrases_added = 0
    for phrase in phrases:
        english_clean = phrase["english"].lower().strip()
        
        # Only add if not already in history (double-check)
        if english_clean not in history["used_english"]:
            # Add to phrases list
            history["phrases"].append({
                "english": phrase["english"],
                "spanish": phrase["spanish"],
                "category": category,
                "generated_at": datetime.now().isoformat()
            })
            
            # Add to used_english list for faster lookup
            history["used_english"].append(english_clean)
            phrases_added += 1
    
    # Save immediately
    save_phrase_history(history)
    
    # Verify save was successful
    verify_history = load_phrase_history()
    if len(verify_history["used_english"]) >= len(history["used_english"]):
        print(f"[history] ✅ VERIFIED: Added {phrases_added} phrases (total unique: {len(verify_history['used_english'])})")
    else:
        print(f"[history] ⚠️ WARNING: Save verification failed!")


# ============== CONTENT GENERATION ==============

def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    """Generate unique bilingual phrases with viral hooks, ensuring no repeats"""

    category_spanish = CATEGORIES_SPANISH[category_english]
    history = load_phrase_history()
    used_phrases = history.get("used_english", [])  # Get ALL used phrases, not just last 50
    
    print(f"[content] 📊 Checking against {len(used_phrases)} previously used phrases")
    print(f"[content] 🚫 Last 15 used phrases: {used_phrases[-15:]}")

    # Try AI first with viral hook instruction and used phrases context
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            import requests
            import random
            url = "https://gen.pollinations.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
                "Content-Type": "application/json"
            }

            # Build exclusion list for AI - show ALL used phrases prominently
            exclusion_note = ""
            if used_phrases:
                # Show last 100 used phrases to AI
                recent_used = used_phrases[-100:] if len(used_phrases) > 100 else used_phrases
                exclusion_note = f"\n\n🚫 CRITICAL: DO NOT USE or create phrases similar to these {len(recent_used)} phrases (ALREADY GENERATED):\n{json.dumps(recent_used, indent=2)}"

            # Add random seed for variety
            random_seed = random.randint(1, 1000000)

            prompt = f"""Create {num_phrases * 3} VIRAL {category_english} phrases for English speakers learning Spanish. Random seed: {random_seed}

🎯 VIRAL HOOK REQUIREMENTS:
1. Start with attention-grabbing words: "Stop...", "Never...", "This is why...", "The secret...", "What nobody tells you..."
2. Create curiosity gaps that make people watch till the end
3. Use emotional triggers: inspiration, surprise, urgency, relatability
4. Make each phrase SHAREABLE - something people send to friends
5. Keep it VERY SHORT (3-8 words MAX) - perfect for TikTok/Reels/Shorts
6. Add natural pauses with commas for TTS rhythm

📝 FORMAT:
- English: Catchy hook + valuable message (MAX 8 WORDS)
- Spanish: Accurate translation with same emotional impact
- Pronunciation: Simple phonetic for English speakers

{exclusion_note}

💡 EXAMPLES OF VIRAL HOOKS:
- "Stop saying 'I can't'"
- "This changes everything"
- "The secret? Consistency"
- "Never translate word-for-word"
- "Your future self is watching"

⚠️ CRITICAL RULES:
- MAX 8 WORDS per phrase (shorter = more viral)
- NO complex grammar
- NO long explanations
- Every word must count
- MUST be different from all {len(used_phrases)} phrases above

Return as JSON array:
[{{"english": "...", "spanish": "...", "pronunciation": "..."}}]

⚠️ CRITICAL: Every phrase must be COMPLETELY NEW, CATCHY, and VIRAL-WORTHY. Check against excluded list above. Random seed: {random_seed}"""

            payload = {
                "model": "openai",
                "messages": [
                    {"role": "system", "content": "You are a viral Spanish teacher and social media expert. Create scroll-stopping, shareable phrases with hooks that make people watch, save, and share. NEVER repeat phrases. Each request should generate UNIQUE content."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.2,  # Even higher for more variety
                "seed": random_seed  # Add seed for randomness
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            phrases = json.loads(content)

            # Filter out already-used phrases and ensure proper length
            unique_phrases = []
            for phrase in phrases:
                # Skip if too long (over 8 words)
                if len(phrase["english"].split()) > 8:
                    print(f"[content] ⚠️ Skipping (too long): {phrase['english'][:50]}...")
                    continue
                # Skip if phrase is used (with fuzzy matching)
                if is_phrase_used(phrase["english"]):
                    print(f"[content] ⚠️ Skipping duplicate: {phrase['english'][:50]}...")
                    continue
                unique_phrases.append(phrase)
                if len(unique_phrases) >= num_phrases:
                    break

            if len(unique_phrases) >= num_phrases:
                add_phrases_to_history(unique_phrases[:num_phrases], category_english)
                return unique_phrases[:num_phrases]
            else:
                print(f"[content] Only got {len(unique_phrases)} unique phrases, need {num_phrases}")

        except Exception as e:
            print(f"[content] Attempt {attempt + 1} failed: {e}")

    # Fallback to fresh phrases (with duplicate check)
    print("[content] Using fallback phrases...")
    fallback_phrases = get_fresh_fallback_phrases(category_english, num_phrases)
    
    # Add fallback phrases to history to prevent future repeats
    if fallback_phrases:
        add_phrases_to_history(fallback_phrases, category_english)
    
    return fallback_phrases


def get_fresh_fallback_phrases(category: str, num_phrases: int) -> list:
    """Get viral fallback phrases with hooks, filtering out used ones"""

    # Viral fallback phrases - SHORT (max 8 words) with attention-grabbing hooks
    all_fallbacks = {
        "Motivation": [
            {"english": "Stop waiting. Start now.", "spanish": "Deja de esperar. Comienza ahora.", "pronunciation": "Deh-hah deh eh-speh-rahr. Koh-meehn-sah ah-oh-rah."},
            {"english": "This is why you're stuck.", "spanish": "Por esto estás atascado.", "pronunciation": "Por ehs-toh ehs-tahs ah-tahs-kah-doh."},
            {"english": "The secret? Consistency wins.", "spanish": "¿El secreto? La constancia gana.", "pronunciation": "Ehl seh-kreh-toh? Lah kohns-tahn-see-ah gah-nah."},
            {"english": "What nobody tells you about success.", "spanish": "Lo que nadie te dice del éxito.", "pronunciation": "Loh keh nah-dyeh teh dee-seh dehl ehk-see-toh."},
            {"english": "Your future self is watching.", "spanish": "Tu yo futuro te mira.", "pronunciation": "Too yoh foo-too-roh teh mee-rah."},
            {"english": "Stop saying 'someday'. Say 'today'.", "spanish": "Deja de decir 'algún día'. Di 'hoy'.", "pronunciation": "Deh-hah deh deh-seer ahl-goon dee-ah. Dee oy."},
        ],
        "Love": [
            {"english": "Stop chasing. Real love finds you.", "spanish": "Deja de perseguir. El amor real te encuentra.", "pronunciation": "Deh-hah deh pehr-seh-geer. El ah-mor reh-ahl teh ehn-kwehn-trah."},
            {"english": "This is what real love feels.", "spanish": "Así se siente el amor verdadero.", "pronunciation": "Ah-see seh seeehn-teh el ah-mor vehr-dah-deh-roh."},
            {"english": "The secret to being deeply loved.", "spanish": "El secreto para ser amado.", "pronunciation": "Ehl seh-kreh-toh pah-rah sehr ah-mah-doh."},
            {"english": "What nobody tells you about heartbreak.", "spanish": "Lo que nadie te dice del desamor.", "pronunciation": "Loh keh nah-dyeh teh dee-seh dehl deh-sah-mor."},
            {"english": "You deserve this kind of love.", "spanish": "Mereces este tipo de amor.", "pronunciation": "Meh-reh-sehs ehs-teh tee-poh deh ah-mor."},
            {"english": "Never settle for less.", "spanish": "Nunca te conformes con menos.", "pronunciation": "Noon-kah teh kohn-for-mehs kohn meh-nohs."},
        ],
        "Success": [
            {"english": "Stop this if you want success.", "spanish": "Deja esto si quieres éxito.", "pronunciation": "Deh-hah ehs-toh see kyeh-rehs ehk-see-toh."},
            {"english": "The one habit that changes everything.", "spanish": "El hábito que lo cambia todo.", "pronunciation": "El ah-bee-toh keh loh kahm-byah toh-doh."},
            {"english": "What successful people do before 8am.", "spanish": "Lo que hace la gente exitosa temprano.", "pronunciation": "Loh keh ah-seh lah hehn-teh ehk-see-toh-sah tehm-prah-noh."},
            {"english": "This mindset shift changes lives.", "spanish": "Este cambio mental cambia vidas.", "pronunciation": "Ehs-teh kahm-byoh mehn-tahl kahm-byah vee-dahs."},
            {"english": "Why you're not seeing results.", "spanish": "Por qué no ves resultados.", "pronunciation": "Por keh noh vehs reh-sool-tah-dohs."},
            {"english": "The truth about overnight success.", "spanish": "La verdad sobre el éxito repentino.", "pronunciation": "Lah vehr-dahd soh-breh ehl ehk-see-toh reh-pehn-tee-noh."},
        ],
        "Wisdom": [
            {"english": "Stop overthinking. Start doing.", "spanish": "Deja de pensar. Empieza a hacer.", "pronunciation": "Deh-hah deh pehn-sahr. Ehm-peeehn-sah ah ah-sehr."},
            {"english": "The lesson life keeps teaching.", "spanish": "La lección que la vida enseña.", "pronunciation": "Lah lehk-seeohn keh lah vee-dah ehn-seh-nyah."},
            {"english": "What I wish I knew at 20.", "spanish": "Lo que desearía saber a los 20.", "pronunciation": "Loh keh deh-seh-ah-ree-ah sah-behr ah lohs veyn-teh."},
            {"english": "This truth will set you free.", "spanish": "Esta verdad te liberará.", "pronunciation": "Ehs-tah vehr-dahd teh lee-beh-rah-rah."},
            {"english": "The price of staying the same.", "spanish": "El precio de permanecer igual.", "pronunciation": "El preh-see-oh deh pehr-mah-neh-sehr ee-gwahl."},
            {"english": "Why wise people stay quiet.", "spanish": "Por qué la gente sabia calla.", "pronunciation": "Por keh lah hehn-teh sah-byah kah-yah."},
        ],
        "Happiness": [
            {"english": "Stop looking for happiness there.", "spanish": "Deja de buscar la felicidad ahí.", "pronunciation": "Deh-hah deh boos-kahr lah feh-lee-see-dahd ah-ee."},
            {"english": "This simple trick boosts joy.", "spanish": "Este truco simple aumenta la alegría.", "pronunciation": "Ehs-teh troo-koh seem-pleh ow-mehn-tah lah ah-leh-gree-ah."},
            {"english": "What happy people do differently.", "spanish": "Lo que hace la gente feliz diferente.", "pronunciation": "Loh keh ah-seh lah hehn-teh feh-lees dee-feh-rehn-teh."},
            {"english": "The real source of lasting happiness.", "spanish": "La fuente real de felicidad duradera.", "pronunciation": "Lah fwehn-teh reh-ahl deh feh-lee-see-dahd doo-rah-deh-rah."},
            {"english": "You're one choice away from joy.", "spanish": "Estás a una elección de la alegría.", "pronunciation": "Ehs-tahs ah oo-nah eh-lehk-seeohn deh lah ah-leh-gree-ah."},
            {"english": "Stop waiting. Choose happiness now.", "spanish": "Deja de esperar. Elige felicidad ahora.", "pronunciation": "Deh-hah deh eh-speh-rahr. Eh-lee-heh feh-lee-see-dahd ah-oh-rah."},
        ],
        "Self Improvement": [
            {"english": "This one change transformed me.", "spanish": "Este único cambio me transformó.", "pronunciation": "Ehs-teh oo-nee-koh kahm-byoh meh trahns-for-moh."},
            {"english": "Stop wasting time on this.", "spanish": "Deja de perder tiempo en esto.", "pronunciation": "Deh-hah deh pehr-dehr teeehm-poh en ehs-toh."},
            {"english": "The 1% rule that changes lives.", "spanish": "La regla del 1% cambia vidas.", "pronunciation": "Lah reh-glah dehl oo-noh por seeehn-toh kahm-byah vee-dahs."},
            {"english": "What I do every morning.", "spanish": "Lo que hago cada mañana.", "pronunciation": "Loh keh ah-goh kah-dah mah-nyah-nah."},
            {"english": "Your comfort zone is killing you.", "spanish": "Tu zona de confort te mata.", "pronunciation": "Too soh-nah deh kohn-for-t teh mah-tah."},
            {"english": "Become who you were meant to be.", "spanish": "Conviértete en quien debías ser.", "pronunciation": "Kohn-vyehr-teh-teh en kyeehn deh-bee-ahs sehr."},
        ],
        "Gratitude": [
            {"english": "This practice changed my life.", "spanish": "Esta práctica cambió mi vida.", "pronunciation": "Ehs-tah prahk-tee-kah kahm-byoh mee vee-dah."},
            {"english": "Stop scrolling. Count your blessings.", "spanish": "Deja de desplazarte. Cuenta bendiciones.", "pronunciation": "Deh-hah deh deh-plah-sahr-teh. Kwehn-tah behn-dee-seeoh-nes."},
            {"english": "What grateful people do daily.", "spanish": "Lo que hace la gente agradecida diariamente.", "pronunciation": "Loh keh ah-seh lah hehn-teh ah-grah-deh-see-dah dee-ah-ree-ah-mehn-teh."},
            {"english": "The fastest way to feel abundant.", "spanish": "La forma más rápida de sentirse abundante.", "pronunciation": "Lah for-mah mahs rah-pee-dah deh seen-teer-seh ah-boon-dahn-teh."},
            {"english": "Say this every morning for 30 days.", "spanish": "Di esto cada mañana por 30 días.", "pronunciation": "Dee ehs-toh kah-dah mah-nyah-nah por treyn-tah dee-ahs."},
            {"english": "Gratitude turns what we have into enough.", "spanish": "La gratitud convierte lo tenemos en suficiente.", "pronunciation": "Lah grah-tee-tood kohn-vyehr-teh loh teh-neh-mos en soo-fee-seeehn-teh."},
        ],
        "Friendship": [
            {"english": "Real friends do this without asking.", "spanish": "Los amigos reales hacen esto sin pedir.", "pronunciation": "Lohs ah-mee-gohs reh-ah-lehs ah-sehn ehs-toh seen peh-deer."},
            {"english": "Stop calling these people friends.", "spanish": "Deja de llamar amigos a estas personas.", "pronunciation": "Deh-hah deh yah-mahr ah-mee-gohs ah ehs-tahs pehr-soh-nahs."},
            {"english": "The test of true friendship.", "spanish": "La prueba de la verdadera amistad.", "pronunciation": "Lah prweh-bah deh lah vehr-dah-deh-rah ah-mees-tahd."},
            {"english": "What I learned about loyalty.", "spanish": "Lo que aprendí sobre la lealtad.", "pronunciation": "Loh keh ah-prehn-dee soh-breh lah leh-al-tahd."},
            {"english": "Keep these people close forever.", "spanish": "Mantén a estas personas cerca siempre.", "pronunciation": "Mahn-tehn ah ehs-tahs pehr-soh-nahs sehr-kah seeehm-preh."},
            {"english": "A friend who does this is rare.", "spanish": "Un amigo que hace esto es raro.", "pronunciation": "Oon ah-mee-goh keh ah-seh ehs-toh ehs rah-roh."},
        ],
        "Hope": [
            {"english": "When everything fails, remember this.", "spanish": "Cuando todo falla, recuerda esto.", "pronunciation": "Kwahn-doh toh-doh fah-yah, reh-kwehr-dah ehs-toh."},
            {"english": "Stop believing this lie about hope.", "spanish": "Deja de creer esta mentira sobre esperanza.", "pronunciation": "Deh-hah deh kreh-ehr ehs-tah mehn-tee-rah soh-breh eh-speh-rahn-sah."},
            {"english": "The dawn always comes after darkness.", "spanish": "El amanecer siempre llega después oscuridad.", "pronunciation": "El ah-mah-neh-sehr seeehm-preh yeh-gah dehs-pwehs ohs-koo-ree-dahd."},
            {"english": "What keeps me going when quitting.", "spanish": "Lo que me mantiene siguiendo cuando rindo.", "pronunciation": "Loh keh meh mahn-tee-neh see-gyehn-doh kwahn-doh reen-doh."},
            {"english": "Your breakthrough is closer than think.", "spanish": "Tu avance está más cerca piensas.", "pronunciation": "Too ah-vahn-seh ehs-tah mahs sehr-kah pyehn-sahs."},
            {"english": "Never lose faith. This too shall pass.", "spanish": "Nunca pierdas fe. Esto también pasará.", "pronunciation": "Noon-kah pyehr-dahs feh. Ehs-toh tahm-byehn pah-sah-rah."},
        ],
        "Creativity": [
            {"english": "Stop waiting for inspiration. Do.", "spanish": "Deja de esperar inspiración. Haz.", "pronunciation": "Deh-hah deh eh-speh-rahr eens-pee-rah-seeohn. Ahz."},
            {"english": "The secret to endless creative ideas.", "spanish": "El secreto para ideas creativas infinitas.", "pronunciation": "Ehl seh-kreh-toh pah-rah ee-deh-ahs kree-ah-tee-vahs een-fee-nee-tahs."},
            {"english": "What artists know that others don't.", "spanish": "Lo que los artistas saben otros no.", "pronunciation": "Loh keh lohs ahr-tees-tahs sah-behn oh-trohs noh."},
            {"english": "Your creativity is hiding here.", "spanish": "Tu creatividad se está escondiendo aquí.", "pronunciation": "Too kree-ah-tee-vee-dahd seh ehs-tah ehs-kohn-dyehn-doh ah-kee."},
            {"english": "Break these rules to be creative.", "spanish": "Rompe estas reglas para ser creativo.", "pronunciation": "Rohm-peh ehs-tahs reh-glahs pah-rah sehr kree-ah-tee-voh."},
            {"english": "Create first, edit later. Trust.", "spanish": "Crea primero, edita después. Confía.", "pronunciation": "Kreh-ah pree-meh-roh, eh-dee-tah dehs-pwehs. Kohn-fee-ah."},
        ],
        "Inner Peace": [
            {"english": "Stop letting them steal your peace.", "spanish": "Deja de dejarles robar tu paz.", "pronunciation": "Deh-hah deh deh-hahr-lehs roh-bahr too pahz."},
            {"english": "This breathing trick calms anxiety.", "spanish": "Este truco respiración calma ansiedad.", "pronunciation": "Ehs-teh troo-koh reh-spee-rah-seeohn kahl-mah ahng-seeeh-dahd."},
            {"english": "What I do when mind races.", "spanish": "Lo que hago cuando mente corre.", "pronunciation": "Loh keh ah-goh kwahn-doh mehn-teh koh-rreh."},
            {"english": "The price of inner peace.", "spanish": "El precio de la paz interior.", "pronunciation": "El preh-see-oh deh lah pahz een-teh-ree-or."},
            {"english": "Let go of what you can't control.", "spanish": "Suelta lo que no puedes controlar.", "pronunciation": "Swehl-tah loh keh noh pweh-dehs kohn-troh-lahr."},
            {"english": "Your calm mind is your superpower.", "spanish": "Tu mente calmada es tu superpoder.", "pronunciation": "Too mehn-teh kahl-mah-dah ehs too soo-pehr-poh-dehr."},
        ],
        "Confidence": [
            {"english": "Stop this if you want confidence.", "spanish": "Deja esto si quieres confianza.", "pronunciation": "Deh-hah ehs-toh see kyeh-rehs kohn-fee-ahn-sah."},
            {"english": "Fake confidence until you become it.", "spanish": "Finge confianza hasta que te conviertas.", "pronunciation": "Feen-heh kohn-fee-ahn-sah ah-stah keh teh kohn-vyehr-tahs."},
            {"english": "The body language trick that works.", "spanish": "El truco lenguaje corporal que funciona.", "pronunciation": "Ehl troo-koh lehn-gwah-heh kor-poh-rahl keh foon-seeoh-nah."},
            {"english": "What confident people never say.", "spanish": "Lo que la gente confiada nunca dice.", "pronunciation": "Loh keh lah hehn-teh kohn-fee-ah-dah noon-kah dee-seh."},
            {"english": "Your self-talk is shaping you.", "spanish": "Tu diálogo interno te está formando.", "pronunciation": "Too dee-ah-loh-goh een-tehr-noh teh ehs-tah for-mahn-doh."},
            {"english": "Stand tall. You're unstoppable.", "spanish": "Mantente firme. Eres imparable.", "pronunciation": "Mahn-tehn-teh feer-meh. Eh-rehs eem-pah-rah-bleh."},
        ],
        "Perseverance": [
            {"english": "When you want to quit, read.", "spanish": "Cuando quieras rendirte, lee.", "pronunciation": "Kwahn-doh kyeh-rahs rehn-deer-teh, leh-eh."},
            {"english": "The pain you feel is growth.", "spanish": "El dolor que sientes es crecimiento.", "pronunciation": "El doh-lor keh seeehn-tehs ehs kreh-see-meeehn-toh."},
            {"english": "Why most people give up soon.", "spanish": "Por qué la mayoría se rinde pronto.", "pronunciation": "Por keh lah mah-yoh-ree-ah seh reen-deh prohn-toh."},
            {"english": "This separates winners from losers.", "spanish": "Esto separa ganadores de perdedores.", "pronunciation": "Ehs-toh seh-pah-rah gah-nah-doh-rehs deh pehr-deh-doh-rehs."},
            {"english": "Keep going. Your moment is coming.", "spanish": "Sigue yendo. Tu momento está llegando.", "pronunciation": "See-geh yehn-doh. Too moh-mehn-toh ehs-tah yeh-gahn-doh."},
            {"english": "Champions are made in dark.", "spanish": "Los campeones se hacen oscuridad.", "pronunciation": "Lohs kahm-peh-oh-nehs seh ah-sehn ohs-koo-ree-dahd."},
        ],
        "Inspiration": [
            {"english": "This message found you for reason.", "spanish": "Este mensaje te encontró por razón.", "pronunciation": "Ehs-teh mehn-sah-heh teh ehn-kohn-troh por rah-sohn."},
            {"english": "Stop doubting. You were chosen.", "spanish": "Deja de dudar. Fuiste elegido.", "pronunciation": "Deh-hah deh doo-dahr. Fwees-teh eh-leh-hee-doh."},
            {"english": "The world needs your unique gift.", "spanish": "El mundo necesita tu regalo único.", "pronunciation": "El moon-doh neh-seh-see-tah too reh-gah-loh oo-nee-koh."},
            {"english": "What I learned from lowest point.", "spanish": "Lo que aprendí desde punto más bajo.", "pronunciation": "Loh keh ah-prehn-dee dehs-deh poon-toh mahs bah-hoh."},
            {"english": "Your comeback will be legendary.", "spanish": "Tu regreso será legendario.", "pronunciation": "Too reh-greh-soh seh-rah leh-hehn-dah-ree-oh."},
            {"english": "Be the person you needed younger.", "spanish": "Sé persona que necesitabas cuando joven.", "pronunciation": "Seh pehr-soh-nah keh neh-seh-see-tah-bahs kwahn-doh hoh-vehn."},
        ],
        "Positive Life": [
            {"english": "Cut these toxic habits from life.", "spanish": "Corta estos hábitos tóxicos vida.", "pronunciation": "Kor-tah ehs-tohs ah-bee-tohs tohk-see-kohs vee-dah."},
            {"english": "The mindset that attracts good things.", "spanish": "La mentalidad que atrae cosas buenas.", "pronunciation": "Lah mehn-tah-lee-dahd keh ah-try-eh koh-sahs bweh-nahs."},
            {"english": "Stop consuming. Start creating.", "spanish": "Deja de consumir. Empieza a crear.", "pronunciation": "Deh-hah deh kohn-soo-meer. Ehm-peeehn-sah ah kreh-ahr."},
            {"english": "Your vibe attracts your tribe.", "spanish": "Tu vibra atrae a tu tribu.", "pronunciation": "Too vee-brah ah-try-eh ah too tree-boo."},
            {"english": "Choose progress over perfection always.", "spanish": "Elige progreso sobre perfección siempre.", "pronunciation": "Eh-lee-heh proh-greh-soh soh-breh pehr-fehk-seeohn seeehm-preh."},
            {"english": "Good things happen to those who hustle.", "spanish": "Cosas buenas pasan a quienes trabajan duro.", "pronunciation": "Koh-sahs bweh-nahs pah-sahn ah kyee-nehs trah-bah-hahn doo-roh."},
        ],
        "Courage": [
            {"english": "Feel the fear. Do it anyway.", "spanish": "Siente el miedo. Hazlo todos modos.", "pronunciation": "Seeehn-teh el mee-eh-doh. Ahz-loh toh-dohs moh-dohs."},
            {"english": "This is what bravery really looks.", "spanish": "Así es como se ve valentía.", "pronunciation": "Ah-see ehs koh-moh seh veh vah-lehn-tee-ah."},
            {"english": "Stop hiding. The world needs seeing.", "spanish": "Deja de esconderte. Mundo necesita verte.", "pronunciation": "Deh-hah deh ehs-kohn-dehr-teh. Moon-doh neh-seh-see-tah vehr-teh."},
            {"english": "The risk you're avoiding is worth.", "spanish": "El riesgo que evitas vale pena.", "pronunciation": "El ree-ez-goh keh eh-vee-tahs vah-leh peh-nah."},
            {"english": "Courage isn't fearlessness. It's this.", "spanish": "El coraje no es falta miedo. Es esto.", "pronunciation": "El koh-rah-heh noh ehs fahl-tah mee-eh-doh. Ehs ehs-toh."},
            {"english": "Take the leap. The net appears.", "spanish": "Da el salto. La red aparece.", "pronunciation": "Dah ehl sahl-toh. Lah reh-d ah-pah-reh-seh."},
        ],
        "Kindness": [
            {"english": "This small act changed someone's day.", "spanish": "Este pequeño acto cambió día alguien.", "pronunciation": "Ehs-teh peh-keh-nyoh ahk-toh kahm-byoh dee-ah ahl-gyeehn."},
            {"english": "Stop underestimating power of kindness.", "spanish": "Deja de subestimar poder amabilidad.", "pronunciation": "Deh-hah deh soo-behs-tee-mahr poh-dehr ah-mah-bee-lee-dahd."},
            {"english": "What happens when you choose kindness.", "spanish": "Lo que pasa eliges amabilidad.", "pronunciation": "Loh keh pah-sah eh-lee-hehs ah-mah-bee-lee-dahd."},
            {"english": "Your kindness is your superpower.", "spanish": "Tu amabilidad es tu superpoder.", "pronunciation": "Too ah-mah-bee-lee-dahd ehs too soo-pehr-poh-dehr."},
            {"english": "The ripple effect one kind word.", "spanish": "El efecto dominó una palabra amable.", "pronunciation": "El eh-fehk-toh doh-mee-noh oo-nah pah-lah-brah ah-mah-bleh."},
            {"english": "Be the reason someone smiles today.", "spanish": "Sé razón por la que alguien sonríe.", "pronunciation": "Seh rah-sohn por lah keh ahl-gyeehn sohn-rree-eh."},
        ],
        "Patience": [
            {"english": "Stop rushing. Trust the timing.", "spanish": "Deja de apresurarte. Confía tiempo.", "pronunciation": "Deh-hah deh ah-preh-soo-rahr-teh. Kohn-fee-ah teeehm-poh."},
            {"english": "This is why patience tested.", "spanish": "Por esto es paciencia probada.", "pronunciation": "Por ehs-toh ehs pah-seeehn-see-ah proh-bah-dah."},
            {"english": "The art of waiting without suffering.", "spanish": "El arte esperar sin sufrir.", "pronunciation": "El ahr-teh eh-speh-rahr seen soo-freer."},
            {"english": "What patient people know you don't.", "spanish": "Lo que sabe gente paciente tú no.", "pronunciation": "Loh keh sah-beh hehn-teh pah-seeehn-teh too noh."},
            {"english": "Good things come to those who wait.", "spanish": "Cosas buenas vienen quienes esperan.", "pronunciation": "Koh-sahs bweh-nahs veeh-nehn kyee-nehs eh-speh-rahn."},
            {"english": "Your seeds growing underground. Be patient.", "spanish": "Semillas creciendo bajo tierra. Sé paciente.", "pronunciation": "Seh-mee-yahs kreh-seeehn-doh bah-hoh tee-ehr-ah. Seh pah-seeehn-teh."},
        ],
        "Forgiveness": [
            {"english": "Holding grudges poisoning you. Let go.", "spanish": "Guardar rencores envenena. Suelta.", "pronunciation": "Gwahr-dahr rehn-koh-rehs ehm-veh-neh-nah. Swehl-tah."},
            {"english": "This is what forgiveness really means.", "spanish": "Esto es lo significa perdón.", "pronunciation": "Ehs-toh ehs loh seeg-nee-fee-kah pehr-dohn."},
            {"english": "Stop waiting apology won't come.", "spanish": "Deja esperar disculpa no vendrá.", "pronunciation": "Deh-hah eh-speh-rahr dees-kool-pah noh vehn-drah."},
            {"english": "The freedom feel after forgiving.", "spanish": "La libertad sientes después perdonar.", "pronunciation": "Lah lee-behr-tahd seeehn-tehs dehs-pwehs pehr-doh-nahr."},
            {"english": "Forgive them not for them, for you.", "spanish": "Perdona no por ellos, por ti.", "pronunciation": "Pehr-doh-nah noh por eh-yohs, por tee."},
            {"english": "Your healing starts moment you forgive.", "spanish": "Sanación comienza momento perdonas.", "pronunciation": "Sah-nah-seeohn koh-meehn-sah moh-mehn-toh pehr-doh-nahs."},
        ],
        "Strength": [
            {"english": "You're stronger than realize. Here's proof.", "spanish": "Eres más fuerte das cuenta. Prueba.", "pronunciation": "Eh-rehs mahs fwehr-teh dahs kwehn-tah. Prweh-bah."},
            {"english": "This is how warriors made.", "spanish": "Así es como hacen guerreros.", "pronunciation": "Ah-see ehs koh-moh ah-sehn geh-rreh-rohs."},
            {"english": "Stop apologizing for being powerful.", "spanish": "Deja disculparte por ser poderoso.", "pronunciation": "Deh-hah dees-kool-pahr-teh por sehr poh-deh-roh-soh."},
            {"english": "The storm didn't break. Refined.", "spanish": "Tormenta no rompió. Refinó.", "pronunciation": "Tor-mehn-tah noh rohm-peeoh. Reh-fee-noh."},
            {"english": "Your scars proof survival. Wear proudly.", "spanish": "Cicatrices prueba supervivencia. Lleva orgullo.", "pronunciation": "See-kah-tree-sehs prweh-bah soo-pehr-vee-vehn-see-ah. Yeh-vah or-goo-yoh."},
            {"english": "Bend but never break. That's resilience.", "spanish": "Dóblate pero nunca rompas. Resiliencia.", "pronunciation": "Doh-blah-teh peh-roh noon-kah rohm-pahs. Reh-see-lyehn-see-ah."},
        ],
        "Joy": [
            {"english": "Stop postponing joy. Celebrate now.", "spanish": "Deja posponer alegría. Celebra ahora.", "pronunciation": "Deh-hah pohs-poh-nehr ah-leh-gree-ah. Seh-leh-brah ah-oh-rah."},
            {"english": "This is what pure joy feels.", "spanish": "Así es como siente alegría pura.", "pronunciation": "Ah-see ehs koh-moh seeehn-teh ah-leh-gree-ah poo-rah."},
            {"english": "Find joy ordinary. It's magic.", "spanish": "Encuentra alegría ordinario. Mágico.", "pronunciation": "Ehn-kwehn-trah ah-leh-gree-ah or-dee-nah-ree-oh. Mah-hee-koh."},
            {"english": "What joyful people do you don't.", "spanish": "Lo que hace gente alegre tú no.", "pronunciation": "Loh keh ah-seh hehn-teh ah-leh-greh too noh."},
            {"english": "Your joy is act resistance.", "spanish": "Alegría es acto resistencia.", "pronunciation": "Ah-leh-gree-ah ehs ahk-toh reh-zees-tehn-see-ah."},
            {"english": "Dance through life nobody's watching.", "spanish": "Baila vida como si nadie viera.", "pronunciation": "Bahy-lah vee-dah koh-moh see nah-dyeh vee-eh-rah."},
        ],
        "Balance": [
            {"english": "Stop burning out. Find rhythm.", "spanish": "Deja quemarte. Encuentra ritmo.", "pronunciation": "Deh-hah keh-mahr-teh. Ehn-kwehn-trah reet-moh."},
            {"english": "This work-life balance really looks.", "spanish": "Así equilibrio trabajo-vida realmente.", "pronunciation": "Ah-see eh-kee-lee-bree-oh trah-bah-hoh-vee-dah reh-ahl-mehn-teh."},
            {"english": "Secret having all without losing yourself.", "spanish": "Secreto tenerlo todo sin perderte.", "pronunciation": "Seh-kreh-toh teh-nehr-loh toh-doh seen pehr-dehr-teh."},
            {"english": "Can't pour from empty cup. Fill.", "spanish": "No servir desde taza vacía. Llena.", "pronunciation": "Noh sehr-veer dehs-deh tah-sah vah-see-ah. Yeh-nah."},
            {"english": "Rest productive. Stop feeling guilty.", "spanish": "Descansar productivo. Deja sentirte culpable.", "pronunciation": "Dehs-kahn-sahr proh-duk-tee-voh. Deh-hah seen-teer-teh kool-pah-bleh."},
            {"english": "Find center. Everything else aligns.", "spanish": "Encuentra centro. Todo demás alinea.", "pronunciation": "Ehn-kwehn-trah sehn-troh. Toh-doh deh-mahs ah-lee-neh-ah."},
        ],
        "Growth": [
            {"english": "This discomfort feel? That's growth.", "spanish": "¿Incomodidad sientes? Eso crecimiento.", "pronunciation": "Een-koh-moh-dee-dahd seeehn-tehs? Eh-soh kreh-see-meeehn-toh."},
            {"english": "Stop playing small. Meant more.", "spanish": "Deja jugar pequeño. Creado más.", "pronunciation": "Deh-hah hoo-gahr peh-keh-nyoh. Kree-ah-doh mahs."},
            {"english": "Person becoming worth pain.", "spanish": "Persona conviertes vale pena.", "pronunciation": "Pehr-soh-nah kohn-vyehr-tehs vah-leh peh-nah."},
            {"english": "What growing pains teach you.", "spanish": "Dolores crecimiento intentan enseñan.", "pronunciation": "Doh-loh-rehs kreh-see-meeehn-toh een-tehn-tahn ehn-seh-nyahn."},
            {"english": "Embrace suck. It's temporary.", "spanish": "Abraza difícil. Temporal.", "pronunciation": "Ah-brah-sah dee-fee-seel. Tehtm-poh-rahl."},
            {"english": "Potential unlimited. Start acting.", "spanish": "Potencial ilimitado. Empieza actuar.", "pronunciation": "Poh-tehn-see-ahl ee-lee-mee-tah-doh. Ehm-peeehn-sah ahk-twahr."},
        ],
        "Purpose": [
            {"english": "Stop searching. Purpose already here.", "spanish": "Deja buscar. Propósito ya aquí.", "pronunciation": "Deh-hah boos-kahr. Proh-poh-see-toh yah ah-kee."},
            {"english": "This is why feel unfulfilled.", "spanish": "Por esto es sientes insatisfecho.", "pronunciation": "Por ehs-toh ehs seeehn-tehs een-sah-tees-feh-choh."},
            {"english": "Intersection joy service purpose.", "spanish": "Intersección alegría servicio propósito.", "pronunciation": "Een-tehr-sehk-seeohn ah-leh-gree-ah sehr-vee-see-oh proh-poh-see-toh."},
            {"english": "What meant do find you.", "spanish": "Lo destinado hacer encontrará.", "pronunciation": "Loh dehs-tee-nah-doh ah-sehr ehn-kohn-trah-rah."},
            {"english": "Live intention live regret.", "spanish": "Vive intención vive arrepentimiento.", "pronunciation": "Vee-veh een-tehn-seeohn vee-veh ah-reh-pehn-tee-meeehn-toh."},
            {"english": "Legacy starts today's choices.", "spanish": "Legado comienza elecciones hoy.", "pronunciation": "Leh-gah-doh koh-meehn-sah eh-lehk-seeoh-nes oy."},
        ],
        "Mindfulness": [
            {"english": "Stop living autopilot. Wake now.", "spanish": "Deja vivir piloto automático. Despierta.", "pronunciation": "Deh-hah vee-veer pee-loh-toh ow-toh-mah-tee-koh. Dehs-pyehr-tah."},
            {"english": "This moment all truly have.", "spanish": "Momento todo realmente tienes.", "pronunciation": "Moh-mehn-toh toh-doh reh-ahl-mehn-teh tee-eh-nehs."},
            {"english": "Present called gift reason.", "spanish": "Presente llama regalo razón.", "pronunciation": "Preh-sehn-teh yah-mah reh-gah-loh rah-sohn."},
            {"english": "What mindfulness does brain.", "spanish": "Atención plena hace cerebro.", "pronunciation": "Ah-tehn-seeohn pleh-nah ah-seh seh-reh-broh."},
            {"english": "Breathe. This only moment exists.", "spanish": "Respira. Este único momento existe.", "pronunciation": "Rehs-pee-rah. Ehs-teh oo-nee-koh moh-mehn-toh eh-kees-teh."},
            {"english": "Mind tool. Master it.", "spanish": "Mente herramienta. Domínala.", "pronunciation": "Mehn-teh eh-rrah-meeehn-tah. Doh-mee-nah-lah."},
        ],
    }

    fallbacks = all_fallbacks.get(category, all_fallbacks["Motivation"])
    
    # Filter with fuzzy matching to avoid similar phrases
    fresh_phrases = []
    for phrase in fallbacks:
        if not is_phrase_used(phrase["english"]):
            fresh_phrases.append(phrase)
    
    # If we still don't have enough, try to get creative variations
    if len(fresh_phrases) < num_phrases:
        print(f"[fallback] Only {len(fresh_phrases)} fresh fallbacks, adding more...")
        # Add generic viral phrases as last resort (SHORT)
        generic_phrases = [
            {"english": "Stop scrolling. This is your sign.", "spanish": "Deja desplazarte. Esta tu señal.", "pronunciation": "Deh-hah deh-plah-sahr-teh. Ehs-tah too seh-nyahl."},
            {"english": "You needed hear this today.", "spanish": "Necesitabas escuchar esto hoy.", "pronunciation": "Neh-seh-see-tah-bahs ehs-koo-char ehs-toh oy."},
            {"english": "This is your wake-up call.", "spanish": "Esta es tu llamada atención.", "pronunciation": "Ehs-tah ehs too yah-mah-dah ah-tehn-seeohn."},
            {"english": "Don't skip. This changes everything.", "spanish": "No saltes. Esto cambia todo.", "pronunciation": "Noh sahl-tehs. Ehs-toh kahm-byah toh-doh."},
        ]
        for phrase in generic_phrases:
            if not is_phrase_used(phrase["english"]) and len(fresh_phrases) < num_phrases:
                fresh_phrases.append(phrase)
    
    return fresh_phrases[:num_phrases]


# ============== AUDIO GENERATION ==============

async def generate_single_audio(text: str, voice: str, output_path: str):
    """Generate audio using Edge TTS"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


def generate_all_audio(phrases: list, output_dir: str):
    """Generate audio for all phrases with proper timing"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, phrase in enumerate(phrases):
        english_file = output_dir / f"english_{i}.mp3"
        spanish_file = output_dir / f"spanish_{i}.mp3"
        combined_file = output_dir / f"combined_{i}.mp3"

        print(f"\n  Phrase {i+1}:")
        print(f"    EN: {phrase['english']}")
        print(f"    ES: {phrase['spanish']}")

        # Generate English audio
        en_success = asyncio.run(generate_single_audio(phrase["english"], ENGLISH_VOICE, str(english_file)))
        if en_success:
            print(f"    ✓ English: {english_file.name}")
        else:
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(english_file)]
            subprocess.run(cmd, capture_output=True)

        # Generate Spanish audio
        es_success = asyncio.run(generate_single_audio(phrase["spanish"], SPANISH_VOICE, str(spanish_file)))
        if es_success:
            print(f"    ✓ Spanish: {spanish_file.name}")
        else:
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(spanish_file)]
            subprocess.run(cmd, capture_output=True)

        # Get ACTUAL durations
        en_duration = get_audio_duration(str(english_file))
        es_duration = get_audio_duration(str(spanish_file))

        # Add pause between English and Spanish
        pause_between = 0.5
        total_duration = en_duration + pause_between + es_duration

        print(f"    ⏱️  Total: {total_duration:.2f}s (EN: {en_duration:.2f}s + pause: {pause_between}s + ES: {es_duration:.2f}s)")

        # Combine audio files
        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(spanish_file),
            "-filter_complex", f"[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            concat_file = output_dir / f"concat_{i}.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                f.write(f"file '{english_file.as_posix()}'\n")
                f.write(f"file '{spanish_file.as_posix()}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:a", "aac",
                str(combined_file)
            ]
            subprocess.run(cmd, capture_output=True)
            if concat_file.exists():
                concat_file.unlink()

        actual_duration = get_audio_duration(str(combined_file))
        print(f"    ✓ Combined verified: {actual_duration:.2f}s")

        audio_files.append({
            "index": i,
            "english": str(english_file),
            "spanish": str(spanish_file),
            "combined": str(combined_file),
            "duration": actual_duration,
            "en_duration": en_duration,
            "es_duration": es_duration
        })

    print(f"\n[audio] ✓ Generated {len(audio_files)} phrase audios")
    return audio_files


def get_audio_duration(audio_file: str) -> float:
    """Get audio duration in seconds"""
    if not Path(audio_file).exists():
        return 2.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0


def create_final_narration(audio_files: list, output_file: str):
    """Combine all audio files"""
    n = len(audio_files)
    print(f"[audio] Combining {n} audio files...")

    concat_file = Path(output_file).parent / "narration_list.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for audio_info in audio_files:
            combined_path = Path(audio_info["combined"])
            if combined_path.exists():
                path_str = str(combined_path.resolve()).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "copy", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if concat_file.exists():
        concat_file.unlink()

    if result.returncode == 0 and Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        size = Path(output_file).stat().st_size
        print(f"\n[audio] ✓ Final narration: {Path(output_file).name} ({size/1024:.1f} KB)")
        return True

    return False


# ============== IMAGE GENERATION ==============

def create_impressive_background(category_english: str):
    """Create stunning gradient background with geometric patterns and glow"""
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    # HIGH CONTRAST gradients for ALL 25 categories (very different colors like Motivation)
    category_colors = {
        "Motivation": [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)],  # Purple → Dark Purple → Pink → Light Purple
        "Love": [(255, 0, 100), (139, 0, 0), (255, 105, 180), (255, 192, 203)],  # Red → Dark Red → Hot Pink → Pink
        "Success": [(255, 215, 0), (0, 100, 0), (255, 140, 0), (34, 139, 34)],  # Gold → Dark Green → Orange → Forest Green
        "Wisdom": [(0, 0, 139), (255, 215, 0), (70, 130, 180), (255, 255, 0)],  # Dark Blue → Gold → Steel Blue → Yellow
        "Happiness": [(255, 255, 0), (255, 0, 255), (255, 165, 0), (147, 112, 219)],  # Yellow → Magenta → Orange → Purple
        "Self Improvement": [(0, 128, 0), (255, 215, 0), (0, 255, 0), (255, 140, 0)],  # Green → Gold → Lime → Orange
        "Gratitude": [(255, 127, 80), (75, 0, 130), (255, 160, 122), (138, 43, 226)],  # Coral → Dark Purple → Light Salmon → Blue Violet
        "Friendship": [(255, 192, 203), (0, 100, 80), (255, 105, 180), (0, 200, 160)],  # Pink → Dark Teal → Hot Pink → Medium Teal
        "Hope": [(0, 0, 100), (255, 255, 0), (70, 130, 180), (255, 215, 0)],  # Dark Blue → Yellow → Steel Blue → Gold
        "Creativity": [(255, 0, 127), (0, 0, 139), (255, 20, 147), (75, 0, 130)],  # Deep Pink → Dark Blue → Deep Pink → Dark Purple
        "Inner Peace": [(135, 206, 235), (0, 0, 100), (176, 224, 230), (75, 0, 130)],  # Sky Blue → Dark Blue → Powder Blue → Dark Purple
        "Confidence": [(255, 69, 0), (0, 0, 139), (255, 140, 0), (70, 130, 180)],  # Red Orange → Dark Blue → Orange → Steel Blue
        "Perseverance": [(139, 69, 19), (255, 215, 0), (160, 82, 45), (255, 140, 0)],  # Saddle Brown → Gold → Sienna → Orange
        "Inspiration": [(255, 0, 255), (75, 0, 130), (255, 20, 147), (0, 0, 139)],  # Magenta → Dark Purple → Deep Pink → Dark Blue
        "Positive Life": [(50, 205, 50), (255, 0, 127), (144, 238, 144), (255, 20, 147)],  # Lime Green → Deep Pink → Light Green → Deep Pink
        "Courage": [(178, 34, 34), (255, 215, 0), (220, 20, 60), (255, 140, 0)],  # Firebrick → Gold → Crimson → Orange
        "Kindness": [(255, 182, 193), (138, 43, 226), (255, 160, 122), (75, 0, 130)],  # Light Salmon → Dark Purple → Light Salmon → Dark Purple
        "Patience": [(34, 139, 34), (255, 255, 0), (60, 179, 113), (255, 215, 0)],  # Forest Green → Yellow → Medium Sea Green → Gold
        "Forgiveness": [(230, 230, 250), (75, 0, 130), (216, 191, 216), (138, 43, 226)],  # Lavender → Dark Purple → Thistle → Blue Violet
        "Strength": [(100, 100, 100), (255, 69, 0), (150, 150, 150), (255, 140, 0)],  # Gray → Red Orange → Light Gray → Orange
        "Joy": [(255, 255, 0), (255, 0, 127), (255, 215, 0), (147, 112, 219)],  # Yellow → Deep Pink → Gold → Purple
        "Balance": [(60, 179, 113), (138, 43, 226), (152, 251, 152), (75, 0, 130)],  # Medium Sea Green → Dark Purple → Pale Green → Dark Purple
        "Growth": [(0, 100, 0), (255, 215, 0), (34, 139, 34), (255, 140, 0)],  # Dark Green → Gold → Forest Green → Orange
        "Purpose": [(75, 0, 130), (255, 215, 0), (138, 43, 226), (255, 140, 0)],  # Dark Purple → Gold → Blue Violet → Orange
        "Mindfulness": [(210, 180, 140), (75, 0, 130), (245, 245, 220), (138, 43, 226)],  # Tan → Dark Purple → Beige → Blue Violet
    }

    colors = category_colors.get(category_english, [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)])

    # Create smooth multi-stop gradient
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.33:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * (ratio * 3))
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * (ratio * 3))
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * (ratio * 3))
        elif ratio < 0.66:
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ((ratio - 0.33) * 3))
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ((ratio - 0.33) * 3))
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ((ratio - 0.33) * 3))
        else:
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * ((ratio - 0.66) * 3))
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * ((ratio - 0.66) * 3))
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * ((ratio - 0.66) * 3))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))

    # Add subtle geometric pattern for depth (MUCH SMALLER circles)
    for i in range(0, VIDEO_WIDTH, 60):
        for j in range(0, VIDEO_HEIGHT, 60):
            draw.ellipse(
                [(i + 45, j + 45), (i + 55, j + 55)],
                outline=(255, 255, 255, 15),
                width=1
            )

    # Add radial glow effect from center
    glow = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for radius in range(800, 0, -50):
        alpha = int(30 * (1 - radius / 800))
        glow_draw.ellipse(
            [(VIDEO_WIDTH//2 - radius, VIDEO_HEIGHT//3 - radius),
             (VIDEO_WIDTH//2 + radius, VIDEO_HEIGHT//3 + radius)],
            fill=(255, 255, 255, alpha)
        )

    # Composite glow over background
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glow)

    return img


def generate_complete_image(phrase_data: dict, category_english: str, output_path: str):
    """Generate image with impressive background"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL not available. Install: pip install Pillow")
        return None

    img = create_impressive_background(category_english)
    draw = ImageDraw.Draw(img)

    # Load fonts - Optimized for mobile viewing (INCREASED sizes)
    # Using Linux-native fonts (pre-installed on GitHub Actions)
    font_category = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)  # Increased from 48
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)     # Increased from 64
    font_pronunciation = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)   # Increased from 32
    font_branding = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)   # Increased from 40
    
    english = phrase_data.get("english", "")
    spanish = phrase_data.get("spanish", "")
    pronunciation = phrase_data.get("pronunciation", "")

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    # Category at top
    category_text = category_english.upper()
    category_bbox = draw.textbbox((VIDEO_WIDTH // 2, 140), category_text, font=font_category, anchor="mm")
    padding = 25
    draw.rectangle(
        [(category_bbox[0] - padding, category_bbox[1] - padding),
         (category_bbox[2] + padding, category_bbox[3] + padding)],
        fill=(0, 0, 0, 200)
    )
    draw.text(
        (VIDEO_WIDTH // 2, 140),
        category_text,
        fill=(255, 255, 255),
        font=font_category,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    # English text
    english_y = 470  # Adjusted for larger fonts
    english_lines = wrap_text(english, font_large, VIDEO_WIDTH - 140)
    total_height = len(english_lines) * 95  # Increased from 75 for larger fonts

    draw.rectangle(
        [(60, english_y - 55), (VIDEO_WIDTH - 60, english_y + total_height + 15)],
        fill=(20, 30, 80, 220)
    )

    for i, line in enumerate(english_lines):
        y_pos = english_y + (i * 95)  # Increased spacing
        draw.text(
            (VIDEO_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 255),
            font=font_large,
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

    # Spanish text
    spanish_y = english_y + total_height + 110  # Increased from 100
    spanish_lines = wrap_text(spanish, font_large, VIDEO_WIDTH - 140)
    total_height = len(spanish_lines) * 95  # Increased from 75

    draw.rectangle(
        [(60, spanish_y - 55), (VIDEO_WIDTH - 60, spanish_y + total_height + 15)],
        fill=(80, 30, 30, 220)
    )

    for i, line in enumerate(spanish_lines):
        y_pos = spanish_y + (i * 95)  # Increased spacing
        draw.text(
            (VIDEO_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 0),
            font=font_large,
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

    # Pronunciation with FILLED BOX
    pronunciation_y = spanish_y + total_height + 90  # Increased from 80
    pronunciation_text = f"[{pronunciation}]"
    pron_lines = wrap_text(pronunciation_text, font_pronunciation, VIDEO_WIDTH - 160)

    if pron_lines:
        pron_total_height = len(pron_lines) * 42  # Increased from 35 for larger font
        draw.rectangle(
            [(70, pronunciation_y - 20), (VIDEO_WIDTH - 70, pronunciation_y + pron_total_height + 10)],
            fill=(40, 40, 40, 230)
        )

        for i, pron_line in enumerate(pron_lines):
            y_pos = pronunciation_y + (i * 42)  # Increased spacing
            draw.text(
                (VIDEO_WIDTH // 2, y_pos),
                pron_line,
                fill=(240, 240, 240),
                font=font_pronunciation,
                anchor="mm",
                stroke_width=1,
                stroke_fill=(20, 20, 20, 200)
            )

    # Branding
    branding_y = VIDEO_HEIGHT - 100
    draw.rectangle(
        [(0, branding_y - 30), (VIDEO_WIDTH, branding_y + 50)],
        fill=(0, 0, 0, 180)
    )
    draw.text(
        (VIDEO_WIDTH // 2, branding_y),
        "VELOCITY SPANISH",
        fill=(255, 255, 255),
        font=font_branding,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    print(f"  ✓ Image: {Path(output_path).name}")
    return output_path


# ============== VIDEO CREATION ==============

def create_video_from_images_audio(image_files: list, audio_files: list, combined_audio: str, output_file: str):
    """Create video from images and audio with PERFECT synchronization"""

    print(f"\n[video] Creating video from {len(image_files)} images...")
    print(f"[video] Ensuring complete audio playback and sync...")

    temp_clips = []

    for i, (img_path, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']
        print(f"  Image {i+1}/{len(image_files)}: {duration:.2f}s (EN: {audio_info.get('en_duration', 0):.1f}s + ES: {audio_info.get('es_duration', 0):.1f}s)")

        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    # Concatenate clips
    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    concat_file = Path(output_file).parent / "concat_list.txt"

    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(temp_video)]
    subprocess.run(cmd, check=True, capture_output=True)

    # Add audio
    print("[video] Adding audio (ensuring complete playback)...")
    audio_duration = get_audio_duration(combined_audio)
    print(f"[video] Audio duration: {audio_duration:.2f}s")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(combined_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Verify
    video_duration = get_audio_duration(str(output_file).replace(".mp4", ".mp4"))
    print(f"[video] ✓ Video created: {Path(output_file).name} ({video_duration:.2f}s)")

    # Cleanup
    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()


# ============== MAIN WORKFLOW ==============

def generate_reel(category_english: str = None):
    """Generate complete Facebook Reel"""

    if not category_english:
        category_english = random.choice(CATEGORIES_ENGLISH)

    print(f"\n{'='*80}")
    print(f"Category: {category_english} ({CATEGORIES_SPANISH[category_english]})")
    print(f"{'='*80}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reel_dir = VIDEO_DIR / f"{category_english}_{timestamp}"
    reel_dir.mkdir(exist_ok=True)

    # Step 1: Generate unique phrases
    print("[1/4] Generating unique phrases (checking history)...")
    phrases = generate_phrases(category_english, num_phrases=5)

    for i, phrase in enumerate(phrases, 1):
        print(f"  {i}. {phrase['english']} → {phrase['spanish']}")

    # Step 2: Generate images
    print("\n[2/4] Generating images with impressive backgrounds...")
    for i, phrase in enumerate(phrases):
        output_path = reel_dir / f"phrase_{i:02d}.jpg"
        generate_complete_image(phrase, category_english, str(output_path))
        print(f"  ✓ Image {i+1}: {phrase['english'][:40]}...")

    # Step 3: Generate audio
    print("\n[3/4] Generating audio (English + Spanish with 500ms pause)...")
    audio_files = generate_all_audio(phrases, str(reel_dir))

    final_audio = reel_dir / "narration.mp3"
    create_final_narration(audio_files, str(final_audio))

    # Step 4: Create video - CRITICAL: Sort images for correct order
    print("\n[4/4] Creating video...")
    output_video = reel_dir / "final_reel.mp4"
    
    image_files = sorted([str(p) for p in reel_dir.glob("phrase_*.jpg")])
    
    create_video_from_images_audio(
        image_files,
        audio_files,
        str(final_audio),
        str(output_video)
    )

    # Save metadata
    metadata = {
        "category_english": category_english,
        "category_spanish": CATEGORIES_SPANISH[category_english],
        "timestamp": timestamp,
        "phrases": phrases,
        "video": str(output_video),
        "audio": str(final_audio)
    }

    with open(reel_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ REEL COMPLETE!")
    print(f"  📁 {reel_dir}")
    print(f"  🎬 {output_video.name}")
    print(f"  🏷️  Branding: Velocity Spanish")
    print(f"{'='*80}\n")

    return metadata


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🇪🇸 VELOCITY SPANISH - FACEBOOK REELS AUTOMATION 🇪🇸")
    print("="*80)
    print("\n✨ IMPROVED FEATURES:")
    print("  ✓ Natural pauses with commas (non-robotic TTS)")
    print("  ✓ Perfect audio-video synchronization")
    print("  ✓ Complete audio playback guaranteed")
    print("  ✓ English category names (for American/European learners)")
    print("  ✓ Velocity Spanish branding at bottom")
    print("  ✓ NEVER repeats phrases (permanent history tracking)")
    
    # Show history status
    print(f"\n📚 PHRASE HISTORY STATUS:")
    history = load_phrase_history()
    phrase_count = len(history.get("used_english", []))
    print(f"  • Total unique phrases in history: {phrase_count}")
    if phrase_count > 0:
        print(f"  • Last 5 used phrases: {history['used_english'][-5:]}")
    
    print(f"\n📊 AVAILABLE CATEGORIES ({len(CATEGORIES_ENGLISH)} total):")
    for i, cat in enumerate(CATEGORIES_ENGLISH, 1):
        print(f"   {i:2d}. {cat} ({CATEGORIES_SPANISH[cat]})")
    print(f"\n📅 DAILY CAPACITY:")
    print(f"  • 7 reels per day = 35 unique phrases daily")
    print(f"  • {len(CATEGORIES_ENGLISH)} categories = Over 3 days before any category repeats")
    print(f"  • Phrase history is PERMANENT (never deletes)")
    print(f"  • AI generates FRESH phrases every time")
    print("="*80)

    generate_reel()

    print("\n" + "="*80)
    print("✅ READY FOR DAILY AUTOMATION!")
    print("="*80)
    print("\nTo generate 4 reels for today:")
    print("  from facebook_reels_automation import generate_daily_content")
    print("  generate_daily_content(times_per_day=4)")
    print("\nTo generate a single reel:")
    print("  generate_reel('Love')  # Or any category from the list above")
    print("="*80)
