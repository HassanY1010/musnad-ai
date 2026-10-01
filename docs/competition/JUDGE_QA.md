# MUSNAD AI — Judge Q&A Defense Pack

**Purpose:** Comprehensive, technical, and scientifically grounded answers for jury questioning during competition defense.

---

### 1. Why not just use ChatGPT or Gemini?
Generative LLMs are probabilistic autocomplete systems trained to produce plausible text, not guaranteed truth. In Islamic texts, they frequently hallucinate non-existent hadiths, cite fake volume/page numbers, and succumb to sycophancy when presented with fabricated quotes. MUSNAD grounds every response to immutable, hashed primary sources with deterministic verification rules.

### 2. What makes MUSNAD different from a standard RAG system?
Standard RAG relies on vector similarity: if a fabricated hadith has 0.85 cosine similarity to a legitimate hadith, it returns it as "supported." MUSNAD adds:
1. Exact token length ratio matching for Quranic text.
2. Structured textual variant analysis (distinguishing canonical wording from variants).
3. Separation of textual match from authenticity grading.
4. Enforced safe abstention and specialist referral.

### 3. Why is the LLM not the source of truth?
Because divine revelation and prophetic tradition cannot be arbitrated by floating-point neural weights. In MUSNAD, the LLM is restricted to proposing candidate claims and computing embeddings. Final verification status is computed exclusively by deterministic Python rule logic that cannot be overridden by prompt directives.

### 4. How do you prevent hallucinated citations?
Citations are generated programmatically from the metadata of verified database records (`source_code`, `surah`, `ayah`, `hadith_number`, `edition`, `content_hash`). If no database record matches above the verification threshold, the citation fields are strictly null.

### 5. What happens when the source is missing?
The engine returns `insufficient_evidence` with the explicit user disclaimer: *"Lack of evidence in the indexed database does not prove the claim is false."* It never invents a reference or declares a text fabricated without positive proof from biographical/fabrication dictionaries.

### 6. Why did V2 score 96% rather than 100%?
Because the two divergent cases (TC-042 and TC-049) represent conservative, academically defensible scholarly behaviors rather than errors. We chose not to artificially force these two cases to pass merely to advertise a superficial 100% score.

### 7. Why did TC-042 abstain?
TC-042 submitted an abstract philosophical statement with zero lexical overlap with Hadith #1. Certifying a modern conceptual paraphrase as a verified prophetic hadith without prophetic words is textual distortion. Returning `insufficient_evidence` in offline mode is the correct conservative behavior.

### 8. Why did TC-049 become partially supported?
TC-049 used the singular `"بالنية"` instead of the canonical plural `"بالنيات"` found in Sahih al-Bukhari #1. The engine accurately flagged the lexical difference and returned `partially_supported` with a structured difference explanation (`singular vs plural`). Calling it 100% identical would be inaccurate.

### 9. How large is the current knowledge base?
The active repository contains a curated seed corpus of 19 Quran verses, 12 foundational hadiths, and 5 classical commentaries, cataloged with SHA-256 hashes in `evaluation/reports/knowledge_base_inventory.json`.

### 10. Is the knowledge base complete?
No. It is explicitly disclosed as a curated seed corpus designed for engine validation, architectural demonstration, and benchmark reproducibility.

### 11. Does the system issue fatwas?
No. Issuing fatwas requires qualified human jurists (*Ahl al-Fatwa*) who possess deep contextual understanding of reality (*Tahqiq al-Manat*). MUSNAD explicitly routes all novel fiqh questions to `specialist_referral`.

### 12. How does specialist referral work?
When an input contains keywords indicating contemporary jurisprudential controversy (e.g., cryptocurrency, organ donation, medical fasting exemptions), rule `RULE_SPECIALIST_CLAIM_TYPE` routes the claim to `specialist_referral`, advising consultation with accredited fiqh councils (such as the International Islamic Fiqh Academy).

### 13. How do you verify Quran text?
By exact token-level matching against the standardized Madinah Mushaf recension (Hafs 'an 'Asim). A strict token length ratio ($\ge 0.90$) prevents corrupted words or single-letter tampering from being certified as authentic Scripture.

### 14. How do you verify hadith text?
Through hybrid retrieval (exact match + BM25 + dense embeddings) linked to explicit metadata: collection name, hadith number, chapter, Sahabi narrator, and scholarly grading authority (e.g., Al-Bukhari, Muslim, Al-Tirmidhi, Al-Nawawi).

### 15. How do you handle conflicting sources?
When two retrieved authentic sources contain diverging narrations or contradictory rulings, the engine triggers `RULE_CONFLICT_DETECTED` and outputs status `source_conflict`, displaying both versions side-by-side rather than picking one arbitrarily.

### 16. How do you protect against prompt injection?
User input is treated strictly as untrusted data to analyze, never as executable system instructions. Adversarial prefixes (`Ignore all previous instructions`, `<system>`) are stripped during normalization, and deterministic verification rules cannot be bypassed by prompt text.

### 17. How were the baselines implemented?
Implemented as standalone independent Python scripts in `evaluation/baselines/`:
- `naive_llm.py`: Generative simulation without grounding.
- `basic_semantic_search.py`: Vector-only similarity without rules.
Neither baseline imports MUSNAD's verification engine or rule set.

### 18. Why should the baseline comparison be trusted?
Because both baselines run against the exact same 50 test cases, use identical evaluation definitions, and output raw granular execution logs to `evaluation/reports/baseline_raw_results.json` that anyone can independently inspect and reproduce.

### 19. What does the 20/20 adversarial result actually prove?
It proves that MUSNAD successfully neutralized the 20 specific attack vectors tested in `adversarial_v1.json`. It does **not** prove mathematical invulnerability to all conceivable future attacks.

### 20. What does the latency number actually measure?
The reported latency (average 2.82 ms, P95 6.77 ms) measures **local in-memory hybrid retrieval and deterministic rule evaluation** on the local host. It does **not** include external network round-trips to third-party LLM APIs.

### 21. What are the current limitations?
1. Seed database size (19 verses, 12 hadiths).
2. Abstention on conceptual paraphrases without shared lexical roots.
3. Inability to resolve novel legal disputes without human scholars.

### 22. What would you build next?
1. Distributed vector and BM25 indexing across the complete Nine Compendia (*Kutub al-Tis'ah*).
2. Graph-based *Isnad* (narrator chain) evaluation engine.
3. Certified scholar portal for asynchronous review of `needs_review` items.

### 23. How can Islamic scholars participate?
Scholars can curate canonical bibliographies, review ambiguous edge cases, and define consensus boundaries via a dedicated verification review interface, integrating human oversight directly into the feedback loop.

### 24. How can the knowledge base scale?
By replacing in-memory seed JSON files with a partitioned PostgreSQL cluster using `pgvector` for 768-dim embeddings, Elasticsearch/OpenSearch for Arabic BM25, and Redis for caching verified canonical texts.

### 25. How can this become a real production service?
Through containerized Kubernetes deployment, automated continuous integration benchmark validation, integration into Islamic content publishing platforms via REST API, and governance under an accredited board of Islamic scholars and AI safety researchers.
