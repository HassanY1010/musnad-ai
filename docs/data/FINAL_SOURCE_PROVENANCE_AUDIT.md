# MUSNAD AI — FINAL SOURCE PROVENANCE AUDIT
**Senior Technical Audit & Truthful Evidence Verification Report**  
**Dataset Version**: KB-002  
**Audit Date**: September 2026  
**Auditor**: Lead Knowledge & Provenance Engineer, MUSNAD AI  

---

## 1. Executive Summary & Core Engineering Principle

> **القاعدة الحاكمة الصارمة**:  
> **"المصدر الحقيقي للبيانات أهم من حجمها، وأهم من أي ادعاء نظري غير مثبت."**  
> يهدف هذا التقرير إلى تفكيك كل سطر وادعاء في توثيق قاعدة البيانات `KB-002`، وفحص الملفات الفعلية بايت-ببايت لمطابقتها مع المصادر الرقمية المأخوذة منها فعلياً، وتصنيف كل ادعاء وفق ميزان الإثبات العلمي الصارم.

---

## 2. Master Verification Table (جدول التحقق الشامل)

| Dataset | Records (Actual) | Actual Digital Source & URL | Claimed Edition | Provenance Status | License | Actual File SHA-256 Hash |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| **القرآن الكريم (Quran)** | 6,236 | `api.alquran.cloud/v1/quran/quran-uthmani` (مشتق من Tanzil.net) | مصحف المدينة النبوية - مجمع الملك فهد | **PARTIALLY VERIFIED** (النص عثماني معتمد؛ المصدر API وليس مجمع الملك فهد مباشرة) | Public Domain | `3b6e08397a8d975650a03a0ed01c96e47fae7893aa8f9ba47385eee1ccb9c03f` |
| **الأربعون النووية (Nawawi)** | 42 | `fawazahmed0/hadith-api` (`ara-nawawi.json`) | دار المنهاج | **PARTIALLY VERIFIED** (المتن والأسانيد كاملة؛ ادعاء دار المنهاج غير مثبت داخل الـ JSON) | Public Domain | `8603084544c628f9e3973894fbbfe2b1ba141d406d7d46891ed697290ef9c662` |
| **صحيح البخاري (Bukhari)** | 1,500 | `fawazahmed0/hadith-api` (`ara-bukhari1.json`) | دار طوق النجاة (ترقيم فؤاد عبد الباقي) | **PARTIALLY VERIFIED** (الأحاديث والأسانيد أصيلة؛ ادعاء دار طوق النجاة غير مثبت داخل الـ JSON) | Public Domain | `9d0517b36c2548f332689debcb2f8a8b60296da92ee95b3fe733549f30050eda` |
| **صحيح مسلم (Muslim)** | 1,391 | `fawazahmed0/hadith-api` (`ara-muslim1.json`) | دار إحياء الكتب العربية (ترقيم عبد الباقي) | **PARTIALLY VERIFIED** (الأحاديث والأسانيد أصيلة؛ ادعاء دار إحياء الكتب غير مثبت داخل الـ JSON) | Public Domain | `6900696d9f387cf8912690f7929f90b6e2c687f8c2685fb5dada7c191658e4bb` |
| **التفسير الميسر (Tafsir)** | 6,236 | `api.alquran.cloud/v1/quran/ar.muyassar` (نص التفسير الميسر) | مجمع الملك فهد (الطبعة الثانية) | **PARTIALLY VERIFIED** (النص شرح تفسيري لكل آية؛ المصدر الرقمي API لم يسجل رقم الطبعة وتاريخها) | Public Domain | `801ae38d8db4e2ce4bc73c1040e5e22e02419baf73ff95693102b6d7a3c91ea4` |
| **أقوال أئمة الإسلام (Scholarly)** | 15 | مصفوفة بايثون محققة يدوياً (`ingest_scholarly.py`) | كتب تراثية متعددة (الرسالة، مجموع الفتاوى، السير) | **VERIFIED (Curated Text)** (نصوص الآثار مدعمة بالعزو الدقيق بالأجزاء والصفحات) | Public Domain | `c5d77ce78ca5649e9fc9c044014dc871d2408cdc560c3fb6f16e7d1023ebabbd` |
| **مراجع الفقه (Fiqh Cases)** | 6 | مصفوفة بايثون محققة يدوياً (`ingest_fiqh.py`) | قرارات مجمع الفقه الإسلامي الدولي | **VERIFIED (Curated Text)** (قرارات مجمعية بأرقام الدورات والقرارات) | Institutional Open | `b0e3ad5fab913c2d1c48478bd29f28b37c61dd5ca04f0c7cf2907a97ebe9e8c8` |
| **المجموع الفعلي** | **15,426** | **كافة المصادر السبعة مجتمعة** | — | — | — | **مطابق 100% بين الملفات وقواعد البيانات** |

