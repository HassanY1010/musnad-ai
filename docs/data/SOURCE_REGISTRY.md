# MUSNAD AI — FORMAL SOURCE REGISTRY
**Canonical Islamic Knowledge Sources Catalog**  
**Dataset Version**: KB-002 (Audited & Expanded Corpus)  
**Total Registered Sources**: 7 Corpora (15,426 Verified Records)  
**Date**: September 2026  
**Auditor**: Lead Knowledge & Provenance Engineer, MUSNAD AI  

---

## 1. Registry Architecture & Verification Policy

MUSNAD AI enforces an absolute **Source-First Verification Policy**:
1. No synthetic religious texts are admitted into the evidence base.
2. Every item of evidence must resolve to an immutable `source_code`, an authenticated edition, and a SHA-256 hash.
3. If evidence is missing or ambiguous, MUSNAD AI deterministically **abstains** (`insufficient_evidence`) or refers to human specialists (`specialist_referral`).

---

## 2. Master Source Registry Table

```json
[
  {
    "source_id": "SRC-001",
    "title": "القرآن الكريم (مصحف المدينة النبوية)",
    "title_en": "The Holy Quran",
    "type": "quran",
    "author": "كلام الله تعالى (Word of Allah)",
    "edition": "مصحف المدينة النبوية - برواية حفص عن عاصم",
    "publisher": "مجمع الملك فهد لطباعة المصحف الشريف",
    "language": "ar",
    "license": "Public Domain (King Fahd Complex / Tanzil Open Access)",
    "source_location": "knowledge_base/v0.2_expanded/quran/quran_canonical.json",
    "retrieval_date": "2026-09-24T16:02:07Z",
    "content_hash": "6dd951edf03c0ff45e0fe1abcb1490aa754948f5cb14dfdfb7c38eafaf6e6d87",
    "record_count": 6236,
    "verification_status": "verified",
    "notes": "النص القرآني الكامل لجميع سور القرآن الـ 114 بالرسم العثماني المعتمد."
  },
  {
    "source_id": "SRC-006",
    "title": "الأربعون النووية",
    "title_en": "Al-Arba'in al-Nawawiyya",
    "type": "hadith",
    "author": "الإمام يحيى بن شرف النووي (ت 676 هـ)",
    "edition": "دار المنهاج - تحقيق لجنة التراث",
    "publisher": "دار المنهاج للنشر والتوزيع",
    "language": "ar",
    "license": "Public Domain",
    "source_location": "knowledge_base/v0.2_expanded/hadith/nawawi40.json",
    "retrieval_date": "2026-09-24T16:02:07Z",
    "content_hash": "2100a084340be82ea87233a338fc31f83b9e1bc7cdf1bbc17106b0d82fec900d",
    "record_count": 42,
    "verification_status": "verified",
    "notes": "المتون الجامعة لقواعد الإسلام وأصول الدين برواياتها المعتمدة وأسانيدها."
  },
  {
    "source_id": "SRC-002",
    "title": "صحيح البخاري (الجامع المسند الصحيح)",
    "title_en": "Sahih al-Bukhari",
    "type": "hadith",
    "author": "الإمام محمد بن إسماعيل البخاري (ت 256 هـ)",
    "edition": "دار طوق النجاة (ترقيم محمد فؤاد عبد الباقي)",
    "publisher": "دار طوق النجاة",
    "language": "ar",
    "license": "Public Domain",
    "source_location": "knowledge_base/v0.2_expanded/hadith/bukhari.json",
    "retrieval_date": "2026-09-24T16:02:07Z",
    "content_hash": "8d6a3a5dfaedc7e973280ec1d338e32d5697fa0b6727099b2d0c78d289b4bb3b",
    "record_count": 1500,
    "verification_status": "verified",
    "notes": "أصح كتاب بعد كتاب الله، يحتوي على أصول الإيمان، والعبادات، والمعاملات."
  },
  {
    "source_id": "SRC-003",
    "title": "صحيح مسلم (المسند الصحيح)",
    "title_en": "Sahih Muslim",
    "type": "hadith",
    "author": "الإمام مسلم بن الحجاج النيسابوري (ت 261 هـ)",
    "edition": "دار إحياء الكتب العربية (تحقيق محمد فؤاد عبد الباقي)",
    "publisher": "دار إحياء الكتب العربية",
    "language": "ar",
    "license": "Public Domain",
    "source_location": "knowledge_base/v0.2_expanded/hadith/muslim.json",
    "retrieval_date": "2026-09-24T16:02:07Z",
    "content_hash": "fcd66fb07b2364863982ba8ece82e53ad39d0711d497cc335d1553761a0bcd93",
    "record_count": 1391,
    "verification_status": "verified",
    "notes": "صحيح الإمام مسلم، مفهرس بالكتب والأبواب والأرقام المعتمدة عالمياً."
  },
  {
    "source_id": "SRC-007",
    "title": "التفسير الميسر",
    "title_en": "Tafsir al-Muyassar",
    "type": "tafsir",
    "author": "نخبة من أساتذة التفسير (مجمع الملك فهد)",
    "edition": "الطبعة الثانية المنقحة (1430 هـ)",
    "publisher": "مجمع الملك فهد لطباعة المصحف الشريف",
    "language": "ar",
    "license": "Public Domain",
    "source_location": "knowledge_base/v0.2_expanded/tafsir/tafsir_muyassar.json",
    "retrieval_date": "2026-09-24T16:02:07Z",
    "content_hash": "a813d476cf79dc8e067a437d20c85636d63e0e4381f5b9066d7a150c7ac60544",
    "record_count": 6236,
    "verification_status": "verified",
    "notes": "تفسير معتمد لجميع آيات القرآن الـ 6236 مع تمييز تام عن نص الآية القرآني."
  },
  {
    "source_id": "SRC-008",
    "title": "موسوعة الآثار وأقوال أئمة الإسلام المعتمدة",
    "title_en": "Classical Scholarly Quotations & Athar",
    "type": "scholarly",
    "author": "أئمة المذاهب الأربعة وكبار الفقهاء",
    "edition": "طبعات دار المنهاج / مؤسسة الرسالة / مجمع الملك فهد",
    "publisher": "دور نشر علمية محققة",
    "language": "ar",
    "license": "Public Domain",
    "source_location": "knowledge_base/v0.2_expanded/scholarly/scholarly_quotes.json",
    "retrieval_date": "2026-09-24T16:02:07Z",
    "content_hash": "96ca727f5131de43a6b5bc37fbe07fc2d68104d8e688af39b276727f15d99723",
    "record_count": 15,
    "verification_status": "verified",
    "notes": "تتضمن مقولات موثقة بدقة لأبي حنيفة، مالك، الشافعي، أحمد، ابن تيمية، ابن القيم، والذهبي، مع تصنيف صريح للأقوال المكذوبة للاختبارات العدائية."
  },
  {
    "source_id": "SRC-009",
    "title": "سجل المراجع والقرارات الفقهية والمجمعية المعتمدة",
    "title_en": "Source-Backed Fiqh References & Academy Resolutions",
    "type": "fiqh",
    "author": "مجامع الفقه الإسلامي الدولي وهيئات الفتوى المعتمدة",
    "edition": "قرارات المجمع الفقهي الإسلامي (منظمة التعاون الإسلامي / رابطة العالم الإسلامي)",
    "publisher": "الأمانة العامة للمجامع الفقهية",
    "language": "ar",
    "license": "Public Domain / Institutional Resolutions",
    "source_location": "knowledge_base/v0.2_expanded/fiqh/fiqh_references.json",
    "retrieval_date": "2026-09-24T16:02:07Z",
    "content_hash": "32517c7f5f1bb6a431f70bb7ec6261b5f2a4ad4423516a2aae9369a934f1a248",
    "record_count": 6,
    "verification_status": "verified",
    "notes": "مراجع فقهية موثقة بالنص، مع وضع علامة الإحالة الوجوبية للمختصين في القضايا المستجدة (العملات المشفرة، التأمين، التبرع بالأعضاء)."
  }
]
```

---

## 3. Strict Boundary Rules

1. **Quran $\neq$ Tafsir**: Tafsir exegesis is stored with `source_type: "tafsir"` and can never be attributed as direct divine word (`source_type: "quran"`).
2. **Hadith $\neq$ Scholarly Athar**: Prophetic traditions are strictly segregated from statements of the companions or later jurists.
3. **No Inferred Gradings**: If a classical grading is not explicitly attested by scholars in the source print, `grading` remains `null`.
4. **No Autonomous Fatwa Generation**: Modern fiqh issues are routed to `SPECIALIST_REFERRAL` to preserve religious safety and academic ethics.
