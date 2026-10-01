# LIVE DEMO 01 — Exact Quran Quotation

**Scenario Title:** Verifying Canonical Quranic Text  
**Purpose:** Demonstrate exact Uthmanic Quran retrieval, coordinate attribution, and deterministic `supported` status.

---

### Exact Input
```arabic
قَالَ اللَّهُ تَعَالَىٰ: قُلْ هُوَ اللَّهُ أَحَدٌ
```

### Expected Behavior
- **Claim Extraction:** Classified as `quran_verse`.
- **Normalization:** Strips diacritics and tatweel; normalizes Hamzas.
- **Retrieval Match:** Exact match against Surah Al-Ikhlas (Ayah 1).
- **Status:** `supported`.
- **Match Type:** `exact`.

### Actual Verified System Result
- **Classification:** `quran_verse`
- **Retrieved Source:** `quran_112_001` — القرآن الكريم (مصحف المدينة)
- **Coordinates:** سورة الإخلاص - آية 1
- **Status:** `supported` (100% confidence)
- **Explanation:** `تم التحقق بنجاح من نص الآية الكريمة بمطابقة تامة مع المصحف الشريف (سورة الإخلاص - آية 1).`

### Why This Result Matters
Demonstrates that sacred divine text is anchored to an immutable reference, with canonical surah and ayah coordinates.

### Possible Judge Question
*"What if someone enters a verse with different diacritics or non-standard calligraphy?"*

### Recommended Answer
*"The Arabic text normalization layer decomposes Unicode ligatures (NFKC), normalizes alef and hamza variants, and strips decorative tashkeel, ensuring the canonical text is identified while preserving the user's raw input unaltered for auditing."*
