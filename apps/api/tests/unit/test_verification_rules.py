"""
Unit tests for VerificationEngine rules and deterministic behavior.
"""
import pytest
from app.verification.engine import VerificationEngine, VerificationStatus
from app.services.claim_extractor import ExtractedClaim
from app.rag.retrieval import RetrievalResult, RetrievedChunk

@pytest.fixture
def engine():
    return VerificationEngine()

def test_fiqh_claim_triggers_specialist_referral(engine):
    claim = ExtractedClaim(
        claim_index=1,
        original_text="حكم تداول العملات الرقمية",
        normalized_text="حكم تداول العملات الرقميه",
        claim_type="fiqh_claim",
        needs_specialist=True
    )
    retrieval = RetrievalResult(claim_text=claim.original_text, claim_type=claim.claim_type)
    decision = engine.decide(claim, retrieval)
    
    assert decision.status == VerificationStatus.SPECIALIST_REFERRAL
    assert decision.needs_specialist is True
    assert "RULE_SPECIALIST_CLAIM_TYPE" in decision.rules_triggered

def test_empty_retrieval_triggers_safe_abstention(engine):
    claim = ExtractedClaim(
        claim_index=1,
        original_text="حديث مكذوب لا أصل له",
        normalized_text="حديث مكذوب لا اصل له",
        claim_type="hadith"
    )
    retrieval = RetrievalResult(claim_text=claim.original_text, claim_type=claim.claim_type, chunks=[])
    decision = engine.decide(claim, retrieval)
    
    assert decision.status == VerificationStatus.INSUFFICIENT_EVIDENCE
    assert decision.abstention_reason == "no_evidence_found"
    assert "RULE_NO_EVIDENCE_RETRIEVED" in decision.rules_triggered

def test_exact_quran_match_decision(engine):
    chunk = RetrievedChunk(
        chunk_id="chk-001",
        source_id="src-001",
        source_code="SRC-001",
        source_title="القرآن الكريم",
        source_title_ar="القرآن الكريم",
        source_type="QURAN",
        author="كلام الله",
        author_ar="كلام الله",
        edition="مصحف المدينة",
        text="قُلْ هُوَ اللَّهُ أَحَدٌ",
        text_normalized="قل هو الله احد",
        page="604",
        chapter="الإخلاص",
        section=None,
        hadith_number=None,
        surah_number=112,
        verse_number=1,
        reference="سورة الإخلاص - آية 1",
        grading=None,
        grading_authority=None,
        exact_match=True,
        final_score=1.0
    )
    claim = ExtractedClaim(
        claim_index=1,
        original_text="قل هو الله أحد",
        normalized_text="قل هو الله احد",
        claim_type="quran_verse"
    )
    retrieval = RetrievalResult(
        claim_text=claim.original_text,
        claim_type=claim.claim_type,
        chunks=[chunk],
        exact_matches_found=1
    )
    decision = engine.decide(claim, retrieval)
    
    assert decision.status == VerificationStatus.SUPPORTED
    assert decision.match_type == "exact"
    assert "RULE_EXACT_QURAN_MATCH" in decision.rules_triggered
