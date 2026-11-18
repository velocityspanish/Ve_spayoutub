"""VELOCITY JAPANESE - language pack, brand and motion design constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_DIR = BASE_DIR / "output"
LESSONS_DIR = OUTPUT_DIR / "lessons"
HISTORY_DIR = OUTPUT_DIR / "history"
SCENE_DIR = BASE_DIR / "scene"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# ---------------------------------------------------------------- brand

BRAND = "VELOCITY SPANISH"
BRAND_LOCKUP_TOP = "VELOCITY"
BRAND_LOCKUP_BOTTOM = "SPANISH"
HANDLE = "@velocityspanish"
MASCOT_NAME = "Velo"

# ==== LANGUAGE PACK START ====
LANGUAGE = {
    "code": "es",
    "name": "Spanish",
    "native_name": "Español",
    "history_key": "spanish",
    "english_voice": "en-US-AvaNeural",
    "english_fallback_voice": "en-US-GuyNeural",
    "native_voice": "es-ES-ElviraNeural",
    "native_fallback_voice": "es-ES-AlvaroNeural",
    "native_engine": "edge",
    "native_lang_code": "es",
    "english_rate": "-4%",
    "native_rate": "-10%",
    "english_pitch": "+0Hz",
    "native_pitch": "+0Hz",
    "native_label": "ESPAÑOL",
    "translit_label": "SAY IT LIKE",
    "flag": "es",
    "greeting": "¡Hola!",
    "encouragement": "¡Genial!",
    "rtl": False,
    "char_tiles": False,
    "script_font": "",
    "glyphs": "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑáéíóúüñ",
}
# ==== LANGUAGE PACK END ====

AI_MODEL = os.getenv("AI_MODEL", "gemini-fast")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# ---------------------------------------------------------------- timing (seconds)

INTRO_DURATION = 4.0
OUTRO_DURATION = 5.2
EN_CARD_IN = 0.55
GAP_EN_NATIVE = 0.5
NATIVE_CARD_LEAD = 0.35
GAP_BEFORE_REPEAT = 0.8
TAIL_HOLD = 1.4
MAX_REEL_DURATION = 88.0

# ---------------------------------------------------------------- palette

INK = "#3C3C3C"
MUTED = "#8A8A8A"
CREAM = "#FFF8E7"
GREEN = "#58CC02"
GREEN_DARK = "#46A302"
GREEN_DEEP = "#3D8F00"
BLUE = "#1CB0F6"
PURPLE = "#A560E8"
ORANGE = "#FF7A00"
RED = "#FF4B4B"
YELLOW = "#F5A700"
TEAL = "#00A889"
PINK = "#E056A0"

PALETTE = [GREEN, BLUE, PURPLE, ORANGE, RED, YELLOW, TEAL, PINK]

# ---------------------------------------------------------------- categories
# (english, native, icon, accent)

# ==== CATEGORY TABLE START ====
CATEGORY_TABLE = [
    ("Greetings", "Saludos", "hand", "#1CB0F6"),
    ("Basic Phrases", "Frases básicas", "chat", "#58CC02"),
    ("Common Expressions", "Expresiones comunes", "chat", "#1CB0F6"),
    ("Travel", "Viajes", "plane", "#1CB0F6"),
    ("Restaurant", "Restaurante", "fork", "#FF7A00"),
    ("Shopping", "Compras", "bag", "#E056A0"),
    ("Emergency", "Emergencias", "siren", "#FF4B4B"),
    ("Family Terms", "Familia", "heart", "#E056A0"),
    ("Numbers", "Números", "hash", "#A560E8"),
    ("Time", "Tiempo", "clock", "#00A889"),
    ("Motivation", "Motivación", "rocket", "#A560E8"),
    ("Love", "Amor", "heart", "#FF4B4B"),
    ("Success", "Éxito", "trophy", "#F5A700"),
    ("Wisdom", "Sabiduría", "book", "#A560E8"),
    ("Happiness", "Felicidad", "smile", "#F5A700"),
    ("Self Improvement", "Superación personal", "leaf", "#58CC02"),
    ("Gratitude", "Gratitud", "heart", "#FF7A00"),
    ("Friendship", "Amistad", "users", "#00A889"),
    ("Hope", "Esperanza", "sun", "#FF7A00"),
    ("Creativity", "Creatividad", "palette", "#E056A0"),
    ("Inner Peace", "Paz interior", "lotus", "#00A889"),
    ("Confidence", "Confianza", "shield", "#1CB0F6"),
    ("Perseverance", "Perseverancia", "mountain", "#FF7A00"),
    ("Inspiration", "Inspiración", "sparkles", "#A560E8"),
    ("Positive Life", "Vida positiva", "sun", "#58CC02"),
    ("Courage", "Coraje", "shield", "#FF4B4B"),
    ("Kindness", "Amabilidad", "heart", "#E056A0"),
    ("Patience", "Paciencia", "hourglass", "#00A889"),
    ("Forgiveness", "Perdón", "hands", "#FF7A00"),
    ("Strength", "Fuerza", "dumbbell", "#FF4B4B"),
    ("Joy", "Alegría", "smile", "#F5A700"),
    ("Balance", "Equilibrio", "scale", "#00A889"),
    ("Growth", "Crecimiento", "sprout", "#58CC02"),
    ("Purpose", "Propósito", "target", "#A560E8"),
    ("Mindfulness", "Atención plena", "lotus", "#00A889"),
    ("Daily Routine", "Rutina diaria", "calendar", "#1CB0F6"),
    ("Weather", "Clima", "cloud", "#1CB0F6"),
    ("Feelings", "Sentimientos", "smile", "#E056A0"),
    ("Food", "Comida", "fork", "#FF7A00"),
    ("Health", "Salud", "heart", "#58CC02"),
    ("Work", "Trabajo", "briefcase", "#1CB0F6"),
    ("Technology", "Tecnología", "chip", "#A560E8"),
    ("Nature", "Naturaleza", "leaf", "#58CC02"),
    ("Animals", "Animales", "paw", "#FF7A00"),
    ("Colors", "Colores", "palette", "#E056A0"),
    ("Directions", "Direcciones", "compass", "#1CB0F6"),
    ("Body Parts", "Partes del cuerpo", "hand", "#00A889"),
    ("Clothes", "Ropa", "shirt", "#E056A0"),
    ("Music", "Música", "music", "#A560E8"),
    ("Sports", "Deportes", "ball", "#FF7A00"),
    ("Holidays", "Vacaciones", "gift", "#FF4B4B"),
    ("Education", "Educación", "book", "#1CB0F6"),
    ("Culture", "Cultura", "globe", "#00A889"),
    ("Finance", "Finanzas", "coin", "#58CC02"),
    ("Relationships", "Relaciones", "users", "#E056A0"),
]
# ==== CATEGORY TABLE END ====

CATEGORIES = [c[0] for c in CATEGORY_TABLE]
CATEGORIES_NATIVE = {c[0]: c[1] for c in CATEGORY_TABLE}
CATEGORY_META = {c[0]: {"native": c[1], "icon": c[2], "accent": c[3]} for c in CATEGORY_TABLE}
MAX_RECENT_CATEGORIES = 25

# ==== HASHTAGS START ====
HASHTAGS = [
    "#learnspanish",
    "#spanishlessons",
    "#spanishforbeginners",
    "#languagelearning",
    "#spanishvocabulary",
    "#velocityspanish",
    "#dailyspanish",
    "#spanish",
    "#learnlanguages",
    "#speakspanish",
    "#bilingual",
    "#languagetips",
]
# ==== HASHTAGS END ====
