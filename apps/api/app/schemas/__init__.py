"""
MUSNAD AI - Pydantic Schemas & DTOs
Request and response models for all API endpoints.
"""
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class EvidenceItem(BaseModel):
    chunk_id: str
    source_code: str
    source_title: str
    source_title_ar: Optional[str] = None
    source_type: str
    author: Optional[str] = None
    author_ar: Optional[str] = None
    edition: Optional[str] = None
    text: str
    page: Optional[str] = None
    chapter: Optional[str] = None
    hadith_number: Optional[str] = None
    surah_number: Optional[int] = None
    verse_number: Optional[int] = None
    reference: Optional[str] = None
    grading: Optional[str] = None
    grading_authority: Optional[str] = None
    exact_match: bool = False
    retrieval_method: str = "semantic"
    relevance_score: float = 0.0


class ClaimResponse(BaseModel):
    claim_id: str
    claim_index: int
    original_text: str
    normalized_text: Optional[str] = None
    claim_type: str
    status: str
    status_label_ar: str
    status_color: str
    evidence_strength: str = "none"
    source_traceability: str = "none"
    interpretation_certainty: str = "none"
    explanation_ar: str = ""
    abstention_reason: Optional[str] = None
    has_exact_match: bool = False
    has_conflict: bool = False
    rules_triggered: List[str] = Field(default_factory=list)
    supporting_evidence: List[EvidenceItem] = Field(default_factory=list)
    conflicting_evidence: List[EvidenceItem] = Field(default_factory=list)
    needs_specialist: bool = False


class AnalysisSummary(BaseModel):
    total: int = 0
    supported: int = 0
    partially_supported: int = 0
    needs_review: int = 0
    insufficient_evidence: int = 0
    source_conflict: int = 0
    specialist_referral: int = 0
    has_exact_matches: bool = False
    has_conflicts: bool = False


class AnalysisCreateRequest(BaseModel):
    content: str = Field(..., min_length=3, max_length=50000)
    input_type: Optional[str] = "text"


class AnalysisResponse(BaseModel):
    analysis_id: str
    processing_status: str
    total_claims: int
    claims: List[ClaimResponse]
    summary: AnalysisSummary
    language_detected: str = "ar"
    kb_version: str = "KB-002"
    model: str = "gemini-3.6-flash"
    kb_record_count: int = 0  # Runtime count from DB — never hardcoded


class SourceResponse(BaseModel):
    id: str
    source_code: str
    title: str
    title_ar: Optional[str] = None
    author: Optional[str] = None
    author_ar: Optional[str] = None
    source_type: str
    edition: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    language: str = "ar"
    license: Optional[str] = None
    provenance: Optional[str] = None
    status: str = "active"
    kb_version: str = "KB-002"
    chunk_count: int = 0


class SourceListResponse(BaseModel):
    total: int
    sources: List[SourceResponse]


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "user"
    user_id: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime
