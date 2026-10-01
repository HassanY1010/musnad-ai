"""
MUSNAD AI - Claim Extractor Service
Extracts atomic, verifiable claims from user input text.
"""
import uuid
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from app.services.llm_provider import llm_provider, LLMCallError, LLMValidationError
from app.services.text_utils import detect_language, normalize_arabic
from app.prompts.claim_extraction_v1 import (
    CLAIM_EXTRACTION_SYSTEM,
    CLAIM_EXTRACTION_USER,
    CLAIM_EXTRACTION_SCHEMA,
)
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ExtractedClaim:
    claim_index: int
    original_text: str
    normalized_text: str
    claim_type: str
    entities: List[str] = field(default_factory=list)
    attributions: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    language: str = "ar"
    needs_specialist: bool = False
    specialist_reason: Optional[str] = None
    extraction_confidence: float = 0.5


@dataclass
class ExtractionResult:
    claims: List[ExtractedClaim] = field(default_factory=list)
    total_claims: int = 0
    language_detected: str = "ar"
    processing_notes: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class ClaimExtractor:
    def __init__(self):
        self.max_claims = settings.MAX_CLAIMS_PER_ANALYSIS

    async def extract(
        self,
        text: str,
        request_id: Optional[str] = None,
    ) -> ExtractionResult:
        if not request_id:
            request_id = str(uuid.uuid4())

        language = detect_language(text)
        max_input = 10000

        if len(text) > max_input:
            logger.warning("text_truncated_for_extraction", length=len(text))
            text = text[:max_input]

        user_prompt = CLAIM_EXTRACTION_USER.format(text=text)

        try:
            raw_result = await llm_provider.generate_structured(
                CLAIM_EXTRACTION_SYSTEM,
                user_prompt,
                request_id,
            )

            claims = self._parse_claims(raw_result, language)

            if len(claims) > self.max_claims:
                logger.warning("claims_truncated", total=len(claims), max=self.max_claims)
                claims = claims[:self.max_claims]

            language_detected = raw_result.get("language_detected", language) if isinstance(raw_result, dict) else language
            processing_notes = raw_result.get("processing_notes") if isinstance(raw_result, dict) else None
            return ExtractionResult(
                claims=claims,
                total_claims=len(claims),
                language_detected=language_detected,
                processing_notes=processing_notes,
                success=True,
            )

        except (LLMCallError, LLMValidationError) as e:
            logger.error("claim_extraction_failed", error=str(e), request_id=request_id)
            return ExtractionResult(
                claims=[],
                total_claims=0,
                language_detected=language,
                processing_notes=None,
                success=False,
                error_message=str(e),
            )

    def _parse_claims(self, raw_result: Any, default_language: str) -> List[ExtractedClaim]:
        if isinstance(raw_result, list):
            raw_claims = raw_result
        elif isinstance(raw_result, dict):
            raw_claims = raw_result.get("claims", [])
        else:
            raw_claims = []
        parsed: List[ExtractedClaim] = []

        valid_types = {
            "quran_verse",
            "hadith",
            "scholarly_quote",
            "fiqh_claim",
            "historical_claim",
            "theological_claim",
            "attribution",
            "general_islamic_claim",
            "source_claim",
            "unknown",
        }

        for i, raw_claim in enumerate(raw_claims, start=1):
            original_text = str(raw_claim.get("original_text", "")).strip()
            if not original_text:
                continue

            claim_type = raw_claim.get("claim_type", "unknown")
            if claim_type not in valid_types:
                claim_type = "unknown"

            normalized = normalize_arabic(original_text)

            parsed.append(
                ExtractedClaim(
                    claim_index=raw_claim.get("claim_index", i),
                    original_text=original_text,
                    normalized_text=normalized,
                    claim_type=claim_type,
                    entities=self._safe_list(raw_claim.get("entities")),
                    attributions=self._safe_list(raw_claim.get("attributions")),
                    references=self._safe_list(raw_claim.get("references")),
                    language=raw_claim.get("language", default_language),
                    needs_specialist=bool(raw_claim.get("needs_specialist", False)),
                    specialist_reason=raw_claim.get("specialist_reason"),
                    extraction_confidence=min(1.0, max(0.0, float(raw_claim.get("extraction_confidence", 0.5)))),
                )
            )

        return parsed

    def _safe_list(self, value: Any) -> List[str]:
        if not value:
            return []
        if isinstance(value, list):
            return [str(v) for v in value if v]
        return [str(value)]


claim_extractor = ClaimExtractor()
