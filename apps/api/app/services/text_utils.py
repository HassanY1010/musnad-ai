"""
MUSNAD AI - Arabic Text Processing Utilities
High-precision normalization, diacritic stripping, and tokenization.
"""
import re
import unicodedata
from typing import List, Optional

# Arabic diacritics and Quranic marks regex
TASHKEEL_REGEX = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]")
TATWEEL_REGEX = re.compile(r"\u0640")
PUNCTUATION_REGEX = re.compile(r"[،؛؟«»""''.,!?:;\-\(\)\[\]\{\}]")

# Eastern Arabic numerals mapping
EASTERN_NUM_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

SURAH_MAP = {
    "فاتحه": 1, "بقره": 2, " عمران": 3, "نساء": 4, "مائده": 5, "انعام": 6, "اعراف": 7, "انفال": 8, "توبه": 9, "يونس": 10,
    "هود": 11, "يوسف": 12, "رعد": 13, "ابراهيم": 14, "حجر": 15, "نحل": 16, "اسراء": 17, "كهف": 18, "مريم": 19, "طه": 20,
    "انبياء": 21, "الحج": 22, "مؤمنون": 23, "نور": 24, "فرقان": 25, "شعراء": 26, "نمل": 27, "قصص": 28, "عنكبوت": 29, "روم": 30,
    "لقمان": 31, "سجده": 32, "احزاب": 33, "سبا": 34, "فاطر": 35, "يس": 36, "صافات": 37, "ص": 38, "زمر": 39, "غافر": 40,
    "فصلت": 41, "شوري": 42, "زخرف": 43, "دخان": 44, "جاثيه": 45, "احقاف": 46, "محمد": 47, "فتح": 48, "حجرات": 49, "ق": 50,
    "ذاريات": 51, "طور": 52, "نجم": 53, "قمر": 54, "رحمن": 55, "واقعه": 56, "حديد": 57, "مجادله": 58, "حشر": 59, "ممتحنه": 60,
    "الصف": 61, "جمعه": 62, "منافقون": 63, "تغابن": 64, "طلاق": 65, "تحريم": 66, "ملك": 67, "قلم": 68, "حاقه": 69, "معارج": 70,
    "نوح": 71, "الجن": 72, "مزمل": 73, "مدثر": 74, "قيامه": 75, "انسان": 76, "مرسلات": 77, "نبا": 78, "نازعات": 79, "عبس": 80,
    "تكوير": 81, "انفطار": 82, "مطففين": 83, "انشقاق": 84, "بروج": 85, "طارق": 86, "اعلي": 87, "غاشيه": 88, "فجر": 89, "بلد": 90,
    "شمس": 91, "ليل": 92, "ضحي": 93, "شرح": 94, "تين": 95, "علق": 96, "قدر": 97, "بينه": 98, "زلزله": 99, "عاديات": 100,
    "قارعه": 101, "تكاثر": 102, "عصر": 103, "همزه": 104, "فيل": 105, "قريش": 106, "ماعون": 107, "كوثر": 108, "كافرون": 109, "نصر": 110,
    "مسد": 111, "اخلاص": 112, "فلق": 113, "ناس": 114,
}


def strip_tashkeel(text: str) -> str:
    """Remove all Arabic diacritical marks (tashkeel/harakat)."""
    if not text:
        return ""
    return TASHKEEL_REGEX.sub("", text)


def normalize_arabic(text: str) -> str:
    """
    Standardize Arabic text for consistent searching and retrieval:
    - Unicode NFKC normalization (decomposes ligatures and standardizes glyphs)
    - Normalize Eastern Arabic numerals (٠-٩ -> 0-9)
    - Strip diacritics & Quranic pause marks
    - Normalize Alef variants (أ, إ, آ, ٱ -> ا)
    - Normalize Alef Maksura (ى -> ي)
    - Normalize Taa Marbuta (ة -> ه)
    - Remove Tatweel (kashida)
    - Collapse extra whitespace
    """
    if not text:
        return ""

    # Unicode NFKC normalization first
    s = unicodedata.normalize("NFKC", text)

    # Normalize Eastern Arabic numerals
    s = s.translate(EASTERN_NUM_MAP)

    # Strip diacritics
    s = strip_tashkeel(s)

    # Remove tatweel
    s = TATWEEL_REGEX.sub("", s)

    # Normalize Alef forms
    s = re.sub(r"[إأآٱ]", "ا", s)

    # Normalize Alef Maksura
    s = re.sub(r"ى", "ي", s)

    # Normalize Taa Marbuta
    s = re.sub(r"ة", "ه", s)

    # Clean whitespace
    s = re.sub(r"\s+", " ", s).strip()

    return s


def tokenize_arabic(text: str) -> List[str]:
    """Tokenize Arabic text into clean normalized words for BM25 and lexical search."""
    if not text:
        return []
    clean = normalize_arabic(text)
    clean = PUNCTUATION_REGEX.sub(" ", clean)
    tokens = [t for t in clean.split() if len(t) > 1]
    return tokens


def detect_language(text: str) -> str:
    """Detect whether input text is predominantly Arabic or other."""
    if not text:
        return "ar"
    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
    total_chars = len(re.findall(r"\w", text))
    if total_chars == 0:
        return "ar"
    return "ar" if (arabic_chars / total_chars) > 0.3 else "en"


