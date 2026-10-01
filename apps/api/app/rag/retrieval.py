"""
MUSNAD AI - Hybrid RAG Retrieval Engine
Implements 5-layer retrieval:
  Layer 1: Exact matching
  Layer 2: BM25 lexical search
  Layer 3: Semantic vector search
  Layer 4: Metadata filtering
  Layer 5: Score fusion + reranking

Every retrieved result includes source provenance.
"""
import math
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, and_, or_
from rank_bm25 import BM25Okapi
import numpy as np

from app.models import SourceChunk, Source, SourceDocument, SourceType, SourceStatus
from app.services.llm_provider import llm_provider
from app.services.text_utils import (
    normalize_arabic, strip_attribution, clean_text_for_matching,
    tokenize_arabic, extract_surah_name, strip_basmalah
)
from app.rag.in_memory_retriever import in_memory_retriever
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    """A retrieved source chunk with full provenance."""
    chunk_id: str
    source_id: str
    source_code: str
    source_title: str
    source_title_ar: Optional[str]
    source_type: str
    author: Optional[str]
    author_ar: Optional[str]
    edition: Optional[str]
    text: str
    text_normalized: Optional[str]
    page: Optional[str]
    chapter: Optional[str]
    section: Optional[str]
    hadith_number: Optional[str]
    surah_number: Optional[int]
    verse_number: Optional[int]
    reference: Optional[str]
    grading: Optional[str]
    grading_authority: Optional[str]
    # Retrieval scores
    exact_match: bool = False
    bm25_score: float = 0.0
    semantic_score: float = 0.0
    final_score: float = 0.0
    retrieval_method: str = "semantic"


@dataclass
class RetrievalResult:
    """Result of hybrid retrieval for a claim."""
    claim_text: str
    claim_type: str
    chunks: List[RetrievedChunk] = field(default_factory=list)
    exact_matches_found: int = 0
    total_retrieved: int = 0
    retrieval_error: Optional[str] = None


