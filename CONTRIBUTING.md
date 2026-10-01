# Contributing to MUSNAD AI

Thank you for your interest in contributing to **MUSNAD AI — AI Evidence & Verification Engine for Islamic Digital Content**.

## Guiding Principles
1. **Never Fabricate:** We never invent citations, accuracy numbers, or scholarly gradings.
2. **Deterministic Precedence:** The LLM is an interpretive assistant, never the arbiter of truth. Verification status is deterministically computed.
3. **Traceability:** Every claimed evidence must trace back to a verifiable source, edition, chunk, and authority.
4. **Honest Abstention:** When an indexed source cannot substantiate a claim, abstaining (`insufficient_evidence`) is strictly preferred over ungrounded speculation.

## Development Workflow
1. Fork and clone the repository.
2. Setup Backend:
   ```bash
   cd apps/api
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Setup Frontend:
   ```bash
   cd apps/web
   npm install
   npm run build
   ```
4. Run Tests & Evaluation:
   ```bash
   python scripts/run_evaluation.py --suite v2
   ```

## Scholarly Source Submission
When submitting knowledge sources for ingestion:
- Provide bibliographic metadata (Title, Author, Publisher, Year, Edition, License, Hash).
- Ensure copyright clearance / open academic licensing.
- Never commit copyrighted digital texts without explicit distribution rights.
