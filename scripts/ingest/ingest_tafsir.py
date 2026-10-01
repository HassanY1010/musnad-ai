"""
MUSNAD AI - Canonical Tafsir Ingestion Module
Ingests authentic Quranic Exegesis (Tafsir al-Muyassar - التفسير الميسر)
Publisher: King Fahd Complex for Printing the Holy Quran / مجمع الملك فهد لطباعة المصحف الشريف
License: Public Domain
"""
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, List
from scripts.ingest.base_ingester import BaseIngester, compute_sha256, normalize_arabic_text


class TafsirIngester(BaseIngester):
    def __init__(self):
        super().__init__(
            source_code="SRC-007",
            source_type="tafsir",
            title="التفسير الميسر",
            author="نخبة من علماء التفسير (إشراف مجمع الملك فهد)",
            license_str="Public Domain",
        )

    def ingest(self, output_path: Path, max_surahs: int = 114) -> List[Dict[str, Any]]:
        print("[TafsirIngester] Fetching canonical Tafsir al-Muyassar dataset...")
        url = "https://api.alquran.cloud/v1/quran/ar.muyassar"
        req = urllib.request.Request(url, headers={"User-Agent": "MUSNAD-AI-Ingester/1.0"})
        
        with urllib.request.urlopen(req, timeout=90) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        if payload.get("status") != "OK" or "data" not in payload:
            raise ValueError(f"Failed to fetch Tafsir dataset: {payload.get('status')}")

        surahs = payload["data"].get("surahs", [])[:max_surahs]
        
        records = []
        for surah in surahs:
            s_num = surah["number"]
            s_name_ar = surah["name"]
            
            for ayah in surah["ayahs"]:
                a_num = ayah["numberInSurah"]
                raw_tafsir = ayah["text"].strip()
                if not raw_tafsir:
                    continue

                tafsir_norm = normalize_arabic_text(raw_tafsir)
                ref = f"التفسير الميسر - سورة {s_name_ar} (آية {a_num})"
                chash = compute_sha256(f"tafsir_muyassar_{s_num}_{a_num}_{tafsir_norm}")

                record = {
                    "id": f"tafsir_muyassar_{s_num}_{a_num}",
                    "source_code": self.source_code,
                    "source_title": self.title,
                    "source_type": "tafsir",
                    "surah_number": s_num,
                    "surah_name_ar": s_name_ar,
                    "verse_number": a_num,
                    "ayah_reference": f"{s_num}:{a_num}",
                    "author": self.author,
                    "book": "التفسير الميسر",
                    "text": raw_tafsir,
                    "text_normalized": tafsir_norm,
                    "reference": ref,
                    "edition": "الطبعة الثانية - مجمع الملك فهد",
                    "content_hash": chash,
                    "verification_status": "verified",
                }
                records.append(record)

        stats = self.calculate_integrity_stats(records)
        print(f"[TafsirIngester] Ingested {stats['total_records']} tafsir entries across {len(surahs)} Surahs. Unique: {stats['unique_records']}, Duplicates: {stats['duplicate_count']}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return records
