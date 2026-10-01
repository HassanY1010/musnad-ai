"""
MUSNAD AI - Knowledge Base Ingestion Script
Ingests registered sources, documents, and chunks with full provenance and embeddings.
"""
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

# Add app to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models import Source, SourceDocument, SourceChunk, SourceType, SourceStatus
from app.services.llm_provider import llm_provider
from app.services.text_utils import normalize_arabic
from app.core.logging import get_logger

logger = get_logger(__name__)

REPO_ROOT = BASE_DIR.parent.parent


async def ingest():
    print("Initializing database...")
    try:
        await init_db()
    except Exception as e:
        print(f"init_db note: {e}")

    manifest_path = REPO_ROOT / "knowledge-base" / "sources" / "manifest.json"
    if not manifest_path.exists():
        print(f"Manifest not found at {manifest_path}")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    async with AsyncSessionLocal() as db:
        print(f"Registering {len(manifest.get('sources', []))} sources...")
        sources_map = {}

        for src_data in manifest.get("sources", []):
            code = src_data["source_code"]
            res = await db.execute(select(Source).where(Source.source_code == code))
            existing = res.scalar_one_or_none()

            if not existing:
                source = Source(
                    id=str(uuid.uuid4()),
                    source_code=code,
                    title=src_data["title"],
                    title_ar=src_data.get("title_ar"),
                    author=src_data.get("author"),
                    author_ar=src_data.get("author_ar"),
                    source_type=SourceType(src_data["source_type"]),
                    edition=src_data.get("edition"),
                    publisher=src_data.get("publisher"),
                    license=src_data.get("license"),
                    provenance=src_data.get("provenance"),
                    status=SourceStatus(src_data.get("status", "active")),
                    kb_version=manifest.get("kb_version", "KB-001"),
                )
                db.add(source)
                await db.commit()
                await db.refresh(source)
                sources_map[code] = source
                print(f"  + Added source: {code} - {source.title_ar}")
            else:
                sources_map[code] = existing
                print(f"  = Found source: {code} - {existing.title_ar}")

        # Ingest Quran Verses
        quran_source = sources_map.get("SRC-001")
        if quran_source:
            quran_data_path = REPO_ROOT / "knowledge-base" / "data" / "quran" / "seed_verses.json"
            if quran_data_path.exists():
                with open(quran_data_path, "r", encoding="utf-8") as f:
                    verses = json.load(f)

                # Create document
                doc_res = await db.execute(
                    select(SourceDocument).where(
                        SourceDocument.source_id == quran_source.id,
                        SourceDocument.document_identifier == "mushaf_madinah",
                    )
                )
                doc = doc_res.scalar_one_or_none()
                if not doc:
                    doc = SourceDocument(
                        id=str(uuid.uuid4()),
                        source_id=quran_source.id,
                        document_identifier="mushaf_madinah",
                        volume="1",
                        ingestion_version="v1",
                    )
                    db.add(doc)
                    await db.commit()
                    await db.refresh(doc)

                print(f"Ingesting {len(verses)} Quran verses...")
                for v in verses:
                    chunk_text = v["text"]
                    norm_text = v.get("text_normalized") or normalize_arabic(chunk_text)
                    emb = await llm_provider.embed_text(chunk_text)

                    chunk = SourceChunk(
                        id=str(uuid.uuid4()),
                        document_id=doc.id,
                        source_id=quran_source.id,
                        text=chunk_text,
                        text_normalized=norm_text,
                        surah_number=v["surah_number"],
                        verse_number=v["verse_number"],
                        chapter=v["surah_name_ar"],
                        reference=v["reference"],
                        chunk_type="quran_verse",
                        embedding=emb,
                        embedding_model="models/text-embedding-004",
                    )
                    db.add(chunk)
                await db.commit()
                print("  Quran ingestion complete.")

        # Ingest Hadith
        hadith_data_path = REPO_ROOT / "knowledge-base" / "data" / "hadith" / "seed_hadiths.json"
        if hadith_data_path.exists():
            with open(hadith_data_path, "r", encoding="utf-8") as f:
                hadiths = json.load(f)

            print(f"Ingesting {len(hadiths)} authentic Hadiths...")
            for h in hadiths:
                src_code = h.get("source_code", "SRC-002")
                src = sources_map.get(src_code) or sources_map.get("SRC-002")
                if not src:
                    continue

                # Document
                doc_ident = f"{src_code}_vol1"
                doc_res = await db.execute(
                    select(SourceDocument).where(
                        SourceDocument.source_id == src.id,
                        SourceDocument.document_identifier == doc_ident,
                    )
                )
                doc = doc_res.scalar_one_or_none()
                if not doc:
                    doc = SourceDocument(
                        id=str(uuid.uuid4()),
                        source_id=src.id,
                        document_identifier=doc_ident,
                        volume="1",
                        ingestion_version="v1",
                    )
                    db.add(doc)
                    await db.commit()
                    await db.refresh(doc)

                chunk_text = h["text"]
                norm_text = h.get("text_normalized") or normalize_arabic(chunk_text)
                emb = await llm_provider.embed_text(chunk_text)

                chunk = SourceChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc.id,
                    source_id=src.id,
                    text=chunk_text,
                    text_normalized=norm_text,
                    hadith_number=h.get("hadith_number"),
                    chapter=h.get("chapter"),
                    grading=h.get("grading"),
                    grading_authority=h.get("grading_authority"),
                    reference=h.get("reference"),
                    chunk_type="hadith",
                    embedding=emb,
                    embedding_model="models/text-embedding-004",
                )
                db.add(chunk)

            await db.commit()
            print("  Hadith ingestion complete.")

    print("\nIngestion finished successfully.")


if __name__ == "__main__":
    asyncio.run(ingest())
