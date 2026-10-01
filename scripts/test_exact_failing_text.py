"""
Test the exact failing text via HTTP API to isolate the real problem.
"""
import asyncio, sys, io, json, urllib.request, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TEST_TEXT = """قال رسول الله ﷺ: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى». وقد ورد هذا الحديث في صحيح البخاري، وهو حديث صحيح. ويقول بعض الناس إن الإسلام يحث على الصدق والأمانة، وإن الصدق من أهم الأخلاق التي دعا إليها النبي ﷺ. وقال الإمام الشافعي: «العلم ما نفع، ليس العلم ما حفظ». كما أن من قال إن العملات الرقمية حلال قطعًا في جميع الحالات فقد أصدر حكمًا شرعيًا ثابتًا لا يحتاج إلى اختلاف أو نظر."""

payload = json.dumps({"content": TEST_TEXT}, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/analyses",
    data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode('utf-8')
        data = json.loads(raw)
        d = data.get("data", {})
        summary = d.get("summary", {})
        claims = d.get("claims", [])
        print(f"SUCCESS: total_claims={summary.get('total')}")
        print(f"  supported={summary.get('supported')}")
        print(f"  partially_supported={summary.get('partially_supported')}")
        print(f"  insufficient={summary.get('insufficient_evidence')}")
        print(f"  specialist={summary.get('specialist_referral')}")
        print(f"  has_exact_matches={summary.get('has_exact_matches')}")
        print()
        for i, c in enumerate(claims, 1):
            print(f"  CLAIM [{i}] type={c.get('claim_type')} status={c.get('status')}")
            print(f"           text={c.get('original_text', '')[:80]}")
            print(f"           evidence_count={len(c.get('supporting_evidence', []))}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f"HTTP ERROR {e.code}: {body[:500]}")
except Exception as e:
    print(f"ERROR: {e}")
