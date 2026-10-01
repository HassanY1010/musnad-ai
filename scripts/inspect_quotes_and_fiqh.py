import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
scholarly = json.load(open(REPO_ROOT / "knowledge_base" / "v0.2_expanded" / "scholarly" / "scholarly_quotes.json", encoding="utf-8"))
fiqh = json.load(open(REPO_ROOT / "knowledge_base" / "v0.2_expanded" / "fiqh" / "fiqh_references.json", encoding="utf-8"))

print("=== 15 SCHOLARLY QUOTES ===")
for i, s in enumerate(scholarly, 1):
    status = s.get("verification_status")
    print(f"{i}. [{status}] {s.get('scholar')} | Work: {s.get('work')} (Vol: {s.get('volume')}, Page: {s.get('page')})")
    print(f"   Quote: {s.get('text')}")
    print(f"   Hash: {s.get('content_hash')}")

print("\n=== 6 FIQH REFERENCES ===")
for i, f in enumerate(fiqh, 1):
    status = f.get("verification_status")
    req = f.get("requires_specialist_review")
    print(f"{i}. [{status}] ReqSpecialist: {req} | Topic: {f.get('topic')}")
    print(f"   Scholar/Council: {f.get('scholar')} | Source: {f.get('source')} (Vol: {f.get('volume')}, Page: {f.get('page')})")
    print(f"   Ruling: {f.get('text')}")
    print(f"   Hash: {f.get('content_hash')}")
