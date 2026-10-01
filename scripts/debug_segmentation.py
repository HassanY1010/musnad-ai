"""
Quick check: what does _smart_segment produce for the failing text?
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'apps', 'api'))

from app.services.llm_provider import LLMProvider

TEXT = """قال رسول الله ﷺ: «إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى». وقد ورد هذا الحديث في صحيح البخاري، وهو حديث صحيح. ويقول بعض الناس إن الإسلام يحث على الصدق والأمانة، وإن الصدق من أهم الأخلاق التي دعا إليها النبي ﷺ. وقال الإمام الشافعي: «العلم ما نفع، ليس العلم ما حفظ». كما أن من قال إن العملات الرقمية حلال قطعًا في جميع الحالات فقد أصدر حكمًا شرعيًا ثابتًا لا يحتاج إلى اختلاف أو نظر."""

provider = LLMProvider.__new__(LLMProvider)
segs = provider._smart_segment(TEXT)
print(f"Total segments: {len(segs)}")
for i, s in enumerate(segs, 1):
    print(f"  [{i}] {repr(s)}")
