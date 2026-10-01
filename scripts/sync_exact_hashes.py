import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
manifest_path = REPO_ROOT / "knowledge_base" / "manifest.json"
manifest = json.load(open(manifest_path, encoding="utf-8"))

for s in manifest["sources"]:
    fp = REPO_ROOT / s["file"]
    raw = open(fp, "rb").read()
    real_hash = hashlib.sha256(raw).hexdigest()
    s["file_sha256"] = real_hash
    print(f"{s['source_code']}: {real_hash}")

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

with open(REPO_ROOT / "knowledge-base" / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# Update COMPETITION_DATASET_FINAL.json
final_comp = REPO_ROOT / "COMPETITION_DATASET_FINAL.json"
if final_comp.exists():
    cdata = json.load(open(final_comp, encoding="utf-8"))
    bk = cdata["verified_corpora_inventory"]["breakdown"]
    bk["quran_verses"]["file_sha256"] = manifest["sources"][0]["file_sha256"]
    bk["al_arbain_al_nawawiyya"]["file_sha256"] = manifest["sources"][1]["file_sha256"]
    bk["sahih_al_bukhari"]["file_sha256"] = manifest["sources"][2]["file_sha256"]
    bk["sahih_muslim"]["file_sha256"] = manifest["sources"][3]["file_sha256"]
    bk["tafsir_al_muyassar"]["file_sha256"] = manifest["sources"][4]["file_sha256"]
    bk["scholarly_quotations"]["file_sha256"] = manifest["sources"][5]["file_sha256"]
    bk["fiqh_references"]["file_sha256"] = manifest["sources"][6]["file_sha256"]
    with open(final_comp, "w", encoding="utf-8") as f:
        json.dump(cdata, f, ensure_ascii=False, indent=2)

print("Manifest and COMPETITION_DATASET_FINAL updated with exact byte hashes.")
