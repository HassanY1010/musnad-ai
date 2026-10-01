"""
MUSNAD AI - Base Ingestion Module
Implements standard pipeline:
  SOURCE -> VALIDATION -> USAGE CHECK -> PARSER -> NORMALIZATION -> STRUCTURING -> PROVENANCE -> HASH -> QUALITY
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


def compute_sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def normalize_arabic_text(text: str) -> str:
    """Canonical Arabic text normalizer."""
    if not text:
        return ""
    # Remove harakat / diacritics
    t = re.sub(r'[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED]', '', text)
    # Normalize Alef forms
    t = re.sub(r'[إأآٱ]', 'ا', t)
    # Normalize Ta Marbuta
    t = t.replace('ة', 'ه')
    # Normalize Yaa
    t = t.replace('ى', 'ي')
    # Collapse multiple whitespaces
    t = re.sub(r'\s+', ' ', t).strip()
    return t


class BaseIngester:
    def __init__(self, source_code: str, source_type: str, title: str, author: str, license_str: str):
        self.source_code = source_code
        self.source_type = source_type
        self.title = title
        self.author = author
        self.license_str = license_str
        self.retrieval_date = datetime.now(timezone.utc).isoformat()

    def validate_provenance(self, records: List[Dict[str, Any]]) -> bool:
        """Ensure every record has valid source, text, and no corruptions."""
        for r in records:
            if not r.get("text") or len(r["text"].strip()) == 0:
                return False
            if not r.get("source_code"):
                return False
            if not r.get("content_hash"):
                return False
        return True

    def calculate_integrity_stats(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        hashes = set()
        duplicates = 0
        for r in records:
            h = r["content_hash"]
            if h in hashes:
                duplicates += 1
            else:
                hashes.add(h)

        return {
            "total_records": len(records),
            "unique_records": len(hashes),
            "duplicate_count": duplicates,
            "provenance_valid": duplicates == 0,
        }