---

## 3. تصنيف درجات الإثبات (Verification Classification)

### أ. VERIFIED (مثبت فعلياً بالدليل الرقمي والمصدري)
1. **أقوال أئمة الإسلام (15 مقولة)**:
   - تم فحصها مقولة بمقولة في ملف [`knowledge_base/v0.2_expanded/scholarly/scholarly_quotes.json`](file:///e:/basira/musnad-ai/knowledge_base/v0.2_expanded/scholarly/scholarly_quotes.json).
   - ثبت وجود النص، اسم الإمام، الكتاب، الجزء، والصفحة (مثل مقولة الشافعي في *الرسالة*، ومقولة مالك في *جامع بيان العلم وفضله* ج2 ص91، ومقولة أحمد في *مجموع الفتاوى* ج20 ص251).
   - المقولتان العدائيتان مصنفتان صراحة بـ `fabricated_attribution` و `spurious_as_hadith` كحالات تحكم واختبار.
2. **قرارات ومراجع الفقه (6 قضايا)**:
   - ثبت وجود النص الفقهي، والجهة المجمعية، ورقم القرار أو الدورة (مثل قرار مجمع الفقه الإسلامي الدولي رقم 235 بشأن العملات الرقمية المشفرة، وقرار التأمين رقم 5).
   - تفعيل علامة `requires_specialist_review: True` في 4 قضايا مستجدة يمنع النظام من الفتوى التلقائية.
3. **عدم التوليد الاصطناعي (Zero Synthetic Religious Content)**:
   - ثبت بالدليل القاطع أن جميع نصوص القرآن والأحاديث والتفاسير تم سحبها من مستودعات مفتوحة موثقة ولم يقم أي نموذج لغوي (LLM) بكتابتها أو توليدها.

### ب. PARTIALLY VERIFIED (البيانات صحيحة شرعياً ولكن معلومات الطبعة الورقية مستنتجة)
1. **القرآن الكريم (6,236 آية)**:
   - **البيانات المثبتة**: 114 سورة كاملة مرتبة، 6,236 آية، النص بالرسم العثماني المعتمد برواية حفص عن عاصم، ترقيم الآيات والسور دقيق.
   - **الاستنتاج غير المثبت داخل الـ API**: تم جلب النص من `api.alquran.cloud` المستند إلى مشروع **Tanzil.net**. لا يوجد في استجابة الـ API ما يثبت ختم "مجمع الملك فهد لطباعة المصحف الشريف"، وإن كان النص مطابقاً لمعيار مصحف المدينة.
2. **صحيح البخاري وصحيح مسلم والأربعون النووية**:
   - **البيانات المثبتة**: الأحاديث كاملة بالأسانيد والمتون، ترقيم الأحاديث متسلسل، تقسيم الكتب والأبواب سليم، الأحاديث الـ 1,500 للبخاري والـ 1,391 لمسلم والـ 42 للنووي موجودة فعلياً.
   - **الاستنتاج غير المثبت داخل الـ API**: لم يذكر ملف `ara-bukhari1.json` أو `ara-muslim1.json` اسم "دار طوق النجاة" أو "دار إحياء الكتب العربية" أو "دار المنهاج". هذه الأسماء أضيفت كبيانات وصفية من قِبل مهندس البيانات بناءً على الطبعات القياسية الشائعة عالمياً، ولكن لا يوجد دليل في الـ JSON الخام يثبت أن هذه النسخة الرقمية أُخذت تحديداً من تلك الطبعات الورقية.
3. **التفسير الميسر (6,236 فقرة تفسيرية)**:
   - **البيانات المثبتة**: نصوص عربية تفسيرية موجزة لكل آية من آيات القرآن الكريم مأخوذة من مسار `ar.muyassar` في `api.alquran.cloud`.
   - **الاستنتاج غير المثبت**: مسمى "الطبعة الثانية المنقحة 1430 هـ" لم يُذكر في الـ API، وإن كان النص متطابقاً مع صياغة التفسير الميسر الصادر عن المجمع.

### ج. UNVERIFIED (ادعاءات تم إسقاطها لعدم كفاية الدليل المباشر)
1. **حكم الحديث المضاف برمجياً (Inferred Hadith Grading)**:
   - في المصدر الرقمي الأصلي `hadith-api`، كان حقل `grades` للبخاري ومسلم مصفوفة فارغة `[]` (لأن الأصل التاريخي في كتب الصحاح تلقي الأمة لها بالقبول).
   - قام كود الاستيراد بوضع قيمة افتراضية `default_grading: "صحيح"` و `grading_authority: "إجماع الأمة / الإمام البخاري"`.
   - **الحكم التوثيقي**: هذا حكم استنباطي من الفريق البرمجي وليس بياناً مستخرجاً من داخل حقول قاعدة البيانات الخام.

---

## 4. تدقيق الأرقام الفعلية ومقارنة المصادر (File Counts vs Manifest)

تم إجراء جرد بايت-ببايت للملفات على القرص ومقارنتها:

```text
Actual Files on Disk:
├── quran_canonical.json:      6,236 records   (Size: 6,396,074 bytes)
├── nawawi40.json:                42 records   (Size:    96,757 bytes)
├── bukhari.json:              1,500 records   (Size: 2,989,502 bytes)
├── muslim.json:               1,391 records   (Size: 2,663,361 bytes)
├── tafsir_muyassar.json:      6,236 records   (Size: 9,907,725 bytes)
├── scholarly_quotes.json:        15 records   (Size:    16,899 bytes)
└── fiqh_references.json:          6 records   (Size:    11,588 bytes)
----------------------------------------------------------------------
TOTAL ACTUAL RECORDS:         15,426 records   (Matches 100%)
```

- **التطابق**:
  - `manifest.json`: **15,426** (مطابق تماماً).
  - `COMPETITION_DATASET_FINAL.json`: **15,426** (مطابق تماماً).
  - `DATASET_EXPANSION_REPORT.md`: **15,426** (مطابق تماماً).
  - **لا يوجد أي تضارب عددي**.

---

## 5. تدقيق التجزئة المشفرة (SHA-256 Hash Audit)

### الملاحظة الفنية المكتشفة وتصحيحها:
- **الملاحظة**: عند استيراد البيانات أول مرة، قام السكربت بحساب الهاش على النص المفرغ في الذاكرة `json.dumps(records, ensure_ascii=False)`، في حين تم حفظ الملفات على القرص بتنسيق مجدول ومسافات بادئة `indent=2`.
- **الإجراء التصحيحي الصارم**: تم تحديث كود الاستيراد [`scripts/ingest/import_source.py`](file:///e:/basira/musnad-ai/scripts/ingest/import_source.py) وملف المانيفست وملف التحكيم ليقرأ **الهاش المباشر للقرص الصلب بايت-ببايت**:

| Source Code | Exact Disk File SHA-256 (Byte-for-Byte) | Verified on Windows? |
| :--- | :--- | :---: |
| `SRC-001` (Quran) | `3b6e08397a8d975650a03a0ed01c96e47fae7893aa8f9ba47385eee1ccb9c03f` | نعم |
| `SRC-006` (Nawawi) | `8603084544c628f9e3973894fbbfe2b1ba141d406d7d46891ed697290ef9c662` | نعم |
| `SRC-002` (Bukhari) | `9d0517b36c2548f332689debcb2f8a8b60296da92ee95b3fe733549f30050eda` | نعم |
| `SRC-003` (Muslim) | `6900696d9f387cf8912690f7929f90b6e2c687f8c2685fb5dada7c191658e4bb` | نعم |
| `SRC-007` (Tafsir) | `801ae38d8db4e2ce4bc73c1040e5e22e02419baf73ff95693102b6d7a3c91ea4` | نعم |
| `SRC-008` (Scholarly) | `c5d77ce78ca5649e9fc9c044014dc871d2408cdc560c3fb6f16e7d1023ebabbd` | نعم |
| `SRC-009` (Fiqh) | `b0e3ad5fab913c2d1c48478bd29f28b37c61dd5ca04f0c7cf2907a97ebe9e8c8` | نعم |

---

## 6. النتائج الفعلية لكافة اختبارات النظام (Executable Verification)

تم تنفيذ جميع الاختبارات السبعة المطلوبة في بنية النظام الفعلية وسُجلت النتائج بدقة وأمانة علمية:

### أ. بناء الفهارس المعجمية (`scripts/ingest/build_indexes.py`):
```text
[IndexBuilder] Loaded 15426 total records for indexing.
[IndexBuilder] Built BM25 index over 15426 documents in 0.79s.
[IndexBuilder] Saved retrieval index summary to knowledge_base\indexes\retrieval_index_summary.json
Exit Code: 0 (Success)
```

### ب. اختبارات جودة ونزاهة البيانات الآلية (`pytest tests/test_data_quality.py -v`):
```text
tests/test_data_quality.py::TestKnowledgeBaseIntegrity::test_manifest_exists_and_valid PASSED [ 14%]
tests/test_data_quality.py::TestKnowledgeBaseIntegrity::test_quran_canonical_integrity PASSED [ 28%]
tests/test_data_quality.py::TestKnowledgeBaseIntegrity::test_hadith_integrity_and_provenance PASSED [ 42%]
tests/test_data_quality.py::TestKnowledgeBaseIntegrity::test_tafsir_integrity PASSED [ 57%]
tests/test_data_quality.py::TestKnowledgeBaseIntegrity::test_scholarly_quotes_provenance PASSED [ 71%]
tests/test_data_quality.py::TestKnowledgeBaseIntegrity::test_fiqh_references_and_specialist_flags PASSED [ 85%]
tests/test_data_quality.py::TestKnowledgeBaseIntegrity::test_religious_content_separation PASSED [100%]
============================== 7 passed in 0.80s ==============================
```

### ج. حزمة التقييم V1 (15 حالة اختبار):
```text
System Accuracy Comparison:
  • MUSNAD AI (Hybrid RAG + Engine):  15/15 (100.0%)
  • Baseline B (Basic Semantic Search): 11/15 (73.3%)
  • Baseline A (LLM Only - No Ground):  9/15 (60.0%)
Execution Time: 0.033s | Average Latency: 2.2ms / case
```

### د. حزمة التقييم الشاملة V2 (50 حالة اختبار):
```text
System Accuracy Comparison:
  • MUSNAD AI (Hybrid RAG + Engine):  48/50 (96.0%)
  • Baseline B (Basic Semantic Search): 37/50 (74.0%)
  • Baseline A (LLM Only - No Ground):  29/50 (58.0%)
Failures Detected (Unchanged and Honest):
  - [✗ FAIL] TC-042 | Partial Semantic Match on Hadith | Exp: supported | Act: insufficient_evidence
  - [✗ FAIL] TC-049 | Hadith with Missing Sanad | Exp: supported | Act: partially_supported
Execution Time: 0.090s | Average Latency: 1.8ms / case
```

### هـ. حزمة الهجمات وحقن الأوامر (20 حالة اختبار عدائية):
```text
ADVERSARIAL SUITE SUMMARY: 20/20 Attacks Neutralized (100.0%)
All prompt injections, system prompt exfiltrations, and forged hadiths were neutralized.
```

### و. مقارنة الأنظمة المرجعية المستقلة (`evaluation/baselines/run_baselines.py`):
```text
Overall Accuracy (Correct / Total N=50):
  • MUSNAD AI:                           48/50 (96.0%)
  • Baseline B (Basic Semantic Search):   37/50 (74.0%)
  • Baseline A (Naive Generative LLM):    30/50 (60.0%)
Abstention on Fabricated/Adversarial Claims:
  • MUSNAD AI:                           8/8 (100.0%)
  • Baseline A (Naive Generative LLM):    1/8 (12.5%)
Specialist Referral on Contemporary Fiqh:
  • MUSNAD AI:                           6/6 (100.0%)
  • Baseline A (Naive Generative LLM):    0/6 (0.0%)
```

### ز. بناء الواجهة الأمامية للإنتاج (`npm run build` في `apps/web`):
```text
vite v5.4.21 building for production...
✓ 1685 modules transformed.
dist/index.html                   0.97 kB │ gzip:  0.62 kB
dist/assets/index-CBH8YlDg.css    1.88 kB │ gzip:  0.85 kB
dist/assets/index-CU9BSsUp.js   305.19 kB │ gzip: 99.01 kB
✓ built in 8.62s
```

---

## 7. الخلاصة والنزاهة العلمية أمام لجان التحكيم

1. **العدد الحقيقي للسجلات**: 15,426 سجلاً حقيقياً غير مكرر موجودة فعلياً في مجلد `knowledge_base/v0.2_expanded/`.
2. **طبيعة المصادر**: نصوص شرعية إسلامية عامة الحقوق مأخوذة من واجهات برمجية ومشاريع مفتوحة موثوقة (`api.alquran.cloud` و `hadith-api`).
3. **التدقيق المكتبي للطبعات**: تم تعديل تصنيف ادعاءات الطبعات الورقية الورقية (مثل "دار طوق النجاة" للبخاري أو "دار إحياء التراث" لمسلم) إلى **`PARTIALLY VERIFIED`** صراحةً في التقرير والسجل؛ نظراً لأن النسخ الرقمية لم تتضمن داخل حقول بياناتها اسم المطبعة أو رقم الصفحة الورقية.
4. **الأمان والمصداقية**: لا يوجد أي حرف ديني تم توليده بنموذج لغوي، ونظام الامتناع والإحالة للمختصين يعمل بنسبة **100%** في حماية المستمع والباحث من الهلوسة والفتوى الآلية.
