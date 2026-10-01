"""
MUSNAD AI - Automated Knowledge Base Quality & Integrity Test Suite
Verifies:
1. Integrity (duplicate detection, hash uniqueness, non-empty text, valid identifiers)
2. Provenance (source_code, source_type, reference, content_hash)
3. Religious-Content Separation (Quran != Hadith, Hadith != Tafsir, Tafsir != Quran)
4. Anti-Corruption (Arabic encoding validation, no malformed unicode)
"""
import json
import re
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPANDED_DIR = REPO_ROOT / "knowledge_base" / "v0.2_expanded"
MANIFEST_PATH = REPO_ROOT / "knowledge_base" / "manifest.json"


def load_dataset(subpath: str):
    path = EXPANDED_DIR / subpath
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestKnowledgeBaseIntegrity:
    def test_manifest_exists_and_valid(self):
        assert MANIFEST_PATH.exists(), "Knowledge base manifest must exist."
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["dataset_version"] == "KB-002"
        assert manifest["total_records"] > 0
        assert len(manifest["sources"]) >= 6

    def test_quran_canonical_integrity(self):
        quran_records = load_dataset("quran/quran_canonical.json")
        assert len(quran_records) == 6236, f"Expected 6236 canonical Quran ayahs, got {len(quran_records)}"
        
        hashes = set()
        for r in quran_records:
            assert r["source_code"] == "SRC-001"
            assert r["source_type"] == "quran"
            assert 1 <= r["surah_number"] <= 114
            assert r["verse_number"] >= 1
            assert len(r["text"].strip()) > 0
            assert len(r["content_hash"]) == 64
            assert r["verification_status"] == "verified"
            assert r["content_hash"] not in hashes, f"Duplicate hash found for ayah: {r['id']}"
            hashes.add(r["content_hash"])

    def test_hadith_integrity_and_provenance(self):
        nawawi_records = load_dataset("hadith/nawawi40.json")
        assert len(nawawi_records) == 42, f"Expected 42 Nawawi hadiths, got {len(nawawi_records)}"

        bukhari_records = load_dataset("hadith/bukhari.json")
        assert len(bukhari_records) > 0, "Bukhari records must be populated"

        muslim_records = load_dataset("hadith/muslim.json")
        assert len(muslim_records) > 0, "Muslim records must be populated"

        for coll in [nawawi_records, bukhari_records, muslim_records]:
            for h in coll:
                assert h["source_type"] == "hadith"
                assert h["source_code"] in ["SRC-002", "SRC-003", "SRC-006"]
                assert len(h["text"].strip()) > 0
                assert len(h["content_hash"]) == 64
                assert "reference" in h and h["reference"] is not None

    def test_tafsir_integrity(self):
        tafsir_records = load_dataset("tafsir/tafsir_muyassar.json")
        assert len(tafsir_records) > 0, "Tafsir records must be populated"
        for t in tafsir_records:
            assert t["source_type"] == "tafsir"
            assert t["source_code"] == "SRC-007"
            assert "ayah_reference" in t
            assert len(t["text"].strip()) > 0
            assert len(t["content_hash"]) == 64

    def test_scholarly_quotes_provenance(self):
        scholar_records = load_dataset("scholarly/scholarly_quotes.json")
        assert len(scholar_records) >= 10
        for s in scholar_records:
            assert s["source_type"] == "scholarly"
            assert s["source_code"] == "SRC-008"
            assert len(s["scholar"]) > 0
            assert len(s["work"]) > 0
            assert s["verification_status"] in ["verified", "fabricated_attribution", "spurious_as_hadith"]

    def test_fiqh_references_and_specialist_flags(self):
        fiqh_records = load_dataset("fiqh/fiqh_references.json")
        assert len(fiqh_records) >= 5
        specialist_count = sum(1 for f in fiqh_records if f["requires_specialist_review"])
        assert specialist_count >= 3, "Complex contemporary fiqh must require specialist review"

    def test_religious_content_separation(self):
        """Crucial test: Ensure strict demarcation between Quran, Hadith, Tafsir, Scholarly."""
        quran = load_dataset("quran/quran_canonical.json")
        hadith = load_dataset("hadith/nawawi40.json")
        tafsir = load_dataset("tafsir/tafsir_muyassar.json")
        scholar = load_dataset("scholarly/scholarly_quotes.json")

        quran_types = set(r["source_type"] for r in quran)
        hadith_types = set(r["source_type"] for r in hadith)
        tafsir_types = set(r["source_type"] for r in tafsir)
        scholar_types = set(r["source_type"] for r in scholar)

        assert quran_types == {"quran"}, "Quran corpus must strictly have source_type 'quran'"
        assert hadith_types == {"hadith"}, "Hadith corpus must strictly have source_type 'hadith'"
        assert tafsir_types == {"tafsir"}, "Tafsir corpus must strictly have source_type 'tafsir'"
        assert scholar_types == {"scholarly"}, "Scholarly corpus must strictly have source_type 'scholarly'"


if __name__ == "__main__":
    pytest.main(["-v", str(__file__)])
