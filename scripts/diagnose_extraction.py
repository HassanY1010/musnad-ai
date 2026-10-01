"""
Diagnostic script: trace the EXACT pipeline for the failing input text.
Run from musnad-ai root:
  python scripts/diagnose_extraction.py
"""
import asyncio, sys, os, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))

TEST_TEXT = """قال رسول الله ﷺ: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى». وقد ورد هذا الحديث في صحيح البخاري، وهو حديث صحيح. ويقول بعض الناس إن الإسلام يحث على الصدق والأمانة، وإن الصدق من أهم الأخلاق التي دعا إليها النبي ﷺ. وقال الإمام الشافعي: «العلم ما نفع، ليس العلم ما حفظ». كما أن من قال إن العملات الرقمية حلال قطعًا في جميع الحالات فقد أصدر حكمًا شرعيًا ثابتًا لا يحتاج إلى اختلاف أو نظر."""

async def main():
    from app.services.llm_provider import llm_provider
    from app.prompts.claim_extraction_v1 import CLAIM_EXTRACTION_SYSTEM, CLAIM_EXTRACTION_USER
    from app.services.claim_extractor import claim_extractor
    from app.core.config import settings

    print("=" * 70)
    print("STEP 0: CONFIG")
    print(f"  DEMO_MODE    = {settings.DEMO_MODE}")
    print(f"  KB_VERSION   = {settings.KB_VERSION}")
    print(f"  API_KEY_SET  = {bool(settings.GEMINI_API_KEY)}")
    print(f"  LLM_AVAIL    = {llm_provider._client_available}")

    print("\n" + "=" * 70)
    print("STEP 1: RAW INPUT")
    print(f"  Length: {len(TEST_TEXT)} chars")
    print(f"  Text  : {TEST_TEXT[:120]}...")

    print("\n" + "=" * 70)
    print("STEP 2: HEURISTIC EXTRACTION (direct call)")
    user_prompt = CLAIM_EXTRACTION_USER.format(text=TEST_TEXT)
    raw_result = llm_provider._heuristic_claim_extraction(user_prompt)
    raw_claims = raw_result.get("claims", [])
    print(f"  Extracted {len(raw_claims)} raw claims")
    for i, c in enumerate(raw_claims, 1):
        print(f"  [{i}] type={c['claim_type']} | text={c['original_text'][:80]!r}")

    print("\n" + "=" * 70)
    print("STEP 3: FULL EXTRACTOR (via claim_extractor.extract)")
    result = await claim_extractor.extract(TEST_TEXT, request_id="diag-001")
    print(f"  success={result.success}")
    print(f"  error  ={result.error_message}")
    print(f"  total_claims={result.total_claims}")
    for i, c in enumerate(result.claims, 1):
        print(f"  [{i}] type={c.claim_type} | text={c.original_text[:80]!r}")

if __name__ == "__main__":
    asyncio.run(main())
