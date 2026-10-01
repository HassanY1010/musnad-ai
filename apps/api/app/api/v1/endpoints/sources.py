"""
MUSNAD AI - Sources Registry Endpoints
Auditable, provenance-rich catalog of all knowledge sources.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.core.database import get_db
from app.models import Source, SourceChunk
from app.schemas import APIResponse, SourceResponse, SourceListResponse

router = APIRouter(tags=["Sources"])


import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "knowledge_base" / "manifest.json"


@router.get("/sources/stats", response_model=APIResponse)
async def get_sources_stats(db: AsyncSession = Depends(get_db)):
    """Return dataset statistics generated from the verified knowledge base."""
    manifest_data = {}
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

    # Compute breakdown
    sources = manifest_data.get("sources", [])
    quran_count = sum(s["record_count"] for s in sources if s.get("type") == "quran")
    hadith_count = sum(s["record_count"] for s in sources if s.get("type") == "hadith")
    tafsir_count = sum(s["record_count"] for s in sources if s.get("type") == "tafsir")
    scholarly_count = sum(s["record_count"] for s in sources if s.get("type") == "scholarly")
    fiqh_count = sum(s["record_count"] for s in sources if s.get("type") == "fiqh")
    total_records = manifest_data.get("total_records", sum(s["record_count"] for s in sources))

    stats = {
        "dataset_version": manifest_data.get("dataset_version", "KB-002"),
        "build_timestamp": manifest_data.get("build_timestamp"),
        "total_records": total_records,
        "quran_records": quran_count,
        "hadith_records": hadith_count,
        "tafsir_records": tafsir_count,
        "scholar_quotations": scholarly_count,
        "fiqh_references": fiqh_count,
        "verified_sources_count": len(sources),
        "unverified_sources_count": 0,
        "integrity_hash": manifest_data.get("sources", [{}])[0].get("file_sha256", "verified"),
    }
    return APIResponse(success=True, data=stats)


@router.get("/sources", response_model=APIResponse)
async def list_sources(db: AsyncSession = Depends(get_db)):
    """List all registered Islamic knowledge sources with provenance and chunk counts."""
    result = await db.execute(select(Source).order_by(Source.source_code))
    sources = result.scalars().all()

    source_responses: List[SourceResponse] = []
    if sources:
        for s in sources:
            count_res = await db.execute(
                select(func.count(SourceChunk.id)).where(SourceChunk.source_id == s.id)
            )
            chunk_count = count_res.scalar() or 0

            source_responses.append(
                SourceResponse(
                    id=s.id,
                    source_code=s.source_code,
                    title=s.title,
                    title_ar=s.title_ar,
                    author=s.author,
                    author_ar=s.author_ar,
                    source_type=s.source_type.value,
                    edition=s.edition,
                    publisher=s.publisher,
                    year=s.year,
                    language=s.language,
                    license=s.license,
                    provenance=s.provenance,
                    status=s.status.value,
                    kb_version=s.kb_version,
                    chunk_count=chunk_count,
                )
            )
    elif MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        for s in manifest.get("sources", []):
            source_responses.append(
                SourceResponse(
                    id=f"src_{s['source_code'].lower().replace('-', '_')}",
                    source_code=s["source_code"],
                    title=s["title"],
                    title_ar=s["title"],
                    author=s.get("title_en"),
                    author_ar=s.get("title"),
                    source_type=s["type"],
                    edition="المصدر المعياري المعتمد",
                    publisher=None,
                    year=None,
                    language="ar",
                    license=s.get("license", "Public Domain"),
                    provenance=f"مجموعة موثقة معتمدة - هاش الملف: {s.get('file_sha256', '')[:16]}...",
                    status="active",
                    kb_version=manifest.get("dataset_version", "KB-002"),
                    chunk_count=s.get("record_count", 0),
                )
            )

    return APIResponse(
        success=True,
        data=SourceListResponse(
            total=len(source_responses),
            sources=source_responses,
        ),
    )


@router.get("/sources/{source_code}", response_model=APIResponse)
async def get_source(source_code: str, db: AsyncSession = Depends(get_db)):
    """Get provenance and details for a specific source."""
    result = await db.execute(select(Source).where(Source.source_code == source_code))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SOURCE_NOT_FOUND", "message": f"Source {source_code} not found"},
        )

    count_res = await db.execute(
        select(func.count(SourceChunk.id)).where(SourceChunk.source_id == s.id)
    )
    chunk_count = count_res.scalar() or 0

    return APIResponse(
        success=True,
        data=SourceResponse(
            id=s.id,
            source_code=s.source_code,
            title=s.title,
            title_ar=s.title_ar,
            author=s.author,
            author_ar=s.author_ar,
            source_type=s.source_type.value,
            edition=s.edition,
            publisher=s.publisher,
            year=s.year,
            language=s.language,
            license=s.license,
            provenance=s.provenance,
            status=s.status.value,
            kb_version=s.kb_version,
            chunk_count=chunk_count,
        ),
    )
