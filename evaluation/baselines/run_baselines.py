"""
MUSNAD AI - Baseline Comparison Benchmark Runner
Executes:
1. Baseline A: Naive Generative LLM
2. Baseline B: Basic Semantic Search
3. MUSNAD AI: Multi-Layer RAG + Deterministic Engine + Abstention
Saves raw granular results to evaluation/reports/baseline_raw_results.json
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))
sys.path.insert(0, str(REPO_ROOT / "evaluation" / "baselines"))

from app.core.config import settings
settings.DEMO_MODE = True

from naive_llm import NaiveLLMBaseline
from basic_semantic_search import BasicSemanticSearchBaseline

from app.services.claim_extractor import claim_extractor
from app.rag.retrieval import RetrievedChunk, RetrievalResult
from app.verification.engine import verification_engine
from app.services.text_utils import clean_text_for_matching, strip_attribution, normalize_arabic


async def run_baseline_benchmark():
    test_cases_path = REPO_ROOT / "evaluation" / "test-cases" / "test_cases_v2_50.json"
    with open(test_cases_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    quran_path = REPO_ROOT / "knowledge-base" / "data" / "quran" / "seed_verses.json"
    hadith_path = REPO_ROOT / "knowledge-base" / "data" / "hadith" / "seed_hadiths.json"

    with open(quran_path, "r", encoding="utf-8") as f:
        quran_verses = json.load(f)

    with open(hadith_path, "r", encoding="utf-8") as f:
        hadiths = json.load(f)

    baseline_a = NaiveLLMBaseline()
    baseline_b = BasicSemanticSearchBaseline()

    raw_records = []
    musnad_correct = 0
    base_a_correct = 0
    base_b_correct = 0

    print("=" * 95)
    print("RUNNING INDEPENDENT BASELINE BENCHMARK (50 CASES)")
    print("=" * 95)

    for idx, tc in enumerate(test_cases, start=1):
        tc_id = tc["id"]
        tc_name = tc["name"]
        input_text = tc["input_text"]
        expected_status = tc["expected_status"]
        category = tc["category"]

        # 1. Retrieval for Semantic Baseline & MUSNAD
        retrieved_chunks = []
        clean_input = clean_text_for_matching(strip_attribution(input_text))

        for v in quran_verses:
            v_clean = clean_text_for_matching(v["text"])
            if clean_input in v_clean or v_clean in clean_input:
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

        # Baseline A execution
        base_a_res = baseline_a.evaluate_claim(input_text)
        base_a_pred = base_a_res["status"]

        # Baseline B execution
        base_b_res = baseline_b.evaluate_claim(input_text, retrieved_chunks)
        base_b_pred = base_b_res["status"]

        # MUSNAD execution
        extraction = await claim_extractor.extract(input_text, request_id=tc_id)
        if extraction.claims:
            claim = extraction.claims[0]
        else:
            from app.services.claim_extractor import ExtractedClaim
            claim = ExtractedClaim(
                claim_index=1,
                original_text=input_text,
                normalized_text=normalize_arabic(input_text),
                claim_type=tc.get("claim_type", "unknown"),
            )

        retrieval_res = RetrievalResult(
            claim_text=claim.original_text,
            claim_type=claim.claim_type,
            chunks=retrieved_chunks,
            exact_matches_found=sum(1 for c in retrieved_chunks if c.exact_match),
            total_retrieved=len(retrieved_chunks),
        )
        decision = verification_engine.decide(claim, retrieval_res)
        musnad_pred = decision.status.value

        m_ok = (musnad_pred == expected_status)
        ba_ok = (base_a_pred == expected_status)
        bb_ok = (base_b_pred == expected_status)

        if m_ok: musnad_correct += 1
        if ba_ok: base_a_correct += 1
        if bb_ok: base_b_correct += 1

        raw_records.append({
            "test_id": tc_id,
            "name": tc_name,
            "category": category,
            "input": input_text,
            "expected": expected_status,
            "musnad": {"prediction": musnad_pred, "correct": m_ok, "rules": decision.rules_triggered},
            "baseline_a": {"prediction": base_a_pred, "correct": ba_ok, "meta": base_a_res},
            "baseline_b": {"prediction": base_b_pred, "correct": bb_ok, "meta": base_b_res},
        })

    n = len(test_cases)
    m_acc = (musnad_correct / n) * 100
    ba_acc = (base_a_correct / n) * 100
    bb_acc = (base_b_correct / n) * 100

    # Detailed metrics
    # 1. Fabricated / Adversarial abstention rate
    fake_cases = [r for r in raw_records if r["category"] in ["unsupported_claim", "adversarial_input"]]
    m_abstained = sum(1 for r in fake_cases if r["musnad"]["prediction"] == "insufficient_evidence")
    ba_abstained = sum(1 for r in fake_cases if r["baseline_a"]["prediction"] == "insufficient_evidence")
    bb_abstained = sum(1 for r in fake_cases if r["baseline_b"]["prediction"] == "insufficient_evidence")

    # 2. Specialist Referral Recall on Fiqh Claims
    fiqh_cases = [r for r in raw_records if r["category"] == "fiqh_specialist_referral"]
    m_fiqh_referred = sum(1 for r in fiqh_cases if r["musnad"]["prediction"] == "specialist_referral")
    ba_fiqh_referred = sum(1 for r in fiqh_cases if r["baseline_a"]["prediction"] == "specialist_referral")
    bb_fiqh_referred = sum(1 for r in fiqh_cases if r["baseline_b"]["prediction"] == "specialist_referral")

    print("\n" + "=" * 95)
    print("INDEPENDENT BASELINE BENCHMARK SUMMARY (N=50)")
    print("=" * 95)
    print(f"Overall Accuracy (Correct / Total N):")
    print(f"  • MUSNAD AI:                           {musnad_correct}/{n} ({m_acc:.1f}%)")
    print(f"  • Baseline B (Basic Semantic Search):   {base_b_correct}/{n} ({bb_acc:.1f}%)")
    print(f"  • Baseline A (Naive Generative LLM):    {base_a_correct}/{n} ({ba_acc:.1f}%)")
    print("-" * 95)
    print(f"Abstention on Fabricated/Adversarial Claims (N={len(fake_cases)}):")
    print(f"  • MUSNAD AI:                           {m_abstained}/{len(fake_cases)} ({(m_abstained/len(fake_cases))*100:.1f}%)")
    print(f"  • Baseline B (Basic Semantic Search):   {bb_abstained}/{len(fake_cases)} ({(bb_abstained/len(fake_cases))*100:.1f}%)")
    print(f"  • Baseline A (Naive Generative LLM):    {ba_abstained}/{len(fake_cases)} ({(ba_abstained/len(fake_cases))*100:.1f}%)")
    print("-" * 95)
    print(f"Specialist Referral on Contemporary Fiqh (N={len(fiqh_cases)}):")
    print(f"  • MUSNAD AI:                           {m_fiqh_referred}/{len(fiqh_cases)} ({(m_fiqh_referred/len(fiqh_cases))*100:.1f}%)")
    print(f"  • Baseline B (Basic Semantic Search):   {bb_fiqh_referred}/{len(fiqh_cases)} ({(bb_fiqh_referred/len(fiqh_cases))*100:.1f}%)")
    print(f"  • Baseline A (Naive Generative LLM):    {ba_fiqh_referred}/{len(fiqh_cases)} ({(ba_fiqh_referred/len(fiqh_cases))*100:.1f}%)")
    print("=" * 95)

    reports_dir = REPO_ROOT / "evaluation" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_file = reports_dir / "baseline_raw_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cases": n,
            "metrics": {
                "musnad_accuracy_pct": round(m_acc, 2),
                "baseline_b_accuracy_pct": round(bb_acc, 2),
                "baseline_a_accuracy_pct": round(ba_acc, 2),
                "musnad_abstention_pct": round((m_abstained / len(fake_cases)) * 100, 2),
                "baseline_a_abstention_pct": round((ba_abstained / len(fake_cases)) * 100, 2),
                "musnad_specialist_referral_pct": round((m_fiqh_referred / len(fiqh_cases)) * 100, 2),
            },
            "raw_records": raw_records,
        }, f, ensure_ascii=False, indent=2)

    print(f"Granular raw records saved to: {out_file}")


if __name__ == "__main__":
    asyncio.run(run_baseline_benchmark())
