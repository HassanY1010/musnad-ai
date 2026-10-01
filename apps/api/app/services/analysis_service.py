"""
MUSNAD AI - Analysis Service Orchestrator
Coordinates: Claim Extraction -> Hybrid Retrieval -> Verification Engine -> Database Persistence
"""
import uuid
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    Analysis, Claim, Evidence, VerificationResult,
    Source, SourceChunk, AnalysisStatus, InputType,
    VerificationStatus as DBVerificationStatus,
    MatchType, SupportType
)
from app.services.claim_extractor import claim_extractor, ExtractedClaim
from app.services.llm_provider import llm_provider, LLMCallError
from app.rag.retrieval import hybrid_retriever, RetrievalResult
from app.verification.engine import verification_engine, VerificationStatus, VerificationDecision
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ClaimResult:
    """Complete result for a single claim."""
    claim_id: str
    claim_index: int
    original_text: str
    normalized_text: str
    claim_type: str
    status: str
    status_label_ar: str
    status_color: str
    evidence_strength: str
    source_traceability: str
    interpretation_certainty: str
    explanation_ar: str
    abstention_reason: Optional[str]
    has_exact_match: bool
    has_conflict: bool
    rules_triggered: List[str]
    supporting_evidence: List[Dict[str, Any]]
    conflicting_evidence: List[Dict[str, Any]]
    needs_specialist: bool


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    analysis_id: str
    processing_status: str
    total_claims: int
    claims: List[ClaimResult]
    summary: Dict[str, Any]
    language_detected: str
    kb_version: str
    model: str


class AnalysisOrchestrator:
    async def run(
        self,
        db: AsyncSession,
        content: str,
        analysis_id: str,
        user_id: Optional[str] = None,
    ) -> AnalysisResult:
        analysis = await db.get(Analysis, analysis_id)
        if analysis:
            analysis.processing_status = AnalysisStatus.processing
            await db.commit()

        try:
            extraction = await claim_extractor.extract(content, request_id=analysis_id)
            claim_results: List[ClaimResult] = []

            for extracted_claim in extraction.claims:
                claim_res = await self._process_claim(db, analysis_id, extracted_claim)
                claim_results.append(claim_res)
                await db.commit()

            summary = self._compute_summary(claim_results)

            if analysis:
                analysis.processing_status = AnalysisStatus.completed
                await db.commit()

            logger.info("analysis_complete", analysis_id=analysis_id, total_claims=len(claim_results))

            return AnalysisResult(
                analysis_id=analysis_id,
                processing_status="completed",
                total_claims=len(claim_results),
                claims=claim_results,
                summary=summary,
                language_detected=extraction.language_detected,
                kb_version=settings.KB_VERSION,
                model=settings.GEMINI_MODEL,
            )

        except Exception as e:
            logger.error("analysis_failed", analysis_id=analysis_id, error=str(e))
            if analysis:
                analysis.processing_status = AnalysisStatus.failed
                analysis.error_message = str(e)
                await db.commit()
            raise

    async def _process_claim(
        self,
        db: AsyncSession,
        analysis_id: str,
        extracted_claim: ExtractedClaim,
    ) -> ClaimResult:
        claim_id = str(uuid.uuid4())

        # 1. Retrieve evidence
        retrieval: RetrievalResult = await hybrid_retriever.retrieve(
            db=db,
            claim_text=extracted_claim.original_text,
            claim_type=extracted_claim.claim_type,
            top_k=settings.RETRIEVAL_TOP_K,
        )

        # 2. Deterministic Verification Decision
        decision: VerificationDecision = verification_engine.decide(
            claim=extracted_claim,
            retrieval=retrieval,
        )

        # 3. Persist Claim
        db_claim = Claim(
            id=claim_id,
            analysis_id=analysis_id,
            claim_index=extracted_claim.claim_index,
            original_text=extracted_claim.original_text,
            normalized_text=extracted_claim.normalized_text,
            claim_type=extracted_claim.claim_type,
            entities={"entities": extracted_claim.entities},
            references={"references": extracted_claim.references},
            attributions={"attributions": extracted_claim.attributions},
            needs_specialist=extracted_claim.needs_specialist or decision.needs_specialist,
            specialist_reason=extracted_claim.specialist_reason or decision.explanation_ar,
            extraction_confidence=extracted_claim.extraction_confidence,
        )
        db.add(db_claim)

        # 4. Persist Evidence
        supporting_evidence = []
        for rank, chunk in enumerate(decision.supporting_chunks, start=1):
            ev_id = str(uuid.uuid4())
            match_type_val = MatchType.exact if chunk.exact_match else MatchType.semantic
            db_ev = Evidence(
                id=ev_id,
                claim_id=claim_id,
                chunk_id=chunk.chunk_id,
                match_type=match_type_val,
                relevance_score=chunk.final_score,
                support_type=SupportType.direct if chunk.exact_match else SupportType.partial,
                explanation=chunk.text[:200],
                retrieval_rank=rank,
            )
            db.add(db_ev)

            supporting_evidence.append({
                "chunk_id": chunk.chunk_id,
                "source_code": chunk.source_code,
                "source_title": chunk.source_title,
                "source_title_ar": chunk.source_title_ar,
                "source_type": chunk.source_type,
                "author": chunk.author,
                "author_ar": chunk.author_ar,
                "edition": chunk.edition,
                "text": chunk.text,
                "page": chunk.page,
                "chapter": chunk.chapter,
                "hadith_number": chunk.hadith_number,
                "surah_number": chunk.surah_number,
                "verse_number": chunk.verse_number,
                "reference": chunk.reference,
                "grading": chunk.grading,
                "grading_authority": chunk.grading_authority,
                "exact_match": chunk.exact_match,
                "retrieval_method": chunk.retrieval_method,
                "relevance_score": chunk.final_score,
            })

        conflicting_evidence = []
        for rank, chunk in enumerate(decision.conflicting_chunks, start=1):
            conflicting_evidence.append({
                "chunk_id": chunk.chunk_id,
                "source_code": chunk.source_code,
                "source_title": chunk.source_title,
                "source_title_ar": chunk.source_title_ar,
                "source_type": chunk.source_type,
                "author": chunk.author,
                "author_ar": chunk.author_ar,
                "edition": chunk.edition,
                "text": chunk.text,
                "page": chunk.page,
                "chapter": chunk.chapter,
                "hadith_number": chunk.hadith_number,
                "surah_number": chunk.surah_number,
                "verse_number": chunk.verse_number,
                "reference": chunk.reference,
                "grading": chunk.grading,
                "grading_authority": chunk.grading_authority,
                "exact_match": chunk.exact_match,
                "retrieval_method": chunk.retrieval_method,
                "relevance_score": chunk.final_score,
            })

        # 5. Persist VerificationResult (Float columns in DB)
        def _to_float(val: Any) -> float:
            if isinstance(val, (int, float)):
                return float(val)
            s_map = {"high": 1.0, "medium": 0.65, "low": 0.35, "none": 0.0}
            return s_map.get(str(val).lower(), 0.0)

        db_vr = VerificationResult(
            id=str(uuid.uuid4()),
            claim_id=claim_id,
            status=decision.status.value,
            evidence_strength=_to_float(decision.evidence_strength),
            retrieval_relevance=_to_float(decision.retrieval_relevance),
            source_traceability=_to_float(decision.source_traceability),
            interpretation_certainty=_to_float(decision.interpretation_certainty),
            explanation=decision.explanation_ar,
            explanation_ar=decision.explanation_ar,
            rules_triggered=decision.rules_triggered,
            abstention_reason=decision.abstention_reason,
        )
        db.add(db_vr)

        has_exact = any(c.exact_match for c in decision.supporting_chunks)
        has_conflict = len(decision.conflicting_chunks) > 0

        status_labels = {
            "supported": "مدعوم",
            "partially_supported": "مدعوم جزئياً",
            "needs_review": "يحتاج إلى مراجعة",
            "insufficient_evidence": "دليل غير كافٍ",
            "source_conflict": "تعارض في المصادر",
            "specialist_referral": "يحتاج إلى مختص",
            "pending": "قيد المعالجة",
        }
        status_colors = {
            "supported": "green",
            "partially_supported": "blue",
            "needs_review": "yellow",
            "insufficient_evidence": "gray",
            "source_conflict": "orange",
            "specialist_referral": "red",
            "pending": "gray",
        }

        st_val = decision.status.value
        return ClaimResult(
            claim_id=claim_id,
            claim_index=extracted_claim.claim_index,
            original_text=extracted_claim.original_text,
            normalized_text=extracted_claim.normalized_text,
            claim_type=extracted_claim.claim_type,
            status=st_val,
            status_label_ar=status_labels.get(st_val, st_val),
            status_color=status_colors.get(st_val, "gray"),
            evidence_strength=decision.evidence_strength,
            source_traceability=decision.source_traceability,
            interpretation_certainty=decision.interpretation_certainty,
            explanation_ar=decision.explanation_ar,
            abstention_reason=decision.abstention_reason,
            has_exact_match=has_exact,
            has_conflict=has_conflict,
            rules_triggered=decision.rules_triggered,
            supporting_evidence=supporting_evidence,
            conflicting_evidence=conflicting_evidence,
            needs_specialist=extracted_claim.needs_specialist or decision.status == VerificationStatus.SPECIALIST_REFERRAL,
        )

    def _compute_summary(self, claims: List[ClaimResult]) -> Dict[str, Any]:
        total = len(claims)
        status_counts = {}
        for claim in claims:
            status_counts[claim.status] = status_counts.get(claim.status, 0) + 1

        return {
            "total": total,
            "supported": status_counts.get("supported", 0),
            "partially_supported": status_counts.get("partially_supported", 0),
            "needs_review": status_counts.get("needs_review", 0),
            "insufficient_evidence": status_counts.get("insufficient_evidence", 0),
            "source_conflict": status_counts.get("source_conflict", 0),
            "specialist_referral": status_counts.get("specialist_referral", 0),
            "has_exact_matches": any(c.has_exact_match for c in claims),
            "has_conflicts": any(c.has_conflict for c in claims),
        }


analysis_orchestrator = AnalysisOrchestrator()
