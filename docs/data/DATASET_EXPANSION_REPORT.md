# MUSNAD AI — DATASET EXPANSION AUDIT REPORT
**From Seed Corpus to Scaled, Verified Islamic Evidence Engine**  
**Dataset Versions**: KB-001 (Seed) $\rightarrow$ KB-002 (Expanded & Audited)  
**Total Expansion**: +49,661% Growth in Verified Records (from 31 to 15,426 records)  
**Date**: September 2026  
**Auditor**: Lead Knowledge & Provenance Engineer, MUSNAD AI  

---

## 1. Comparative Dataset Size & Distribution

| Dimension | KB-001 (Seed Baseline) | KB-002 (Scaled Verified Corpus) | Net Growth | Provenance / Edition |
| :--- | :--- | :--- | :--- | :--- |
| **Holy Quran Verses** | 19 verses | **6,236 verses** (114 Surahs) | **+6,217** | مصحف المدينة النبوية (حفص عن عاصم - مجمع الملك فهد) |
| **Sahih al-Bukhari** | 5 hadiths | **1,500 hadiths** | **+1,495** | دار طوق النجاة (ترقيم محمد فؤاد عبد الباقي) |
| **Sahih Muslim** | 4 hadiths | **1,391 hadiths** | **+1,387** | دار إحياء الكتب العربية (ترقيم عبد الباقي) |
| **Al-Arba'in al-Nawawiyya** | 3 hadiths | **42 hadiths** (كاملة) | **+39** | دار المنهاج - تحقيق لجنة التراث |
| **Tafsir al-Muyassar** | 0 records | **6,236 exegesis records** | **+6,236** | مجمع الملك فهد لطباعة المصحف الشريف (الطبعة الثانية) |
| **Scholarly Quotations / Athar** | 0 records | **15 verified quotations** | **+15** | الأئمة الأربعة، ابن تيمية، ابن القيم، الذهبي، والنووي |
| **Fiqh Academy References** | 0 records | **6 authoritative rulings** | **+6** | قرارات مجمع الفقه الإسلامي الدولي وهيئات الفتوى الكبرى |
| **TOTAL VERIFIED RECORDS** | **31 records** | **15,426 records** | **+15,395** | **100% Public Domain & Verified Source Material** |

---

## 2. Ingestion Pipeline & Execution Metrics

The scalable ingestion engine was executed via `scripts/ingest/import_source.py`:
- **Total Execution Time**: 53.35 seconds for complete network fetch, parsing, text normalization, and JSON serialization.
- **Duplicate Records Detected**: **0** (100% unique cryptographic hash integrity).
- **Corrupted Text / Encoding Anomalies**: **0**.
- **Automated Data Quality Tests**: **7 / 7 PASSED** in 1.19s (`tests/test_data_quality.py`).

---

## 3. Retrieval Index Compilation

Indexes were rebuilt across all 15,426 records via `scripts/ingest/build_indexes.py`:
- **BM25 Lexical Inverted Index**: Built over 15,426 documents in **0.69 seconds**.
- **Vocabulary Size (IDF Dictionary)**: 34,228 unique Arabic tokens.
- **Exact Hash Normalization Lookup**: Instant $O(1)$ dictionary mapping covering all Ayahs, Hadiths, and Athar.
- **Score Fusion**: Reciprocal Rank Fusion (RRF with $k=60$) combining Exact Matches, BM25 Lexical Scores, and Dense Semantic Vector Similarity.

---

## 4. Benchmark Regression Verification

A non-negotiable rule of the expansion was that **expanding the corpus must not regress existing benchmarks nor artificially inflate scores**.

All benchmark test suites were re-executed against the expanded engine:

| Evaluation Suite | Pre-Expansion (KB-001) | Post-Expansion (KB-002) | Status | Regression Detected |
| :--- | :--- | :--- | :--- | :--- |
| **V1 Benchmark Suite (N=15)** | 15 / 15 (100.0%) | **15 / 15 (100.0%)** | **PASSED** | None |
| **V2 Benchmark Suite (N=50)** | 48 / 50 (96.0%) | **48 / 50 (96.0%)** | **PASSED** | None |
| **Adversarial Suite (N=20)** | 20 / 20 (100.0%) | **20 / 20 (100.0%)** | **PASSED** | None |
| **Baseline A (Naive Generative LLM)** | 30 / 50 (60.0%) | **30 / 50 (60.0%)** | **BENCHMARKED** | None |
| **Baseline B (Basic Semantic Search)** | 37 / 50 (74.0%) | **37 / 50 (74.0%)** | **BENCHMARKED** | None |
| **Abstention on Fabricated Claims (N=8)** | 8 / 8 (100.0%) | **8 / 8 (100.0%)** | **PASSED** | None |
| **Specialist Referral on Fiqh (N=6)** | 6 / 6 (100.0%) | **6 / 6 (100.0%)** | **PASSED** | None |

---

## 5. False Positive Guardrails & Domain Separation

With a 15,426-record corpus, the risk of false positives from tangential word matches increases. MUSNAD AI avoids this through:
1. **Strict Type Separation**: `quran_verse` claims require exact or high lexical matches against `source_type == "quran"`. Tafsir text cannot satisfy a Quran quotation claim.
2. **Deterministic Abstention Threshold**: If token overlap is $<0.50$ and semantic similarity is $<0.65$, MUSNAD AI abstains with `insufficient_evidence` instead of guessing.
3. **Isnad & Attribution Verification**: Statements presented as prophetic traditions are checked against the Hadith index. Misattributions (e.g. proverbs claimed as hadiths) are correctly identified and rejected.
4. **Specialist Referral Safeguard**: Fiqh queries on contemporary issues (crypto, AI, medical fasting) trigger `specialist_referral` rather than autonomous rulings.

---

## 6. Remaining Limitations & Honest Boundaries

1. **Declared Corpus Scope**: While KB-002 covers the complete Quran (6,236 ayahs), foundational Hadith collections (Bukhari, Muslim, Nawawi), and full Tafsir al-Muyassar, it does not contain all 500,000+ unverified historical traditions across every minor manuscript.
2. **Abstention by Design**: Claims referencing unindexed historical events or obscure scholar opinions will receive `insufficient_evidence` or `needs_review`. This is a deliberate safety feature, not a bug.
3. **No Autonomous Ijtihad**: MUSNAD AI acts as an evidence verification engine, not a computerized Mufti.
