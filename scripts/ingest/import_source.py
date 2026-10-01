"""
MUSNAD AI - Master Source Ingestion CLI
Executes modular ingestion across verified Islamic corpora.
Usage:
  python scripts/ingest/import_source.py --source quran
  python scripts/ingest/import_source.py --source bukhari
  python scripts/ingest/import_source.py --source muslim
  python scripts/ingest/import_source.py --source nawawi
  python scripts/ingest/import_source.py --source tafsir
  python scripts/ingest/import_source.py --source scholarly
  python scripts/ingest/import_source.py --source fiqh
  python scripts/ingest/import_source.py --source all
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.ingest.ingest_quran import QuranIngester
from scripts.ingest.ingest_hadith import HadithIngester
from scripts.ingest.ingest_tafsir import TafsirIngester
from scripts.ingest.ingest_scholarly import ScholarlyIngester
from scripts.ingest.ingest_fiqh import FiqhIngester
from scripts.ingest.base_ingester import compute_sha256


def build_manifest(kb_dir: Path, sources_meta: list) -> dict:
    manifest = {
        "dataset_version": "KB-002",
        "kb_label": "MUSNAD Scaled Verified Knowledge Base",
        "kb_label_ar": "قاعدة بيانات مسند الموسعة للمصادر الإسلامية الموثقة",
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_corpora_count": len(sources_meta),
        "total_records": sum(s["record_count"] for s in sources_meta),
        "sources": sources_meta,
    }
    return manifest


def main():
    parser = argparse.ArgumentParser(description="MUSNAD AI Knowledge Ingestion Pipeline")
    parser.add_argument(
        "--source",
        choices=["quran", "hadith", "bukhari", "muslim", "nawawi", "tafsir", "scholarly", "fiqh", "all"],
        default="all",
        help="Source to ingest",
    )
    parser.add_argument(
        "--bukhari-limit",
        type=int,
        default=2500,
        help="Optional maximum number of Bukhari hadiths to ingest in this build",
    )
    parser.add_argument(
        "--muslim-limit",
        type=int,
        default=2000,
        help="Optional maximum number of Muslim hadiths to ingest in this build",
    )
    parser.add_argument(
        "--tafsir-surahs",
        type=int,
        default=114,
        help="Number of surahs to ingest tafsir for (default: 114)",
    )
    args = parser.parse_args()

    out_base = REPO_ROOT / "knowledge_base" / "v0.2_expanded"
    out_base.mkdir(parents=True, exist_ok=True)

    sources_metadata = []
    t_start = time.time()

    # 1. Quran
    if args.source in ["quran", "all"]:
        q_path = out_base / "quran" / "quran_canonical.json"
        q_records = QuranIngester().ingest(q_path)
        sources_metadata.append({
            "source_code": "SRC-001",
            "type": "quran",
            "title": "القرآن الكريم",
            "title_en": "The Holy Quran",
            "record_count": len(q_records),
            "file": str(q_path.relative_to(REPO_ROOT)),
            "file_sha256": hashlib.sha256(open(q_path, "rb").read()).hexdigest(),
            "license": "Public Domain",
            "verification_status": "verified",
        })

    # 2. Nawawi
    if args.source in ["nawawi", "hadith", "all"]:
        n_path = out_base / "hadith" / "nawawi40.json"
        n_records = HadithIngester("nawawi").ingest(n_path)
        sources_metadata.append({
            "source_code": "SRC-006",
            "type": "hadith",
            "title": "الأربعون النووية",
            "title_en": "Al-Arba'in al-Nawawiyya",
            "record_count": len(n_records),
            "file": str(n_path.relative_to(REPO_ROOT)),
            "file_sha256": hashlib.sha256(open(n_path, "rb").read()).hexdigest(),
            "license": "Public Domain",
            "verification_status": "verified",
        })

    # 3. Bukhari
    if args.source in ["bukhari", "hadith", "all"]:
        b_path = out_base / "hadith" / "bukhari.json"
        b_records = HadithIngester("bukhari").ingest(b_path, max_records=args.bukhari_limit)
        sources_metadata.append({
            "source_code": "SRC-002",
            "type": "hadith",
            "title": "صحيح البخاري (الجامع المسند الصحيح)",
            "title_en": "Sahih al-Bukhari",
            "record_count": len(b_records),
            "file": str(b_path.relative_to(REPO_ROOT)),
            "file_sha256": hashlib.sha256(open(b_path, "rb").read()).hexdigest(),
            "license": "Public Domain",
            "verification_status": "verified",
        })

    # 4. Muslim
    if args.source in ["muslim", "hadith", "all"]:
        m_path = out_base / "hadith" / "muslim.json"
        m_records = HadithIngester("muslim").ingest(m_path, max_records=args.muslim_limit)
        sources_metadata.append({
            "source_code": "SRC-003",
            "type": "hadith",
            "title": "صحيح مسلم (المسند الصحيح)",
            "title_en": "Sahih Muslim",
            "record_count": len(m_records),
            "file": str(m_path.relative_to(REPO_ROOT)),
            "file_sha256": hashlib.sha256(open(m_path, "rb").read()).hexdigest(),
            "license": "Public Domain",
            "verification_status": "verified",
        })

    # 5. Tafsir
    if args.source in ["tafsir", "all"]:
        t_path = out_base / "tafsir" / "tafsir_muyassar.json"
        t_records = TafsirIngester().ingest(t_path, max_surahs=args.tafsir_surahs)
        sources_metadata.append({
            "source_code": "SRC-007",
            "type": "tafsir",
            "title": "التفسير الميسر",
            "title_en": "Tafsir al-Muyassar",
            "record_count": len(t_records),
            "file": str(t_path.relative_to(REPO_ROOT)),
            "file_sha256": hashlib.sha256(open(t_path, "rb").read()).hexdigest(),
            "license": "Public Domain",
            "verification_status": "verified",
        })

    # 6. Scholarly Quotes
    if args.source in ["scholarly", "all"]:
        s_path = out_base / "scholarly" / "scholarly_quotes.json"
        s_records = ScholarlyIngester().ingest(s_path)
        sources_metadata.append({
            "source_code": "SRC-008",
            "type": "scholarly",
            "title": "موسوعة الآثار وأقوال أئمة الإسلام المعتمدة",
            "title_en": "Classical Scholarly Quotations & Athar",
            "record_count": len(s_records),
            "file": str(s_path.relative_to(REPO_ROOT)),
            "file_sha256": hashlib.sha256(open(s_path, "rb").read()).hexdigest(),
            "license": "Public Domain",
            "verification_status": "verified",
        })

    # 7. Fiqh References
    if args.source in ["fiqh", "all"]:
        f_path = out_base / "fiqh" / "fiqh_references.json"
        f_records = FiqhIngester().ingest(f_path)
        sources_metadata.append({
            "source_code": "SRC-009",
            "type": "fiqh",
            "title": "سجل المراجع والقرارات الفقهية والمجمعية المعتمدة",
            "title_en": "Source-Backed Fiqh References & Academy Resolutions",
            "record_count": len(f_records),
            "file": str(f_path.relative_to(REPO_ROOT)),
            "file_sha256": hashlib.sha256(open(f_path, "rb").read()).hexdigest(),
            "license": "Public Domain / Institutional Decisions",
            "verification_status": "verified",
        })

    manifest = build_manifest(REPO_ROOT / "knowledge_base", sources_metadata)
    
    # Save manifest in both knowledge_base and knowledge-base for compatibility
    for m_path in [
        REPO_ROOT / "knowledge_base" / "manifest.json",
        REPO_ROOT / "knowledge-base" / "manifest.json",
    ]:
        m_path.parent.mkdir(parents=True, exist_ok=True)
        with open(m_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print("MUSNAD AI — KNOWLEDGE BASE INGESTION COMPLETE")
    print(f"Dataset Version: {manifest['dataset_version']}")
    print(f"Total Sources Ingested: {len(sources_metadata)}")
    print(f"Total Verified Records: {manifest['total_records']}")
    print(f"Time Taken: {total_time:.2f}s")
    print(f"Manifest: knowledge_base/manifest.json")
    print("=" * 80)


if __name__ == "__main__":
    main()
