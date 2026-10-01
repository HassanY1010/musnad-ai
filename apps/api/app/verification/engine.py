"""
MUSNAD AI - Deterministic Verification Engine
Core principle: CLAIM -> EVIDENCE -> SOURCE -> VERIFICATION STATUS -> EXPLANATION -> ABSTENTION

The LLM NEVER directly decides the verification status.
All verification decisions are deterministic and rule-driven.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from app.rag.retrieval import RetrievedChunk, RetrievalResult
from app.services.claim_extractor import ExtractedClaim
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VerificationStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    NEEDS_REVIEW = "needs_review"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    SOURCE_CONFLICT = "source_conflict"
    SPECIALIST_REFERRAL = "specialist_referral"
    PENDING = "pending"
    ERROR = "error"


@dataclass
class VerificationDecision:
    status: VerificationStatus
    evidence_strength: str  # high, medium, low, none
    retrieval_relevance: str
    source_traceability: str
    interpretation_certainty: str
    match_type: str = "none"  # exact, near_exact, lexical, semantic, partial, conflicting, none (Phase 8 Formal Evidence Model)
    rules_triggered: List[str] = field(default_factory=list)
    supporting_chunks: List[RetrievedChunk] = field(default_factory=list)
    conflicting_chunks: List[RetrievedChunk] = field(default_factory=list)
    explanation_ar: str = ""
    abstention_reason: Optional[str] = None
    needs_specialist: bool = False
    textual_difference: Optional[Dict[str, Any]] = None  # Structured textual variant analysis (Phase 3)


def analyze_textual_difference(user_text: str, canonical_text: str) -> Optional[Dict[str, Any]]:
    """
    Structured evidence explanation comparing user quotation to canonical quotation (Phase 3 & Phase 8).
    Identifies exact difference, difference type, similarity, and verification implication.
    """
    if not user_text or not canonical_text:
        return None

    u_words = user_text.split()
    c_words = canonical_text.split()

    diff_u = [w for w in u_words if w not in c_words]
    diff_c = [w for w in c_words if w not in u_words]

    if not diff_u and not diff_c:
        return None

    diff_type = "اختلاف لفظي في الرواية (lexical variant)"
    for wu in diff_u:
        for wc in diff_c:
            if (
                wu + "ت" == wc
                or wu + "ات" == wc
                or wc + "ت" == wu
                or wc + "ات" == wu
                or (wu.endswith("ة") and wc.endswith("ات"))
            ):
                diff_type = "مفرد مقابل جمع (singular vs plural)"
                break

    if any(w in ["و", "ف", "انما", "ثم", "او", "لكل", "وانما"] for w in diff_u + diff_c):
        if diff_type != "مفرد مقابل جمع (singular vs plural)":
            diff_type = "حذف أو زيادة أداة ربط / لفظ يسير (particle variant)"

    set_u, set_c = set(u_words), set(c_words)
    similarity = round(len(set_u & set_c) / max(1, len(set_u | set_c)), 2)

    return {
        "user_quotation": user_text,
        "canonical_quotation": canonical_text,
        "differing_user_words": diff_u,
        "differing_canonical_words": diff_c,
        "difference_type": diff_type,
        "similarity": similarity,
        "verification_implication": (
            f"اللفظ المذكور ({', '.join(diff_u) if diff_u else 'نص مجتزأ'}) يختلف عن اللفظ المعتمد في الرواية المفهرسة "
            f"({', '.join(diff_c) if diff_c else 'الأصل الكامل'}). "
            f"نوع الاختلاف: {diff_type}. لا يحكم بوضع اللفظ، لكنه غير مطابق للمتن المعتمد حرفياً."
        ),
    }


class VerificationEngine:
    HIGH_SCORE = 0.82
    MEDIUM_SCORE = 0.60
    LOW_SCORE = 0.45

    def decide(
        self,
        claim: ExtractedClaim,
        retrieval: RetrievalResult,
        llm_assessment: Optional[Dict[str, Any]] = None,
    ) -> VerificationDecision:
        rules = []

        # 1. Specialist Referral Check
        if claim.needs_specialist or claim.claim_type == "fiqh_claim":
            rules.append("RULE_SPECIALIST_CLAIM_TYPE")
            return VerificationDecision(
                status=VerificationStatus.SPECIALIST_REFERRAL,
                evidence_strength="none",
                retrieval_relevance="none",
                source_traceability="none",
                interpretation_certainty="none",
                match_type="none",
                rules_triggered=rules,
                explanation_ar="هذا الادعاء يتعلق بحكم فقهي أو مسألة اجتهادية دقيقة تتطلب الرجوع للمفتين والمختصين الشرعيين.",
                abstention_reason="specialist_referral_required",
                needs_specialist=True,
            )

        # 2. Check if no chunks retrieved
        if not retrieval.chunks:
            if claim.claim_type in ["historical_claim", "scholarly_quote", "attribution", "source_claim"]:
                rules.append("RULE_UNVERIFIED_HISTORICAL_OR_ATTRIBUTION")
                return VerificationDecision(
                    status=VerificationStatus.NEEDS_REVIEW,
                    evidence_strength="none",
                    retrieval_relevance="none",
                    source_traceability="low",
                    interpretation_certainty="low",
                    match_type="none",
                    rules_triggered=rules,
                    explanation_ar="هذا الادعاء يتعلق بواقعة تاريخية أو نسبة قول لعالم معين أو عزو مصدري؛ يتطلب الرجوع لكتب السير والتراجم والمصادر المخصصة.",
                    abstention_reason="requires_historical_sources",
                )

            rules.append("RULE_NO_EVIDENCE_RETRIEVED")
            return VerificationDecision(
                status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                evidence_strength="none",
                retrieval_relevance="none",
                source_traceability="none",
                interpretation_certainty="none",
                match_type="none",
                rules_triggered=rules,
                explanation_ar="لم نتمكن من إثبات هذا الادعاء من المصادر المتاحة للنظام. هذا لا يعني بالضرورة أن الادعاء خاطئ. يوصى بمراجعته من مختص.",
                abstention_reason="no_evidence_found",
            )

        exact_matches = [c for c in retrieval.chunks if c.exact_match]
        top_score = max((c.final_score for c in retrieval.chunks), default=0.0)

        # 2b. Source attribution claim — check if cited source exists in DB
        if claim.claim_type == "source_claim":
            # If retrieval found matching hadith chunks from the cited source, it's verifiable
            if exact_matches or top_score >= self.MEDIUM_SCORE:
                rules.append("RULE_SOURCE_ATTRIBUTION_VERIFIED")
                return VerificationDecision(
                    status=VerificationStatus.SUPPORTED,
                    evidence_strength="medium",
                    retrieval_relevance="high",
                    source_traceability="high",
                    interpretation_certainty="medium",
                    match_type="exact" if exact_matches else "lexical",
                    rules_triggered=rules,
                    supporting_chunks=exact_matches or [c for c in retrieval.chunks if c.final_score >= self.MEDIUM_SCORE],
                    explanation_ar="تم التحقق من وجود الحديث في المصدر المذكور من خلال السجلات المفهرسة في قاعدة المعرفة.",
                )
            else:
                rules.append("RULE_SOURCE_ATTRIBUTION_UNVERIFIED")
                return VerificationDecision(
                    status=VerificationStatus.NEEDS_REVIEW,
                    evidence_strength="low",
                    retrieval_relevance="low",
                    source_traceability="medium",
                    interpretation_certainty="low",
                    match_type="none",
                    rules_triggered=rules,
                    explanation_ar="لم يتم التحقق من وجود هذا النص في المصدر المذكور بشكل قاطع. يُوصى بمراجعة الكتاب مباشرة.",
                    abstention_reason="source_attribution_unverifiable",
                )

        # 2c. Scholar quote — search for text in DB
        if claim.claim_type == "scholarly_quote":
            if exact_matches:
                rules.append("RULE_SCHOLAR_QUOTE_EXACT")
                return VerificationDecision(
                    status=VerificationStatus.SUPPORTED,
                    evidence_strength="high",
                    retrieval_relevance="high",
                    source_traceability="high",
                    interpretation_certainty="medium",
                    match_type="exact",
                    rules_triggered=rules,
                    supporting_chunks=exact_matches,
                    explanation_ar="تم العثور على القول المنسوب بمطابقة تامة في قاعدة المعرفة.",
                )
            elif top_score >= self.MEDIUM_SCORE:
                rules.append("RULE_SCHOLAR_QUOTE_PARTIAL")
                return VerificationDecision(
                    status=VerificationStatus.PARTIALLY_SUPPORTED,
                    evidence_strength="medium",
                    retrieval_relevance="medium",
                    source_traceability="medium",
                    interpretation_certainty="low",
                    match_type="partial",
                    rules_triggered=rules,
                    supporting_chunks=[c for c in retrieval.chunks if c.final_score >= self.MEDIUM_SCORE],
                    explanation_ar="القول المنسوب قريب المعنى من نصوص محفوظة لكن لم يتم التأكد من دقة العزو أو اللفظ.",
                )
            else:
                rules.append("RULE_SCHOLAR_QUOTE_INSUFFICIENT")
                return VerificationDecision(
                    status=VerificationStatus.NEEDS_REVIEW,
                    evidence_strength="low",
                    retrieval_relevance="low",
                    source_traceability="low",
                    interpretation_certainty="low",
                    match_type="none",
                    rules_triggered=rules,
                    explanation_ar="القول منسوب لعالم لكن لم يُعثر على نصه في قاعدة المعرفة المتاحة. يوصى بمراجعة مصادر الأقوال المخصصة.",
                    abstention_reason="scholar_quote_not_found",
                )
        # 3. Exact Quran Verse Match
        if claim.claim_type == "quran_verse" and exact_matches:

            rules.append("RULE_EXACT_QURAN_MATCH")
            top_chunk = exact_matches[0]
            ref_str = f"سورة {top_chunk.chapter or top_chunk.surah_number} - آية {top_chunk.verse_number}"
            return VerificationDecision(
                status=VerificationStatus.SUPPORTED,
                evidence_strength="high",
                retrieval_relevance="high",
                source_traceability="high",
                interpretation_certainty="high",
                match_type="exact",
                rules_triggered=rules,
                supporting_chunks=exact_matches,
                explanation_ar=f"تم التحقق بنجاح من نص الآية الكريمة بمطابقة تامة مع المصحف الشريف ({ref_str}).",
            )

        # 4. Exact Hadith Match
        if claim.claim_type == "hadith" and exact_matches:
            rules.append("RULE_EXACT_HADITH_MATCH")
            top_chunk = exact_matches[0]
            ref_str = f"{top_chunk.source_title} - رقم {top_chunk.hadith_number or ''}"
            grading_str = f" (الحكم: {top_chunk.grading})" if top_chunk.grading else ""
            return VerificationDecision(
                status=VerificationStatus.SUPPORTED,
                evidence_strength="high",
                retrieval_relevance="high",
                source_traceability="high",
                interpretation_certainty="high",
                match_type="exact",
                rules_triggered=rules,
                supporting_chunks=exact_matches,
                explanation_ar=f"تم التحقق من الحديث الشريف بمطابقة تامة في {ref_str}{grading_str}.",
            )

        # 5. Check for conflicts
        conflicting = [c for c in retrieval.chunks if getattr(c, 'support_type', '') == 'contradictory']
        if conflicting:
            rules.append("RULE_CONFLICT_DETECTED")
            return VerificationDecision(
                status=VerificationStatus.SOURCE_CONFLICT,
                evidence_strength="medium",
                retrieval_relevance="medium",
                source_traceability="high",
                interpretation_certainty="low",
                match_type="conflicting",
                rules_triggered=rules,
                supporting_chunks=[c for c in retrieval.chunks if c not in conflicting],
                conflicting_chunks=conflicting,
                explanation_ar="يوجد تعارض أو تباين في الروايات أو الألفاظ بين المصادر المعتمدة المسجلة.",
                abstention_reason="source_conflict_detected",
            )

        # 6. High Score Semantic / Lexical Support
        high_supporting = [c for c in retrieval.chunks if c.final_score >= self.HIGH_SCORE]
        medium_supporting = [c for c in retrieval.chunks if self.MEDIUM_SCORE <= c.final_score < self.HIGH_SCORE]

        if high_supporting:
            rules.append("RULE_HIGH_SEMANTIC_SUPPORT")
            match_type_val = "near_exact" if top_score >= 0.90 else "lexical"
            return VerificationDecision(
                status=VerificationStatus.SUPPORTED,
                evidence_strength="high",
                retrieval_relevance="high",
                source_traceability="high",
                interpretation_certainty="medium",
                match_type=match_type_val,
                rules_triggered=rules,
                supporting_chunks=high_supporting,
                explanation_ar=self._extract_llm_explanation(llm_assessment) or "تم العثور على شواهد نصية قوية تسند الادعاء من المصادر المعتمدة.",
            )

        # 7. Partial Support with Structured Textual Variant Analysis
        if medium_supporting and top_score >= self.MEDIUM_SCORE:
            rules.append("RULE_PARTIAL_SEMANTIC_SUPPORT")
            top_candidate = medium_supporting[0]
            diff = analyze_textual_difference(
                claim.normalized_text or claim.original_text,
                top_candidate.text_normalized or top_candidate.text,
            )
            base_exp = self._extract_llm_explanation(llm_assessment) or "النصوص المسترجعة تؤيد المعنى العام للادعاء مع وجود فروق في السياق أو الصياغة."
            if diff:
                exp_with_diff = (
                    f"{base_exp}\n"
                    f"[تحليل الفروق: {diff['difference_type']} — اللفظ الوارد: {', '.join(diff['differing_user_words'])} "
                    f"مقابل اللفظ المعتمد: {', '.join(diff['differing_canonical_words'])}]"
                )
            else:
                exp_with_diff = base_exp

            return VerificationDecision(
                status=VerificationStatus.PARTIALLY_SUPPORTED,
                evidence_strength="medium",
                retrieval_relevance="medium",
                source_traceability="medium",
                interpretation_certainty="medium",
                match_type="partial",
                rules_triggered=rules,
                supporting_chunks=medium_supporting,
                explanation_ar=exp_with_diff,
                textual_difference=diff,
            )

        # 8. Needs Review
        low_supporting = [c for c in retrieval.chunks if self.LOW_SCORE <= c.final_score < self.MEDIUM_SCORE]
        if low_supporting:
            rules.append("RULE_MEDIUM_SEMANTIC_SUPPORT")
            return VerificationDecision(
                status=VerificationStatus.NEEDS_REVIEW,
                evidence_strength="low",
                retrieval_relevance="medium",
                source_traceability="low",
                interpretation_certainty="low",
                match_type="semantic",
                rules_triggered=rules,
                supporting_chunks=low_supporting,
                explanation_ar=self._extract_llm_explanation(llm_assessment) or "الشواهد المسترجعة غير حاسمة وتحتاج إلى مراجعة وتدقيق إضافي.",
            )

        # 9. Below Threshold -> Insufficient Evidence
        rules.append("RULE_BELOW_THRESHOLD")
        return VerificationDecision(
            status=VerificationStatus.INSUFFICIENT_EVIDENCE,
            evidence_strength="none",
            retrieval_relevance="low",
            source_traceability="low",
            interpretation_certainty="none",
            match_type="none",
            rules_triggered=rules,
            explanation_ar="لم نتمكن من إثبات هذا الادعاء من المصادر المتاحة للنظام. هذا لا يعني بالضرورة أن الادعاء خاطئ. يوصى بمراجعته من مختص.",
            abstention_reason="below_relevance_threshold",
        )

    def _score_to_level(self, score: float) -> str:
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.3:
            return "low"
        return "none"

    def _get_llm_support_level(self, assessment: Optional[Dict[str, Any]]) -> str:
        if not assessment:
            return "unknown"
        return assessment.get("support_level", "unknown")

    def _extract_llm_explanation(self, assessment: Optional[Dict[str, Any]]) -> Optional[str]:
        if not assessment:
            return None
        return assessment.get("explanation_ar") or assessment.get("explanation")


verification_engine = VerificationEngine()
