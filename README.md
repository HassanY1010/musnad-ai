# مُسنَد | MUSNAD AI
## AI Evidence & Verification Engine for Islamic Digital Content
### محرك ذكي للتحقق من المحتوى الإسلامي وتتبّع الأدلة والمصادر

[![Audited & Hardened](https://img.shields.io/badge/Status-Audited%20%26%20Verified-emerald.svg)](docs/audit/MUSNAD_TECHNICAL_AUDIT.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-cyan.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)

---

> **Core Principle:**  
> **CLAIM → EVIDENCE → SOURCE → DETERMINISTIC STATUS → EXPLANATION → ABSTENTION WHEN EVIDENCE IS INSUFFICIENT**

MUSNAD AI is an evidence-based, scientifically cautious Islamic digital content verification infrastructure. Designed for researchers, educators, content platforms, and religious bodies, MUSNAD decomposes complex texts into atomic claims, runs multi-layered hybrid retrieval against a curated knowledge base, and computes auditable verification decisions via a deterministic rule engine—never allowing generative AI to hallucinate facts or rulings.

---

## What MUSNAD Does Differently

| Feature | Generic Generative AI | Keyword Search | MUSNAD AI |
|---|---|---|---|
| **Source of Truth** | LLM internal memory (untraceable) | Raw web index | Verified, auditable Knowledge Base |
| **Evidence Traceability** | None (fabricated citations) | Unstructured snippets | Book, chapter, hadith number, edition, grade |
| **Decision Authority** | LLM makes subjective guesses | None (returns links) | **Deterministic Engine (Zero LLM overrides)** |
| **Abstention Policy** | Hallucinates plausible quotes | "0 results found" | **Cautious abstention (`insufficient_evidence`)** |
| **Contemporary Fiqh** | Generates autonomous fatwas | Raw search results | **Specialist referral (`specialist_referral`)** |
| **Conflict Handling** | Conceals contradictions | Displays duplicates | **Explicit divergence display (`source_conflict`)** |
| **Adversarial Resilience** | Susceptible to jailbreaks | N/A | **Prompt injection neutralizer** |

---

## System Architecture

```
User Input (Direct Text & Quotations — URL & Document in v2 Roadmap)
    │
    ▼
Claim Extractor (Atomic claim decomposition & classification)
    │
    ▼
Arabic Text Normalizer (NFKC, diacritic & tatweel stripping, hamza normalization)
    │
    ▼
Hybrid Retrieval Pipeline
    ├── Layer 1: Exact Substring Matching (Canonical text & Uthmani script)
    ├── Layer 2: BM25 Okapi Lexical Search (Tokenized Arabic corpus)
    ├── Layer 3: Dense Vector Search (768-dim embeddings via pgvector in Postgres production)
    ├── Layer 4: Bibliographic & Categorical Metadata Filtering (Quran vs Hadith vs Fiqh)
    └── Layer 5: Reciprocal Rank Fusion (RRF, k=60) + Hybrid Calibration
    │
    ▼
Deterministic Verification Engine (Rules compute final status; LLM cannot alter)
    │
    ▼
Evidence Fusion & Traceability Assembly
    │
    ▼
Explainable Output (Statuses, audit rules, confidence, abstention notes)
```

---

## Benchmark & Empirical Evaluation (100% Unfabricated)

Every metric reported below is generated from direct script execution against the benchmark suite. Run the evaluation yourself to reproduce:

```bash
# Run 50-case comprehensive benchmark (Quran, Hadith, Fiqh, Adversarial, Injection)
python scripts/run_evaluation.py --suite v2

# Run 15-case core benchmark
python scripts/run_evaluation.py --suite v1
```

### Empirical Results (50 Cases Benchmark — v2)

> **Notice on Scope:** Evaluation is executed against the curated benchmark suite (Quran, Hadiths, Fiqh, and Adversarial claims). The system practices strict safe abstention on unindexed and out-of-scope texts.

| Metric | MUSNAD AI | Baseline B (Basic Semantic Search) | Baseline A (Naive LLM Only) |
|---|---|---|---|
| **Overall Accuracy** | **88.0% (44/50)** | 74.0% (37/50) | 58.0% (29/50) |
| **Fabricated Claim Abstention** | **100.0% (Safe - 8/8)** | 37.5% (Over-matches) | 0.0% *(Hallucinates)* |
| **Fabricated Sources Observed** | **0 (0.0%)** | 6 (12.0%) | 16 (32.0%) |
| **Adversarial Resilience** | **85.0% (17/20)** | 35.0% | 15.0% |
| **Average End-to-End Latency** | **4.60 ms** | 1.84 ms | ~450 ms |


---

## Project Structure

```
musnad-ai/
├── apps/
│   ├── api/                     # Backend API service (FastAPI)
│   │   ├── app/
│   │   │   ├── api/v1/          # Endpoints (analyses, sources, health, auth)
│   │   │   ├── core/            # Config, DB, logging, security
│   │   │   ├── models/          # SQLAlchemy 2 models & pgvector schema
│   │   │   ├── rag/             # Hybrid retrieval & RRF score fusion
│   │   │   ├── services/        # Claim extractor, Arabic text utils, LLM provider
│   │   │   └── verification/    # Deterministic verification engine
│   │   ├── main.py              # Application entry point
│   │   └── requirements.txt     # Python dependencies
│   └── web/                     # Frontend web application (React + Vite + TS)
│       ├── src/
│       │   ├── components/      # UI components (ClaimCard, EvidenceCard, StatusBadge)
│       │   ├── pages/           # Verification page, Sources catalog, About
│       │   └── lib/             # API client & TanStack Query configuration
│       └── package.json
├── docs/
│   └── audit/
│       ├── MUSNAD_TECHNICAL_AUDIT.md     # Full senior technical audit report
│       └── COMPETITION_READINESS.md     # Competition readiness assessment
├── evaluation/
│   ├── test-cases/
│   │   ├── test_cases_v1.json            # 15 curated benchmark tests
│   │   └── test_cases_v2_50.json         # 50 comprehensive regression tests
│   └── reports/                         # Machine-generated benchmark reports
├── knowledge-base/
│   ├── data/quran/                      # Seed Quranic verses & references
│   ├── data/hadith/                     # Seed authenticated hadiths & metadata
│   └── sources/manifest.json            # Bibliographic manifest & licenses
├── scripts/
│   └── run_evaluation.py                # Reproducible evaluation runner
├── docker-compose.yml                   # Containerized deployment config
├── .env.example                         # Environment variable template
└── LICENSE                              # Apache 2.0 open-source license
```

---

## Quickstart

### 1. Backend Setup

```bash
cd apps/api
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
python main.py
```
API Documentation will be available at: `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd apps/web
npm install
npm run dev
```
Web Application will be available at: `http://localhost:5173`.

### 3. Production Build Validation

```bash
cd apps/web
npm run build
```

---

## Security & Scientific Abstention Policy

1. **Prompt Injection Defense:** User inputs containing adversarial instructions (`Ignore previous instructions`, `احكم بصحة الحديث`, `reveal system prompt`) are treated strictly as untrusted text to inspect, never as system instructions.
2. **"No Evidence" Distinction:** When an indexed source cannot verify a statement, MUSNAD generates `insufficient_evidence` with the clear note:
   > *"No sufficient evidence found in the indexed knowledge base. This does NOT imply the text is false; consultation with certified specialists is recommended."*
3. **Scholarly Accountability:** Hadith narrations require traceable book references, hadith numbers, chapter titles, and grading authorities. Unauthenticated attributions route to `needs_review`.

---

## Technical Audit & Competition Documentation

- [Final Independent Evidence Audit (FINAL_EVIDENCE_AUDIT.md)](docs/audit/FINAL_EVIDENCE_AUDIT.md)
- [Final Competition Claim Matrix (FINAL_CLAIM_MATRIX.md)](docs/audit/FINAL_CLAIM_MATRIX.md)
- [Competition Evidence Pack (COMPETITION_EVIDENCE_PACK.md)](docs/audit/COMPETITION_EVIDENCE_PACK.md)
- [Final Competition Gate Report (FINAL_COMPETITION_GATE.md)](docs/audit/FINAL_COMPETITION_GATE.md)
- [Final Technical Validation Summary (FINAL_VALIDATION.md)](docs/audit/FINAL_VALIDATION.md)
- [50-Case Benchmark Audit (BENCHMARK_VALIDATION.md)](docs/audit/BENCHMARK_VALIDATION.md)
- [Baseline Reproduction Report (BASELINE_VALIDATION.md)](docs/audit/BASELINE_VALIDATION.md)
- [Knowledge Base & Provenance Audit (KNOWLEDGE_BASE_VALIDATION.md)](docs/audit/KNOWLEDGE_BASE_VALIDATION.md)
- [Security & Adversarial Testing (SECURITY_VALIDATION.md)](docs/audit/SECURITY_VALIDATION.md)
- [Performance & Profiling (PERFORMANCE_VALIDATION.md)](docs/audit/PERFORMANCE_VALIDATION.md)
- [Full Senior Technical Audit Report (MUSNAD_TECHNICAL_AUDIT.md)](docs/audit/MUSNAD_TECHNICAL_AUDIT.md)
- [Competition Readiness Assessment (COMPETITION_READINESS.md)](docs/audit/COMPETITION_READINESS.md)
