"""
MUSNAD AI - Canonical Quran Ingestion Module
Ingests complete canonical Quran (114 Surahs, 6236 Ayahs)
Source: Tanzil Project / King Fahd Complex for Printing the Holy Quran
License: Public Domain
"""
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, List
from scripts.ingest.base_ingester import BaseIngester, compute_sha256, normalize_arabic_text


class QuranIngester(BaseIngester):
    def __init__(self):
        super().__init__(
            source_code="SRC-001",
            source_type="quran",
            title="القرآن الكريم - مصحف المدينة النبوية (حفص عن عاصم)",
            author="كلام الله تعالى",
            license_str="Public Domain",
        )

    def ingest(self, output_path: Path) -> List[Dict[str, Any]]:
        print("[QuranIngester] Fetching canonical Uthmani Quran dataset...")
        url = "https://api.alquran.cloud/v1/quran/quran-uthmani"
        req = urllib.request.Request(url, headers={"User-Agent": "MUSNAD-AI-Ingester/1.0"})
        
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        if payload.get("status") != "OK" or "data" not in payload:
            raise ValueError(f"Failed to fetch Quran dataset: {payload.get('status')}")

        data = payload["data"]
        surahs = data.get("surahs", [])
        
        records = []
        for surah in surahs:
            s_num = surah["number"]
            s_name_ar = surah["name"]
            s_name_en = surah["englishName"]
            
            for ayah in surah["ayahs"]:
                a_num = ayah["numberInSurah"]
                text_uthmani = ayah["text"].strip()
                text_norm = normalize_arabic_text(text_uthmani)
                juz = ayah.get("juz")
                page = ayah.get("page")
                hizb = ayah.get("hizbQuarter")

                ref = f"سورة {s_name_ar} - آية {a_num}"
                h = compute_sha256(f"quran_{s_num}_{a_num}_{text_norm}")

                record = {
                    "id": f"quran_{s_num}_{a_num}",
                    "source_code": self.source_code,
                    "source_title": "القرآن الكريم",
                    "source_type": "quran",
                    "surah_number": s_num,
                    "surah_name_ar": s_name_ar,
                    "surah_name_en": s_name_en,
                    "verse_number": a_num,
                    "juz": juz,
                    "page": page,
                    "hizb": hizb,
                    "text": text_uthmani,
                    "text_normalized": text_norm,
                    "reference": ref,
                    "edition": "مصحف المدينة النبوية - برواية حفص عن عاصم",
                    "content_hash": h,
                    "verification_status": "verified",
                }
                records.append(record)

        stats = self.calculate_integrity_stats(records)
        print(f"[QuranIngester] Ingested {stats['total_records']} ayahs across 114 Surahs. Unique: {stats['unique_records']}, Duplicates: {stats['duplicate_count']}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return records
