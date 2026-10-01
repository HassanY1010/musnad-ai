# MUSNAD AI — Architecture Diagram Specification

**Purpose:** Definitive visual and architectural blueprint for MUSNAD AI verification infrastructure.  
**Core Thesis:** $\text{LLM} \neq \text{Source of Truth}$. Verification is computed by deterministic rule logic over immutable, hashed evidence.

---

## 1. Complete Architecture Flowchart

```mermaid
flowchart TD
    classDef userLayer fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef extractLayer fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef ragLayer fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#f8fafc;
    classDef engineLayer fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#f8fafc;
    classDef outputLayer fill:#701a75,stroke:#f43f5e,stroke-width:2px,color:#f8fafc;
    classDef auditLayer fill:#312e81,stroke:#6366f1,stroke-width:2px,color:#f8fafc;

    User[USER CONTENT<br>Text / URL / Document]:::userLayer --> Extractor[CLAIM EXTRACTION ENGINE<br>Decomposes into Atomic Claims<br>Deterministic Precedence Rules]:::extractLayer
    
    Extractor --> Normalizer[ARABIC TEXT NORMALIZATION<br>NFKC Normalization + Diacritic Stripping<br>Tatweel Stripping + Hamza Unification]:::extractLayer

    Normalizer --> HybridRAG[5-LAYER HYBRID RETRIEVAL]:::ragLayer

    subgraph HybridRAGPipeline [Hybrid Retrieval Engine]
        direction TB
        Layer1[Layer 1: Exact Substring Matching]
        Layer2[Layer 2: BM25 Okapi Lexical Search]
        Layer3[Layer 3: Dense Semantic Vector 768-dim]
        Layer4[Layer 4: Metadata Filtering Chapter, Grade]
        Layer5[Layer 5: Reciprocal Rank Fusion RRF k=60]
    end

    HybridRAG --> Fusion[EVIDENCE FUSION & PROVENANCE<br>Coordinates + Narrator + Edition + Content Hash]:::ragLayer

    Fusion --> Engine[DETERMINISTIC VERIFICATION ENGINE<br>LLM NEVER Decides Authenticity<br>Strict Deterministic Rules]:::engineLayer

    subgraph DecisionTaxonomy [6-State Verification Taxonomy]
        direction TB
        S1[supported — Exact canonical match]
        S2[partially_supported — Lexical/thematic variant]
        S3[needs_review — Unverified attribution]
        S4[insufficient_evidence — Unindexed; does NOT imply falsity]
        S5[source_conflict — Contradictory narrations]
        S6[specialist_referral — Contemporary fiqh / fatwa]
    end

    Engine --> Explanation[EXPLAINABLE VERIFICATION DECISION<br>Structured Textual Variant Report<br>Singular vs Plural / Textual Differences]:::outputLayer

    Explanation --> Traceability[SOURCE TRACEABILITY<br>Canonical Book + Surah/Ayah + Hadith # + Hash]:::outputLayer

    Traceability --> AuditLog[(CRYPTOGRAPHIC AUDIT LOG<br>SHA-256 Forward-Chained Tree<br>entry_hash = SHA256 prev_hash + payload)]:::auditLayer
```

---

## 2. Key Architectural Invariants

1. **The LLM is Never the Source of Truth:**
   - LLMs only assist with candidate claim extraction and vector embedding generation.
   - The status decision (`supported`, `insufficient_evidence`, `specialist_referral`, etc.) is computed exclusively by deterministic Python logic.
2. **Deterministic Precedence Order:**
   $$\text{Prompt Injection Defense} \to \text{Contemporary Fiqh} \to \text{Scholarly Attribution} \to \text{Quran} \to \text{Hadith} \to \text{Historical} \to \text{General}$$
3. **Safe Abstention Standard:**
   - Absence in database $\ne$ Theological falsity.
   - Unverified Hadiths evaluate to `insufficient_evidence`, never automated declarations of fabrication.
4. **Cryptographic Immutability:**
   - Every verified source is indexed with an immutable SHA-256 content hash.
   - Every verification result is appended to a forward-chained hash tree, preventing retrospective tampering.
