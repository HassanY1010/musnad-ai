"""
MUSNAD AI - Analysis Endpoints
Core verification workflow.
"""
import json
import uuid
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user_optional, TokenData
from app.models import Analysis, Claim, VerificationResult, Evidence, SourceChunk, Source, InputType, AnalysisStatus
from app.schemas import (
    AnalysisCreateRequest, AnalysisResponse, APIResponse,
    ClaimResponse, EvidenceItem, AnalysisSummary
)
from app.services.analysis_service import analysis_orchestrator, ClaimResult
from app.core.config import settings
from app.core.logging import get_logger
from sqlalchemy import func

logger = get_logger(__name__)
router = APIRouter()


def _parse_rules(rules_val: Any) -> list:
    if not rules_val:
        return []
    if isinstance(rules_val, list):
        return rules_val
    if isinstance(rules_val, dict):
        return rules_val.get("rules", [])
    if isinstance(rules_val, str):
        try:
            parsed = json.loads(rules_val)
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return parsed.get("rules", [])
        except Exception:
            return [rules_val]
    return []


def _float_to_strength(val: Any) -> str:
    if val is None:
        return "none"
    if isinstance(val, str):
        return val
    try:
        f = float(val)
        if f >= 0.8:
            return "high"
        elif f >= 0.5:
            return "medium"
        elif f > 0.0:
            return "low"
        return "none"
    except Exception:
        return "none"



def _claim_to_response(claim_result: ClaimResult) -> ClaimResponse:
    return ClaimResponse(
        claim_id=claim_result.claim_id,
        claim_index=claim_result.claim_index,
        original_text=claim_result.original_text,
        normalized_text=claim_result.normalized_text,
        claim_type=claim_result.claim_type,
        status=claim_result.status,
        status_label_ar=claim_result.status_label_ar,
        status_color=claim_result.status_color,
        evidence_strength=claim_result.evidence_strength,
        source_traceability=claim_result.source_traceability,
        interpretation_certainty=claim_result.interpretation_certainty,
        explanation_ar=claim_result.explanation_ar,
        abstention_reason=claim_result.abstention_reason,
        has_exact_match=claim_result.has_exact_match,
        has_conflict=claim_result.has_conflict,
        rules_triggered=claim_result.rules_triggered,
        supporting_evidence=[EvidenceItem(**e) for e in claim_result.supporting_evidence],
        conflicting_evidence=[EvidenceItem(**e) for e in claim_result.conflicting_evidence],
        needs_specialist=claim_result.needs_specialist,
    )


@router.post("/analyses", response_model=APIResponse, tags=["Analysis"])
async def create_analysis(
    request: AnalysisCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_current_user_optional),
):
    """
    Submit content for Islamic verification analysis.
    Returns a complete analysis with claims, evidence, and verification statuses.
    """
    analysis_id = str(uuid.uuid4())
    user_id = current_user.user_id if current_user else None

    # Create analysis record
    analysis = Analysis(
        id=analysis_id,
        user_id=user_id,
        input_type=InputType.TEXT,
        original_content=request.content,
        processing_status=AnalysisStatus.QUEUED,
        app_version=settings.APP_VERSION,
        prompt_version=settings.PROMPT_VERSION,
        model=settings.GEMINI_MODEL,
        kb_version=settings.KB_VERSION,
        retrieval_config={
            "top_k": settings.RETRIEVAL_TOP_K,
            "semantic_threshold": settings.SEMANTIC_THRESHOLD,
            "abstention_threshold": settings.ABSTENTION_THRESHOLD,
        }
    )
    db.add(analysis)
    await db.commit()

    logger.info("analysis_created", analysis_id=analysis_id, user_id=user_id)

    # Run analysis synchronously for MVP (async queue for production)
    try:
        # --- Runtime Provenance: count actual KB records ---
        kb_count_result = await db.execute(select(func.count()).select_from(SourceChunk))
        kb_record_count = kb_count_result.scalar() or 0

        result = await analysis_orchestrator.run(
            db=db,
            content=request.content,
            analysis_id=analysis_id,
            user_id=user_id,
        )

        logger.info(
            "analysis_complete_debug",
            analysis_id=analysis_id,
            total_claims=result.total_claims,
            kb_version=result.kb_version,
            kb_record_count=kb_record_count,
        )

        return APIResponse(
            success=True,
            data=AnalysisResponse(
                analysis_id=result.analysis_id,
                processing_status=result.processing_status,
                total_claims=result.total_claims,
                claims=[_claim_to_response(c) for c in result.claims],
                summary=AnalysisSummary(**result.summary),
                language_detected=result.language_detected,
                kb_version=result.kb_version,
                model=result.model,
                kb_record_count=kb_record_count,
            )
        )

    except Exception as e:
        logger.error("analysis_endpoint_error", error=str(e), analysis_id=analysis_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "ANALYSIS_FAILED",
                "message": "تعذر إكمال التحليل. يرجى المحاولة مرة أخرى.",
            }
        )