class HybridRetriever:
    """
    Hybrid retrieval engine implementing multiple retrieval layers.
    Returns provenance-rich results for evidence evaluation.
    """

    def __init__(self):
        self.top_k = settings.RETRIEVAL_TOP_K
        self.reranker_top_k = settings.RERANKER_TOP_K
        self.semantic_threshold = settings.SEMANTIC_THRESHOLD
        self.bm25_weight = settings.BM25_WEIGHT
        self.semantic_weight = settings.SEMANTIC_WEIGHT

    async def retrieve(
        self,
        db: AsyncSession,
        claim_text: str,
        claim_type: str,
        normalized_claim: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> RetrievalResult:
        """
        Run the complete hybrid retrieval pipeline.
        Returns ranked chunks with full source provenance.
        """
        effective_top_k = top_k or self.reranker_top_k
        if normalized_claim is None:
            normalized_claim = normalize_arabic(claim_text)

        result = RetrievalResult(claim_text=claim_text, claim_type=claim_type)

        # --- Layer 1: Exact Matching ---
        exact_chunks = await self._exact_search(db, normalized_claim, claim_type)
        result.exact_matches_found = len(exact_chunks)

        # --- Layer 2+3: Lexical + Semantic ---
        try:
            query_embedding = await llm_provider.embed_query(claim_text)
        except Exception as e:
            logger.error("embedding_failed", error=str(e))
            query_embedding = None

        semantic_chunks = await self._semantic_search(db, query_embedding, claim_type)
        lexical_chunks = await self._lexical_search(db, normalized_claim, claim_type)

        # --- Layer 5: Score Fusion (RRF + Weighted) ---
        fused = self._fuse_results(exact_chunks, lexical_chunks, semantic_chunks)

        # Deduplicate by chunk_id, keep best score
        seen = {}
        for chunk in fused:
            if chunk.chunk_id not in seen or chunk.final_score > seen[chunk.chunk_id].final_score:
                seen[chunk.chunk_id] = chunk

        ranked = sorted(seen.values(), key=lambda x: x.final_score, reverse=True)
        top = ranked[: effective_top_k]

        result.chunks = top
        result.total_retrieved = len(top)

        logger.info(
            "retrieval_complete",
            claim_type=claim_type,
            exact_matches=result.exact_matches_found,
            total_retrieved=result.total_retrieved,
        )

        return result

    async def _exact_search(
        self,
        db: AsyncSession,
        normalized_text: str,
        claim_type: str,
    ) -> List[RetrievedChunk]:
        """
        Layer 1: Exact string matching in normalized text.
        Uses in_memory_retriever to completely bypass SQLite ilike encoding issues.
        """
        seen_ids: set = set()
        chunks: list = []

        query_clean = clean_text_for_matching(strip_attribution(normalized_text))
        
        if claim_type == "quran_verse":
            surah_num = extract_surah_name(normalized_text)
            in_mem_chunks = in_memory_retriever.exact_search_quran(query_clean, surah_num)
        else:
            in_mem_chunks = in_memory_retriever.exact_search_general(query_clean, claim_type)

        for rc in in_mem_chunks:
            if rc.chunk_id not in seen_ids:
                seen_ids.add(rc.chunk_id)
                chunks.append(rc)

        return chunks


    async def _semantic_search(
        self,
        db: AsyncSession,
        query_embedding: Optional[list],
        claim_type: str,
    ) -> List[RetrievedChunk]:
        if not query_embedding:
            return []

        # pgvector <=> operator is PostgreSQL-only; return empty on SQLite
        bind = getattr(db, "bind", None) or getattr(getattr(db, "sync_session", None), "bind", None)
        if bind and bind.dialect.name == "sqlite":
            return []

        try:
            embedding_str = f"[{','.join(str(x) for x in query_embedding)}]"
            stmt = text("""
                SELECT sc.id, sc.source_id, sc.text, sc.text_normalized,
                       sc.page, sc.chapter, sc.section, sc.hadith_number,
                       sc.surah_number, sc.verse_number, sc.reference,
                       sc.grading, sc.grading_authority,
                       s.source_code, s.title, s.title_ar, s.source_type,
                       s.author, s.author_ar, s.edition,
                       1 - (sc.embedding <=> :embedding) AS similarity
                FROM source_chunks sc
                JOIN sources s ON sc.source_id = s.id
                WHERE s.status = 'active'
                  AND sc.embedding IS NOT NULL
                  AND 1 - (sc.embedding <=> :embedding) >= :threshold
                ORDER BY sc.embedding <=> :embedding
                LIMIT :top_k
            """)

            rows = (await db.execute(stmt, {
                "embedding": embedding_str,
                "threshold": self.semantic_threshold,
                "top_k": self.top_k,
            })).mappings().all()

            chunks = []
            for row in rows:
                rc = RetrievedChunk(
                    chunk_id=row["id"],
                    source_id=row["source_id"],
                    source_code=row["source_code"],
                    source_title=row["title"],
                    source_title_ar=row.get("title_ar"),
                    source_type=row["source_type"],
                    author=row.get("author"),
                    author_ar=row.get("author_ar"),
                    edition=row.get("edition"),
                    text=row["text"],
                    text_normalized=row.get("text_normalized"),
                    page=row.get("page"),
                    chapter=row.get("chapter"),
                    section=row.get("section"),
                    hadith_number=row.get("hadith_number"),
                    surah_number=row.get("surah_number"),
                    verse_number=row.get("verse_number"),
                    reference=row.get("reference"),
                    grading=row.get("grading"),
                    grading_authority=row.get("grading_authority"),
                    semantic_score=float(row["similarity"]),
                    final_score=float(row["similarity"]) * self.semantic_weight,
                    retrieval_method="semantic",
                )
                chunks.append(rc)

            return chunks

        except Exception as e:
            logger.error("semantic_search_failed", error=str(e))
            return []

    async def _lexical_search(
        self,
        db: AsyncSession,
        normalized_text: str,
        claim_type: str,
    ) -> List[RetrievedChunk]:
        """Layer 2: BM25 lexical search over indexed chunks."""
        try:
            # Use proper Arabic tokenization (strips stop-words, normalizes)
            # Also strip attribution from query before tokenizing
            stripped = clean_text_for_matching(strip_attribution(normalized_text))
            query_text = stripped if stripped and len(stripped) > 5 else normalized_text
            words = tokenize_arabic(query_text)

            if not words:
                return []

            # If claim_type is quran_verse, restrict/prioritize Quran source (SRC-001)
            source_filter = []
            if claim_type == "quran_verse":
                source_filter.append(Source.source_code == "SRC-001")
            elif claim_type == "hadith":
                source_filter.append(Source.source_type.in_(["HADITH", "hadith", "SCHOLARLY", "scholarly"]))

            # Use top meaningful unique tokens as DB filter (OR conditions for recall)
            key_words = sorted(list(set(words)), key=len, reverse=True)[:5]
            conditions = [SourceChunk.text_normalized.ilike(f"%{w}%") for w in key_words]
            stmt = (
                select(SourceChunk, Source)
                .join(Source, SourceChunk.source_id == Source.id)
                .where(
                    and_(
                        Source.status.in_(['ACTIVE', 'active']),
                        *source_filter,
                        or_(*conditions),
                    )
                )
                .limit(100)  # larger pool for BM25 to score over
            )


            rows = (await db.execute(stmt)).all()
            if not rows:
                return []

            # BM25 scoring using Arabic-tokenized corpus
            corpus = [
                tokenize_arabic(row[0].text_normalized or row[0].text)
                for row in rows
            ]
            bm25 = BM25Okapi(corpus)
            query_tokens = tokenize_arabic(query_text)
            scores = bm25.get_scores(query_tokens)

            chunks = []
            for i, (chunk, source) in enumerate(rows):
                bm25_score = float(scores[i])
                if bm25_score > 0:
                    rc = self._to_retrieved_chunk(chunk, source)
                    rc.bm25_score = bm25_score
                    rc.final_score = bm25_score * self.bm25_weight
                    rc.retrieval_method = "lexical"
                    chunks.append(rc)

            # Normalize BM25 scores
            if chunks:
                max_score = max(c.bm25_score for c in chunks)
                if max_score > 0:
                    for c in chunks:
                        c.bm25_score = c.bm25_score / max_score
                        c.final_score = c.bm25_score * self.bm25_weight

            return sorted(chunks, key=lambda x: x.bm25_score, reverse=True)[:self.top_k]

        except Exception as e:
            logger.error("lexical_search_failed", error=str(e))
            return []

    def _fuse_results(
        self,
        exact: List[RetrievedChunk],
        lexical: List[RetrievedChunk],
        semantic: List[RetrievedChunk],
        k: int = 60,
    ) -> List[RetrievedChunk]:
        """
        Reciprocal Rank Fusion (RRF) combining Exact, BM25 Lexical, and Dense Semantic retrieval.
        Formula: RRF_Score(d) = sum_{m in M} (1.0 / (k + rank_m(d))) with tie-handling.
        """
        all_chunks: dict[str, RetrievedChunk] = {}
        rrf_scores: dict[str, float] = {}

        # 1. Exact matches get immediate max priority
        for chunk in exact:
            all_chunks[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] = 1.0

        # 2. Add BM25 Lexical ranks
        for rank, chunk in enumerate(lexical, start=1):
            cid = chunk.chunk_id
            if cid not in all_chunks:
                all_chunks[cid] = chunk
            else:
                all_chunks[cid].bm25_score = chunk.bm25_score
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))

        # 3. Add Semantic Vector ranks
        for rank, chunk in enumerate(semantic, start=1):
            cid = chunk.chunk_id
            if cid not in all_chunks:
                all_chunks[cid] = chunk
            else:
                all_chunks[cid].semantic_score = chunk.semantic_score
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))

        # 4. Final score calibration combining RRF rank and weighted similarity
        for cid, chunk in all_chunks.items():
            if chunk.exact_match:
                chunk.final_score = 1.0
                chunk.retrieval_method = "exact"
            else:
                weighted_score = (
                    chunk.bm25_score * self.bm25_weight
                    + chunk.semantic_score * self.semantic_weight
                )
                # Max RRF for single list is 1/(60+1) ~ 0.01639, two lists ~ 0.0328
                normalized_rrf = min(1.0, rrf_scores.get(cid, 0.0) * 30.0)
                chunk.final_score = max(weighted_score, normalized_rrf * 0.85)
                if chunk.bm25_score > 0 and chunk.semantic_score > 0:
                    chunk.retrieval_method = "hybrid_rrf"
                elif chunk.bm25_score > 0:
                    chunk.retrieval_method = "lexical"
                else:
                    chunk.retrieval_method = "semantic"

        return list(all_chunks.values())

    @staticmethod
    def _to_retrieved_chunk(chunk: SourceChunk, source: Source) -> RetrievedChunk:
        """Convert SQLAlchemy models to RetrievedChunk dataclass."""
        return RetrievedChunk(
            chunk_id=chunk.id,
            source_id=chunk.source_id,
            source_code=source.source_code,
            source_title=source.title,
            source_title_ar=source.title_ar,
            source_type=source.source_type.value,
            author=source.author,
            author_ar=source.author_ar,
            edition=source.edition,
            text=chunk.text,
            text_normalized=chunk.text_normalized,
            page=chunk.page,
            chapter=chunk.chapter,
            section=chunk.section,
            hadith_number=chunk.hadith_number,
            surah_number=chunk.surah_number,
            verse_number=chunk.verse_number,
            reference=chunk.reference,
            grading=chunk.grading,
            grading_authority=chunk.grading_authority,
        )


# Singleton
hybrid_retriever = HybridRetriever()
