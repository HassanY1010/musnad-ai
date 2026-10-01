"""
MUSNAD AI - Data Models
SQLAlchemy ORM models with PostgreSQL and pgvector support.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List
import enum
from sqlalchemy import (
    String, Text, Float, Boolean, Integer, DateTime,
    ForeignKey, Enum as SAEnum, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def gen_uuid() -> str:
    return str(uuid.uuid4())


# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    admin = "admin"
    REVIEWER = "reviewer"
    reviewer = "reviewer"
    USER = "user"
    user = "user"
    ANONYMOUS = "anonymous"
    anonymous = "anonymous"


class SourceType(str, enum.Enum):
    QURAN = "quran"
    quran = "quran"
    HADITH = "hadith"
    hadith = "hadith"
    SCHOLARLY = "scholarly"
    scholarly = "scholarly"
    FIQH = "fiqh"
    fiqh = "fiqh"
    TAFSIR = "tafsir"
    tafsir = "tafsir"
    OTHER = "other"
    other = "other"


class SourceStatus(str, enum.Enum):
    ACTIVE = "active"
    active = "active"
    INACTIVE = "inactive"
    inactive = "inactive"
    PENDING_REVIEW = "pending_review"
    pending_review = "pending_review"
    INGESTION_FAILED = "ingestion_failed"
    ingestion_failed = "ingestion_failed"


class ClaimType(str, enum.Enum):
    QURAN_VERSE = "quran_verse"
    quran_verse = "quran_verse"
    HADITH = "hadith"
    hadith = "hadith"
    SCHOLARLY_QUOTE = "scholarly_quote"
    scholarly_quote = "scholarly_quote"
    FIQH_CLAIM = "fiqh_claim"
    fiqh_claim = "fiqh_claim"
    HISTORICAL_CLAIM = "historical_claim"
    historical_claim = "historical_claim"
    THEOLOGICAL_CLAIM = "theological_claim"
    theological_claim = "theological_claim"
    ATTRIBUTION = "attribution"
    attribution = "attribution"
    GENERAL_ISLAMIC_CLAIM = "general_islamic_claim"
    general_islamic_claim = "general_islamic_claim"
    SOURCE_CLAIM = "source_claim"
    source_claim = "source_claim"
    UNKNOWN = "unknown"
    unknown = "unknown"


class VerificationStatus(str, enum.Enum):
    SUPPORTED = "supported"
    supported = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    partially_supported = "partially_supported"
    NEEDS_REVIEW = "needs_review"
    needs_review = "needs_review"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    insufficient_evidence = "insufficient_evidence"
    SOURCE_CONFLICT = "source_conflict"
    source_conflict = "source_conflict"
    SPECIALIST_REFERRAL = "specialist_referral"
    specialist_referral = "specialist_referral"
    PENDING = "pending"
    pending = "pending"
    ERROR = "error"
    error = "error"


class MatchType(str, enum.Enum):
    EXACT = "exact"
    exact = "exact"
    LEXICAL = "lexical"
    lexical = "lexical"
    SEMANTIC = "semantic"
    semantic = "semantic"
    METADATA = "metadata"
    metadata = "metadata"


class SupportType(str, enum.Enum):
    DIRECT = "direct"
    direct = "direct"
    PARTIAL = "partial"
    partial = "partial"
    CONTRADICTORY = "contradictory"
    contradictory = "contradictory"
    TANGENTIAL = "tangential"
    tangential = "tangential"
    INSUFFICIENT = "insufficient"
    insufficient = "insufficient"


class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    queued = "queued"
    PROCESSING = "processing"
    processing = "processing"
    COMPLETED = "completed"
    completed = "completed"
    FAILED = "failed"
    failed = "failed"


class InputType(str, enum.Enum):
    TEXT = "text"
    text = "text"
    PDF = "pdf"
    pdf = "pdf"
    DOCX = "docx"
    docx = "docx"
    URL = "url"
    url = "url"


# Models
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    analyses: Mapped[List["Analysis"]] = relationship("Analysis", back_populates="user")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="actor_user")


class Source(Base):
    """
    A registered, auditable source in the knowledge base.
    Every evidence item must trace back to a Source.
    """
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    source_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ar: Mapped[Optional[str]] = mapped_column(String(255))
    author: Mapped[Optional[str]] = mapped_column(String(255))
    author_ar: Mapped[Optional[str]] = mapped_column(String(255))
    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType), nullable=False)
    edition: Mapped[Optional[str]] = mapped_column(String(255))
    publisher: Mapped[Optional[str]] = mapped_column(String(255))
    year: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[str] = mapped_column(String(16), default="ar")
    license: Mapped[Optional[str]] = mapped_column(String(128))
    provenance: Mapped[Optional[str]] = mapped_column(Text)
    retrieval_url: Mapped[Optional[str]] = mapped_column(String(512))
    retrieval_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[SourceStatus] = mapped_column(SAEnum(SourceStatus), default=SourceStatus.active)
    kb_version: Mapped[str] = mapped_column(String(32), default="KB-001")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    documents: Mapped[List["SourceDocument"]] = relationship("SourceDocument", back_populates="source", cascade="all, delete-orphan")


class SourceDocument(Base):
    """A document/volume within a source."""
    __tablename__ = "source_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    source_id: Mapped[str] = mapped_column(String, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    document_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    volume: Mapped[Optional[str]] = mapped_column(String(64))
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)
    content_hash: Mapped[Optional[str]] = mapped_column(String(128))
    ingestion_version: Mapped[str] = mapped_column(String(32), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    source: Mapped["Source"] = relationship("Source", back_populates="documents")
    chunks: Mapped[List["SourceChunk"]] = relationship("SourceChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("source_id", "document_identifier", name="uq_source_document"),
    )


class SourceChunk(Base):
    """
    An indexed text chunk from a source document.
    This is the atomic unit of evidence retrieval.
    Every claim's evidence must point to a chunk.
    """
    __tablename__ = "source_chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str] = mapped_column(String, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_normalized: Mapped[Optional[str]] = mapped_column(Text)
    page: Mapped[Optional[str]] = mapped_column(String(32))
    chapter: Mapped[Optional[str]] = mapped_column(String(255))
    section: Mapped[Optional[str]] = mapped_column(String(255))
    hadith_number: Mapped[Optional[str]] = mapped_column(String(64))
    surah_number: Mapped[Optional[int]] = mapped_column(Integer)
    verse_number: Mapped[Optional[int]] = mapped_column(Integer)
    reference: Mapped[Optional[str]] = mapped_column(String(255))
    grading: Mapped[Optional[str]] = mapped_column(String(64))
    grading_authority: Mapped[Optional[str]] = mapped_column(String(255))
    chunk_type: Mapped[Optional[str]] = mapped_column(String(64))
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(768))
    embedding_model: Mapped[Optional[str]] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    document: Mapped["SourceDocument"] = relationship("SourceDocument", back_populates="chunks")
    evidence_items: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="chunk")


class Analysis(Base):
    """A verification analysis request."""
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"))
    input_type: Mapped[InputType] = mapped_column(SAEnum(InputType), default=InputType.text)
    original_content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="ar")
    processing_status: Mapped[AnalysisStatus] = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.queued)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    app_version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    prompt_version: Mapped[str] = mapped_column(String(32), default="v1")
    model: Mapped[str] = mapped_column(String(64), default="gemini-1.5-flash")
    kb_version: Mapped[str] = mapped_column(String(32), default="KB-001")
    retrieval_config: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="analyses")
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="analysis", cascade="all, delete-orphan")


class Claim(Base):
    """
    A structured claim extracted from content.
    This is the unit of verification.
    """
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    analysis_id: Mapped[str] = mapped_column(String, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    claim_index: Mapped[int] = mapped_column(Integer, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[Optional[str]] = mapped_column(Text)
    claim_type: Mapped[ClaimType] = mapped_column(SAEnum(ClaimType), default=ClaimType.unknown)
    entities: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    references: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    attributions: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    needs_specialist: Mapped[bool] = mapped_column(Boolean, default=False)
    specialist_reason: Mapped[Optional[str]] = mapped_column(Text)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="claims")
    evidence_items: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan")
    verification_result: Mapped[Optional["VerificationResult"]] = relationship("VerificationResult", back_populates="claim", uselist=False, cascade="all, delete-orphan")


class Evidence(Base):
    """
    A piece of evidence retrieved from the knowledge base.
    Every evidence item must trace to a source chunk.
    """
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    claim_id: Mapped[str] = mapped_column(String, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    chunk_id: Mapped[str] = mapped_column(String, ForeignKey("source_chunks.id", ondelete="CASCADE"), nullable=False)
    match_type: Mapped[MatchType] = mapped_column(SAEnum(MatchType), default=MatchType.semantic)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    support_type: Mapped[SupportType] = mapped_column(SAEnum(SupportType), default=SupportType.partial)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    retrieval_rank: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    claim: Mapped["Claim"] = relationship("Claim", back_populates="evidence_items")
    chunk: Mapped["SourceChunk"] = relationship("SourceChunk", back_populates="evidence_items")


class VerificationResult(Base):
    """
    The final deterministic verification result for a claim.
    The LLM does not set this — the verification engine does.
    """
    __tablename__ = "verification_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    claim_id: Mapped[str] = mapped_column(String, ForeignKey("claims.id", ondelete="CASCADE"), unique=True, nullable=False)
    status: Mapped[VerificationStatus] = mapped_column(SAEnum(VerificationStatus), default=VerificationStatus.pending)
    evidence_strength: Mapped[float] = mapped_column(Float, default=0.0)
    retrieval_relevance: Mapped[float] = mapped_column(Float, default=0.0)
    source_traceability: Mapped[float] = mapped_column(Float, default=0.0)
    interpretation_certainty: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    explanation_ar: Mapped[Optional[str]] = mapped_column(Text)
    rules_triggered: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    abstention_reason: Mapped[Optional[str]] = mapped_column(Text)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"))
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    claim: Mapped["Claim"] = relationship("Claim", back_populates="verification_result")


class TestCase(Base):
    """Evaluation test cases for regression testing."""
    __tablename__ = "test_cases"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[Optional[str]] = mapped_column(String(64))
    expected_status: Mapped[str] = mapped_column(String(64), nullable=False)
    expected_behavior: Mapped[Optional[str]] = mapped_column(Text)
    source_expectations: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    actual_status: Mapped[Optional[str]] = mapped_column(String(64))
    actual_behavior: Mapped[Optional[str]] = mapped_column(Text)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_run_passed: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    """Immutable audit trail for all significant actions."""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    actor_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="SET NULL"))
    actor_type: Mapped[str] = mapped_column(String(32), default="user")
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    previous_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    entry_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    actor_user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