@router.get("/analyses/{analysis_id}", response_model=APIResponse, tags=["Analysis"])
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[TokenData] = Depends(get_current_user_optional),
):
    """Get a specific analysis by ID."""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Analysis not found"},
        )

    # Load claims with their results
    result = await db.execute(
        select(Claim).where(Claim.analysis_id == analysis_id).order_by(Claim.claim_index)
    )
    claims = result.scalars().all()

    claim_responses = []
    for claim in claims:
        vr_result = await db.execute(
            select(VerificationResult).where(VerificationResult.claim_id == claim.id)
        )
        vr = vr_result.scalar_one_or_none()

        # Load evidence
        ev_result = await db.execute(
            select(Evidence, SourceChunk, Source)
            .join(SourceChunk, Evidence.chunk_id == SourceChunk.id)
            .join(Source, SourceChunk.source_id == Source.id)
            .where(Evidence.claim_id == claim.id)
            .order_by(Evidence.retrieval_rank)
        )
        evidence_rows = ev_result.all()

        supporting_evidence = []
        for ev, chunk, source in evidence_rows:
            supporting_evidence.append(EvidenceItem(
                chunk_id=chunk.id,
                source_code=source.source_code,
                source_title=source.title,
                source_title_ar=source.title_ar,
                source_type=source.source_type.value,
                author=source.author,
                author_ar=source.author_ar,
                edition=source.edition,
                text=chunk.text,
                page=chunk.page,
                chapter=chunk.chapter,
                hadith_number=chunk.hadith_number,
                surah_number=chunk.surah_number,
                verse_number=chunk.verse_number,
                reference=chunk.reference,
                grading=chunk.grading,
                grading_authority=chunk.grading_authority,
                exact_match=(ev.match_type.value == "exact"),
                retrieval_method=ev.match_type.value,
                relevance_score=ev.relevance_score,
            ))

        has_exact = any(ev.exact_match for ev in supporting_evidence)
        claim_responses.append(ClaimResponse(
            claim_id=claim.id,
            claim_index=claim.claim_index,
            original_text=claim.original_text,
            normalized_text=claim.normalized_text,
            claim_type=claim.claim_type.value if hasattr(claim.claim_type, "value") else str(claim.claim_type),
            status=vr.status.value if vr and hasattr(vr.status, "value") else (str(vr.status) if vr else "pending"),
            status_label_ar=_status_label(vr.status.value if vr and hasattr(vr.status, "value") else (str(vr.status) if vr else "pending")),
            status_color=_status_color(vr.status.value if vr and hasattr(vr.status, "value") else (str(vr.status) if vr else "pending")),
            evidence_strength=_float_to_strength(vr.evidence_strength) if vr else "none",
            source_traceability=_float_to_strength(vr.source_traceability) if vr else "none",
            interpretation_certainty=_float_to_strength(vr.interpretation_certainty) if vr else "none",
            explanation_ar=vr.explanation_ar or "" if vr else "",
            abstention_reason=vr.abstention_reason if vr else None,
            has_exact_match=has_exact,
            has_conflict=False,
            rules_triggered=_parse_rules(vr.rules_triggered) if vr else [],
            supporting_evidence=supporting_evidence,
            conflicting_evidence=[],
            needs_specialist=claim.needs_specialist,
        ))

    # Summary
    status_counts = {}
    for cr in claim_responses:
        status_counts[cr.status] = status_counts.get(cr.status, 0) + 1

    summary = AnalysisSummary(
        total=len(claim_responses),
        supported=status_counts.get("supported", 0),
        partially_supported=status_counts.get("partially_supported", 0),
        needs_review=status_counts.get("needs_review", 0),
        insufficient_evidence=status_counts.get("insufficient_evidence", 0),
        source_conflict=status_counts.get("source_conflict", 0),
        specialist_referral=status_counts.get("specialist_referral", 0),
        has_exact_matches=any(cr.has_exact_match for cr in claim_responses),
        has_conflicts=any(cr.has_conflict for cr in claim_responses),
    )

    kb_count_result = await db.execute(select(func.count()).select_from(SourceChunk))
    kb_record_count = kb_count_result.scalar() or 0

    return APIResponse(
        success=True,
        data=AnalysisResponse(
            analysis_id=analysis.id,
            processing_status=analysis.processing_status.value if hasattr(analysis.processing_status, "value") else str(analysis.processing_status),
            total_claims=len(claim_responses),
            claims=claim_responses,
            summary=summary,
            language_detected=analysis.language,
            kb_version=analysis.kb_version,
            model=analysis.model,
            kb_record_count=kb_record_count,
        )
    )


def _status_label(status: str) -> str:
    labels = {
        "supported": "مدعوم",
        "partially_supported": "مدعوم جزئياً",
        "needs_review": "يحتاج إلى مراجعة",
        "insufficient_evidence": "دليل غير كافٍ",
        "source_conflict": "تعارض في المصادر",
        "specialist_referral": "يحتاج إلى مختص",
        "pending": "قيد المعالجة",
    }
    return labels.get(status, status)


def _status_color(status: str) -> str:
    colors = {
        "supported": "green",
        "partially_supported": "blue",
        "needs_review": "yellow",
        "insufficient_evidence": "gray",
        "source_conflict": "orange",
        "specialist_referral": "red",
        "pending": "gray",
    }
    return colors.get(status, "gray")