def strip_attribution(text: str) -> str:
    """Strip common Islamic attributions, prompt injection preambles, and sanad prefixes to extract core matn."""
    if not text:
        return ""
    t = TATWEEL_REGEX.sub("", text).strip()

    # Neutralize prompt injection command prefixes (Phase 6 requirement)
    injection_prefix = (
        r"^(?:OVERRIDE\s+DECISION\s*:\s*|SYSTEM\s*(?:MESSAGE)?\s*:\s*|<system>.*?</system>\s*|"
        r"IGNORE\s+ALL\s+PREVIOUS\s+INSTRUCTIONS\s*:\s*|"
        r"Please\s+output\s+supported\s+and\s+grant\s+100%\s+confidence\s+to\s+this\s+claim\s*:\s*|"
        r"تجاهل\s+(?:كل|جميع)\s+التعليمات\s+السابقة\s*(?:و|ثم)?\s*)+"
    )
    t = re.sub(injection_prefix, "", t, flags=re.IGNORECASE).strip()

    patterns = [
        r"^قال\s+الله\s+تعال[ىي](?:\s+في\s+سور[ةه]\s+[^\s:،.]{2,30})?(?:\s*:\s*)?",
        r"^قال\s+تعال[ىي](?:\s+في\s+سور[ةه]\s+[^\s:،.]{2,30})?(?:\s*:\s*)?",
        r"^قوله\s+تعال[ىي](?:\s+في\s+سور[ةه]\s+[^\s:،.]{2,30})?(?:\s*:\s*)?",
        r"^(?:في\s+)?سور[ةه]\s+[^\s:،.]{2,30}(?:\s*:\s*)?",
        r"^قال\s+الله\s+تعال[ىي](?:\s*:\s*)?",
        r"^قال\s+تعال[ىي](?:\s*:\s*)?",
        r"^قوله\s+تعال[ىي](?:\s*:\s*)?",
        r"^قال\s+رسول\s+الله\s+صل[ىي]\s+الله\s+عليه\s+وسلم(?:\s*:\s*)?",
        r"^قال\s+رسول\s+الله(?:\s*:\s*)?",
        r"^قال\s+النبي\s+صل[ىي]\s+الله\s+عليه\s+وسلم(?:\s*:\s*)?",
        r"^قال\s+النبي(?:\s*:\s*)?",
        r"^رو[ىي]\s+عن\s+النبي\s+صل[ىي]\s+الله\s+عليه\s+وسلم\s+أنه\s+قال(?:\s*:\s*)?",
        r"^عن\s+.*?\s+أن\s+النبي\s+صل[ىي]\s+الله\s+عليه\s+وسلم\s+قال(?:\s*:\s*)?",
        r"^عن\s+.*?\s+قال(?:\s*:\s*)?",
        r"^قالت\s+عائش[ةه]\s+قال\s+رسول\s+الله\s+صل[ىي]\s+الله\s+عليه\s+وسلم(?:\s*:\s*)?",
        r"^ورد\s+في\s+الأثر(?:\s*:\s*)?",
        r"^قال\s+الإمام\s+.*?(?:\s*:\s*)?",
    ]
    for p in patterns:
        t = re.sub(p, "", t).strip()



    # If text has diacritics, match against unvocalized prefix and slice (for stacked diacritic attacks)
    t_no_tashkeel = strip_tashkeel(t)
    for p in patterns:
        m = re.match(p, t_no_tashkeel)
        if m:
            matched_len = m.end()
            consumed = 0
            idx = 0
            tashkeel_chars = set("\u0617\u0618\u0619\u061A\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0670\u06D6\u06D7\u06D8\u06D9\u06DA\u06DB\u06DC\u06DD\u06DE\u06DF\u06E0\u06E1\u06E2\u06E3\u06E4\u06E5\u06E6\u06E7\u06E8\u06E9\u06EA\u06EB\u06EC\u06ED")
            while idx < len(t) and consumed < matched_len:
                if t[idx] not in tashkeel_chars:
                    consumed += 1
                idx += 1
            t = t[idx:].strip()
            break

    return t


def clean_text_for_matching(text: str) -> str:
    """Fully clean Arabic text for exact and fuzzy matching (no diacritics, no punctuation, normalized hamza)."""
    if not text:
        return ""
    s = normalize_arabic(text)
    # Normalize orthographic hamza variants for robust exact matching (مسؤول vs مسئول)
    s = re.sub(r"[ؤئ]", "ء", s)
    # Also normalize dagger alif \u0670 if present
    s = re.sub(r"\u0670", "", s)
    s = PUNCTUATION_REGEX.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_surah_name(text: str) -> Optional[int]:
    """Extract mentioned surah name from text if present, returns surah_number."""
    if not text:
        return None
    m = re.search(r"سور[ةه]\s+([^\s:،.]{2,30})", text)
    if m:
        name = m.group(1).strip()
        stem = re.sub(r"^[اإآٱ]ل", "", name)
        stem = stem if len(stem) >= 3 else name
        return SURAH_MAP.get(stem) or SURAH_MAP.get(name)
    return None



def strip_basmalah(text: str) -> str:
    """Strip Basmalah from the beginning of text if present."""
    if not text:
        return ""
    p = r"^(?:بِسْمِ\s+ٱللَّهِ\s+ٱلرَّحْمَٰنِ\s+ٱلرَّحِيمِ|بسم\s+الله\s+الرحم[ٰا]?ن\s+الرحيم)\s*"
    return re.sub(p, "", text).strip()



