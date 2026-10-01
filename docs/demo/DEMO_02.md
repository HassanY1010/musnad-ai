# LIVE DEMO 02 — Authentic Canonical Hadith

**Scenario Title:** Verifying Foundational Prophetic Narration  
**Purpose:** Demonstrate exact hadith retrieval, book/chapter/number traceability, narrator chain tracking, and authenticity grading verification.

---

### Exact Input
```arabic
قال رسول الله صلى الله عليه وسلم: إنما الأعمال بالنيات وإنما لكل امرئ ما نوى
```

### Expected Behavior
- **Claim Extraction:** Classified as `hadith`.
- **Normalization:** Strips sanad prefix (`قال رسول الله صلى الله عليه وسلم:`).
- **Retrieval Match:** Exact match against Sahih al-Bukhari #1.
- **Status:** `supported`.
- **Match Type:** `exact`.

### Actual Verified System Result
- **Classification:** `hadith`
- **Retrieved Source:** `SRC-002` — صحيح البخاري (كتاب بدء الوحي، حديث رقم 1)
- **Primary Narrator:** عمر بن الخطاب رضي الله عنه
- **Authenticity Grading:** صحيح (البخاري ومسلم)
- **Status:** `supported`
- **Explanation:** `تم التحقق من الحديث الشريف بمطابقة تامة في صحيح البخاري - رقم 1 (الحكم: صحيح).`

### Why This Result Matters
Distinguishes between a text merely existing in a book and being authenticated by classical Hadith scholarship.

### Possible Judge Question
*"Does MUSNAD assume a hadith is authentic just because it is found in a database?"*

### Recommended Answer
*"No. MUSNAD strictly separates textual presence from authenticity grading. Every hadith must have an explicit grading authority record in the metadata. If grading is absent, the system explicitly reports that grading is unavailable rather than inferring it."*
