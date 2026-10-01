"""
MUSNAD AI - Adversarial Attack & Robustness Verification Runner
Executes 20 targeted adversarial attacks including:
- Prompt injection (English / Arabic)
- System prompt exfiltration
- Unicode zero-width tricks & tatweel evasion
- SQL injection / XSS tags
- Quran corruption (single-letter alteration)
- Forged scholarly consensus
- Bogus citations & modern anachronisms
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from app.core.config import settings
settings.DEMO_MODE = True

from app.services.claim_extractor import claim_extractor
from app.rag.retrieval import RetrievedChunk, RetrievalResult
from app.verification.engine import verification_engine
from app.services.text_utils import clean_text_for_matching, strip_attribution, normalize_arabic


async def run_adversarial_suite():
    adv_path = REPO_ROOT / "evaluation" / "test-cases" / "adversarial_v1.json"
    with open(adv_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    quran_path = REPO_ROOT / "knowledge-base" / "data" / "quran" / "seed_verses.json"
    hadith_path = REPO_ROOT / "knowledge-base" / "data" / "hadith" / "seed_hadiths.json"

    with open(quran_path, "r", encoding="utf-8") as f:
        quran_verses = json.load(f)
    with open(hadith_path, "r", encoding="utf-8") as f:
        hadiths = json.load(f)

    print("=" * 95)
    print("MUSNAD AI — ADVERSARIAL ATTACK & INJECTION ROBUSTNESS BENCHMARK (N=20)")
    print("=" * 95)

    results = []
    passed = 0

    for idx, tc in enumerate(cases, start=1):
        adv_id = tc["id"]
        adv_name = tc["name"]
        attack_type = tc["attack_type"]
        input_text = tc["input_text"]
        expected_status = tc["expected_status"]

        # Step 1: Claim Extraction & Normalization
        extraction = await claim_extractor.extract(input_text, request_id=adv_id)
        if extraction.claims:
            claim = extraction.claims[0]
            claim_text = claim.original_text
            claim_type = claim.claim_type
        else:
            from app.services.claim_extractor import ExtractedClaim
            claim_text = input_text
            claim_type = "unknown"
            claim = ExtractedClaim(
                claim_index=1,
                original_text=input_text,
                normalized_text=normalize_arabic(input_text),
                claim_type="unknown",
            )

        # Step 2: Retrieval
        clean_input = clean_text_for_matching(strip_attribution(claim_text))
        retrieved_chunks = []

        # Check individual Quran verses
        for v in quran_verses:
            v_clean = clean_text_for_matching(v["text"])
            if clean_input and (clean_input in v_clean or (v_clean in clean_input and len(v_clean) >= len(clean_input) * 0.85)):
                is_exact = (clean_input == v_clean or clean_input in v_clean or (v_clean in clean_input and len(v_clean) >= len(clean_input) * 0.9))
                retrieved_chunks.append(
                    RetrievedChunk(
                        chunk_id=f"quran_{v['surah_number']}_{v['verse_number']}",
                        source_id="src_quran",
                        source_code="SRC-001",
                        source_title="القرآن الكريم",
                        source_title_ar="القرآن الكريم",
                        source_type="quran",
                        author="كلام الله تعالى",
                        author_ar="كلام الله تعالى",
                        edition="مصحف المدينة",
                        text=v["text"],
                        text_normalized=v_clean,
                        page=None,
                        chapter=v["surah_name_ar"],
                        section=None,
                        hadith_number=None,
                        surah_number=v["surah_number"],
                        verse_number=v["verse_number"],
                        reference=v["reference"],
                        grading=None,
                        grading_authority=None,
                        exact_match=is_exact,
                        final_score=1.0 if is_exact else 0.8,
                    )
                )

        # Check combined surah text for multi-verse quotations (e.g. complete Al-Ikhlas)
        surah_map = {}
        for v in quran_verses:
            surah_map.setdefault(v["surah_number"], []).append(v)

        for s_num, s_verses in surah_map.items():
            if len(s_verses) > 1:
                combined_clean = " ".join(clean_text_for_matching(v["text"]) for v in s_verses)
                if clean_input and clean_input == combined_clean:
                    v0 = s_verses[0]
                    retrieved_chunks.append(
                        RetrievedChunk(
                            chunk_id=f"quran_surah_{s_num}",
                            source_id="src_quran",
                            source_code="SRC-001",
                            source_title="القرآن الكريم",
                            source_title_ar="القرآن الكريم",
                            source_type="quran",
                            author="كلام الله تعالى",
                            author_ar="كلام الله تعالى",
                            edition="مصحف المدينة",
                            text=" ".join(v["text"] for v in s_verses),
                            text_normalized=combined_clean,
                            page=None,
                            chapter=v0["surah_name_ar"],
                            section=None,
                            hadith_number=None,
                            surah_number=s_num,
                            verse_number=1,
                            reference=f"سورة {v0['surah_name_ar']} (كاملة)",
                            grading=None,
                            grading_authority=None,
                            exact_match=True,
                            final_score=1.0,
                        )
                    )

        for h in hadiths:
            h_clean = clean_text_for_matching(h["text"])
            words_h = set(h_clean.split())
            words_in = set(clean_input.split())
            overlap = len(words_h & words_in) / max(1, len(words_in))

            if clean_input in h_clean or h_clean in clean_input or overlap >= 0.5:
                is_exact = (overlap >= 0.8 or clean_input in h_clean or h_clean in clean_input)
                retrieved_chunks.append(
                    RetrievedChunk(
                        chunk_id=f"hadith_{h.get('hadith_number')}",
                        source_id="src_hadith",
                        source_code=h.get("source_code", "SRC-002"),
                        source_title=h.get("book", "صحيح البخاري"),
                        source_title_ar=h.get("book", "صحيح البخاري"),
                        source_type="hadith",
                        author=None,
                        author_ar=None,
                        edition=None,
                        text=h["text"],
                        text_normalized=h_clean,
                        page=None,
                        chapter=h.get("chapter"),
                        section=None,
                        hadith_number=h.get("hadith_number"),
                        surah_number=None,
                        verse_number=None,
                        reference=h.get("reference"),
                        grading=h.get("grading"),
                        grading_authority=h.get("grading_authority"),
                        exact_match=is_exact,
                        final_score=1.0 if is_exact else overlap,
                    )
                )

        retrieval_res = RetrievalResult(
            claim_text=claim.original_text,
            claim_type=claim.claim_type,
            chunks=retrieved_chunks,
            exact_matches_found=sum(1 for c in retrieved_chunks if c.exact_match),
            total_retrieved=len(retrieved_chunks),
        )

        # Step 3: Verification Decision
        decision = verification_engine.decide(claim, retrieval_res)
        actual_status = decision.status.value

        is_passed = (actual_status == expected_status)
        if is_passed:
            passed += 1

        sym = "✓ SAFE" if is_passed else "✗ FAILED"
        print(f"[{sym}] {adv_id} | {attack_type[:24]:<24} | Exp: {expected_status:<22} | Act: {actual_status}")

        results.append({
            "id": adv_id,
            "name": adv_name,
            "attack_type": attack_type,
            "input": input_text,
            "expected_status": expected_status,
            "actual_status": actual_status,
            "passed": is_passed,
            "rules_triggered": decision.rules_triggered,
            "explanation": decision.explanation_ar,
        })

    rate = (passed / len(cases)) * 100
    print("\n" + "=" * 95)
    print(f"ADVERSARIAL SUITE SUMMARY: {passed}/{len(cases)} Attacks Neutralized ({rate:.1f}%)")
    print("=" * 95)

    reports_dir = REPO_ROOT / "evaluation" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_file = reports_dir / "adversarial_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_adversarial_tests": len(cases),
            "neutralized_attacks": passed,
            "defense_rate_pct": round(rate, 2),
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"Report saved to: {out_file}")


if __name__ == "__main__":
    asyncio.run(run_adversarial_suite())
