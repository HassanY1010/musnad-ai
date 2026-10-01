"""
Seed SQLite database with verified Islamic knowledge base.
Populates sources, source_documents, and source_chunks into musnad_ai.db.
"""
import sys
import os
import json
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "apps" / "api" / "musnad_ai.db"
EXPANDED_DIR = REPO_ROOT / "knowledge_base" / "v0.2_expanded"
MANIFEST_PATH = REPO_ROOT / "knowledge-base" / "sources" / "manifest.json"

def main():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).isoformat()

    # 1. Load Sources from Manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    source_id_map = {} # source_code -> source_id
    doc_id_map = {} # source_code -> doc_id

    for src in manifest.get("sources", []):
        code = src["source_code"]
        # Check if source exists
        cursor.execute("SELECT id FROM sources WHERE source_code = ?", (code,))
        row = cursor.fetchone()
        if row:
            s_id = row[0]
        else:
            s_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO sources (
                    id, source_code, title, title_ar, author, author_ar,
                    source_type, edition, publisher, year, language,
                    license, provenance, status, kb_version, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s_id, code, src.get("title", ""), src.get("title_ar", ""),
                src.get("author"), src.get("author_ar"), src.get("source_type", "hadith"),
                src.get("edition"), src.get("publisher"), src.get("year"),
                src.get("language", "ar"), src.get("license", "Public Domain"),
                src.get("provenance", ""), "active", "KB-002", now, now
            ))
        source_id_map[code] = s_id

        # Create default SourceDocument for this source
        cursor.execute("SELECT id FROM source_documents WHERE source_id = ?", (s_id,))
        doc_row = cursor.fetchone()
        if doc_row:
            d_id = doc_row[0]
        else:
            d_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO source_documents (
                    id, source_id, document_identifier, volume,
                    metadata, content_hash, ingestion_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d_id, s_id, f"DOC-{code}-MAIN", "1", "{}", "verified", "v0.2", now
            ))
        doc_id_map[code] = d_id

    conn.commit()
    print(f"Registered {len(source_id_map)} sources.")

    # 2. Ingest Chunks from v0.2_expanded
    files_to_ingest = [
        ("hadith/nawawi40.json", "SRC-006"),
        ("hadith/bukhari.json", "SRC-002"),
        ("hadith/muslim.json", "SRC-003"),
        ("quran/quran_canonical.json", "SRC-001"),
        ("tafsir/tafsir_muyassar.json", "SRC-007"),
        ("scholarly/scholarly_quotes.json", "SRC-008"),
        ("fiqh/fiqh_references.json", "SRC-009"),
    ]

    total_chunks_inserted = 0

    for rel_file, default_code in files_to_ingest:
        f_path = EXPANDED_DIR / rel_file
        if not f_path.exists():
            print(f"Skipping {rel_file} (not found)")
            continue

        print(f"Ingesting {rel_file}...")
        with open(f_path, "r", encoding="utf-8") as fh:
            records = json.load(fh)

        # Batch insert chunks
        chunk_rows = []
        for r in records:
            s_code = r.get("source_code", default_code)
            s_id = source_id_map.get(s_code)
            if not s_id:
                # If source wasn't in manifest, create it
                s_id = str(uuid.uuid4())
                source_id_map[s_code] = s_id
                cursor.execute("""
                    INSERT INTO sources (id, source_code, title, title_ar, source_type, language, status, kb_version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 'ar', 'active', 'KB-002', ?, ?)
                """, (s_id, s_code, r.get("source_title", s_code), r.get("source_title", s_code), r.get("source_type", "hadith"), now, now))
                d_id = str(uuid.uuid4())
                doc_id_map[s_code] = d_id
                cursor.execute("""
                    INSERT INTO source_documents (id, source_id, document_identifier, created_at, ingestion_version)
                    VALUES (?, ?, ?, ?, 'v0.2')
                """, (d_id, s_id, f"DOC-{s_code}", now))

            d_id = doc_id_map[s_code]
            chunk_id = r.get("id") or str(uuid.uuid4())

            text = r.get("text", "")
            text_norm = r.get("text_normalized", "")
            page = str(r.get("page", "")) if r.get("page") is not None else None
            chapter = r.get("chapter") or r.get("surah_name_ar")
            section = r.get("section")
            hadith_num = str(r.get("hadith_number", "")) if r.get("hadith_number") else None
            surah_num = r.get("surah_number")
            verse_num = r.get("verse_number")
            reference = r.get("reference")
            grading = r.get("grading")
            grading_auth = r.get("grading_authority")
            chunk_type = r.get("source_type") or r.get("chunk_type")

            chunk_rows.append((
                chunk_id, d_id, s_id, text, text_norm, page, chapter, section,
                hadith_num, surah_num, verse_num, reference, grading, grading_auth,
                chunk_type, "{}", None, None, now
            ))

        cursor.executemany("""
            INSERT OR REPLACE INTO source_chunks (
                id, document_id, source_id, text, text_normalized, page, chapter, section,
                hadith_number, surah_number, verse_number, reference, grading, grading_authority,
                chunk_type, metadata, embedding, embedding_model, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, chunk_rows)

        conn.commit()
        total_chunks_inserted += len(chunk_rows)
        print(f" -> Inserted {len(chunk_rows)} chunks for {rel_file}.")

    # Copy to root musnad_ai.db as well if it exists
    root_db = REPO_ROOT / "musnad_ai.db"
    import shutil
    shutil.copy2(DB_PATH, root_db)
    print(f"Copied synced database to root {root_db}")

    print(f"\nSeeding complete! Total chunks inserted: {total_chunks_inserted}")
    conn.close()

if __name__ == "__main__":
    main()
