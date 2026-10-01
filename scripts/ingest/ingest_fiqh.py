"""
MUSNAD AI - Source-Backed Fiqh Reference Ingestion Module
Stores verified fiqh references and Islamic Fiqh Academy resolutions.
Ensures contemporary and complex ijtihad questions are explicitly flagged with `requires_specialist_review: True`.
Prevents the system from functioning as an autonomous fatwa engine.
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from scripts.ingest.base_ingester import BaseIngester, compute_sha256, normalize_arabic_text


FIQH_SOURCE_REFERENCES = [
    {
        "topic": "العبادات - الصلاة",
        "question": "ما حكم قراءة سورة الفاتحة في كل ركعة من ركعات الصلاة؟",
        "ruling_text": "قراءة الفاتحة ركن من أركان الصلاة للمنفرد والإمام في كل ركعة، لقوله ﷺ: لا صلاة لمن لم يقرأ بفاتحة الكتاب",
        "madhhab": "جمهور الفقهاء (مالكية، شافعية، حنابلة)",
        "scholar": "الإمام النووي / ابن قدامة",
        "source": "المجموع شرح المهذب / المغني",
        "edition": "دار إحياء التراث",
        "volume": "3",
        "page": "284",
        "verification_status": "verified",
        "requires_specialist_review": False,
        "notes": "مسألة إجماعية في الركنية العامة للأصل."
    },
    {
        "topic": "العبادات - الصيام",
        "question": "هل يفسد صوم من أكل أو شرب ناسياً في نهار رمضان؟",
        "ruling_text": "من أكل أو شرب ناسياً فصومه صحيح ولا قضاء عليه ولا كفارة، لقول النبي ﷺ: من نسي وهو صائم فأكل أو شرب فليتم صومه فإنما أطعمه الله وسقاه",
        "madhhab": "جمهور الأئمة (الشافعي، أحمد، أبو حنيفة)",
        "scholar": "الإمام الترمذي / ابن حجر",
        "source": "فتح الباري شرح صحيح البخاري",
        "edition": "دار المعرفة",
        "volume": "4",
        "page": "160",
        "verification_status": "verified",
        "requires_specialist_review": False,
        "notes": "متفق عليه بالنص الصحيح الصريح."
    },
    {
        "topic": "المعاملات المالية المعاصرة - العملات المشفرة",
        "question": "ما حكم تداول العملات الرقمية والمشفرة والبيتكوين؟",
        "ruling_text": "تداول العملات المشفرة مسألة مستجدة معاصرة تكتنفها مخاطر الغرر والتقلبات الحادة وغياب الضمانات السيادية، وقد صدرت فيها فتاوى متباينة بين المجامع الفقهية ودور الإفتاء، وتحتاج إلى دراسة واقع التعامل وطبيعة كل عملة",
        "madhhab": "معاصر / نوازل",
        "scholar": "مجمع الفقه الإسلامي الدولي / هيئة كبار العلماء / دار الإفتاء المصرية",
        "source": "قرارات مجمع الفقه الإسلامي الدولي ومؤتمر المعاملات المالية الحديثة",
        "edition": "الأمانة العامة للمجمع",
        "volume": "الدورة 24",
        "page": "قرار رقم 235",
        "verification_status": "requires_institutional_ijtihad",
        "requires_specialist_review": True,
        "notes": "نازلة معاصرة تتطلب إحالة وجوبية للمختصين والمجامع الفقهية المعتمدة."
    },
    {
        "topic": "المعاملات المالية المعاصرة - المشتقات والتأمين التجاري",
        "question": "ما حكم عقود التأمين التجاري التقليدي وعقود الخيارات والتحوط المالي؟",
        "ruling_text": "التأمين التجاري التقليدي قائم على الغرر والمقامرة والربا بنوعيه فضل ونسيئة، والبديل الشرعي هو التأمين التكافلي الإسلامي القائم على التعاون والتبرع",
        "madhhab": "قرار مجمعي إجماعي",
        "scholar": "مجلس مجمع الفقه الإسلامي الدولي برابطة العالم الإسلامي",
        "source": "قرارات المجمع الفقهي الإسلامي بمكة المكرمة",
        "edition": "رابطة العالم الإسلامي",
        "volume": "الدورة الأولى",
        "page": "القرار رقم 5",
        "verification_status": "verified_institutional_decision",
        "requires_specialist_review": True,
        "notes": "تتطلب استشارة خبير رقابة شرعية في تفاصيل العقود والمستندات."
    },
    {
        "topic": "القضايا الطبية المعاصرة - نقل الأعضاء والموت الدماغي",
        "question": "ما حكم التبرع بالأعضاء بعد الموت الدماغي المتحقق طبياً؟",
        "ruling_text": "يجوز نقل العضو من إنسان ميت إلى إنسان حي تتوقف حياته على ذلك العضو أو تكون سلامة وظيفة أساسية فيه متوقفة على ذلك، بشرط تحقق الوفاة بالشروط الطبية الشرعية وعدم الاتجار بالأعضاء",
        "madhhab": "قرار مجمعي معتمد",
        "scholar": "مجمع الفقه الإسلامي الدولي التابع لمنظمة التعاون الإسلامي",
        "source": "مجلة مجمع الفقه الإسلامي",
        "edition": "العدد الرابع",
        "volume": "1",
        "page": "509",
        "verification_status": "verified_institutional_decision",
        "requires_specialist_review": True,
        "notes": "نازلة طبية يلزم فيها التثبت من التقرير الطبي ولجنة الخبراء المعتمدة."
    },
    {
        "topic": "المعاملات المعاصرة - التورق المصرفي المنظم",
        "question": "ما حكم التورق المصرفي المنظم كما تجريه بعض المصارف المعاصرة؟",
        "ruling_text": "التورق المنظم الذي تلتزم فيه المؤسسة المالية بتوكيل العميل في بيع السلعة وتسليم النقد له غير جائز شرعاً؛ لما فيه من شبهة العينة والتحايل على الربا",
        "madhhab": "قرار مجمعي",
        "scholar": "مجمع الفقه الإسلامي الدولي",
        "source": "قرارات المجمع الفقهي الإسلامي (قرار رقم 179)",
        "edition": "منظمة التعاون الإسلامي",
        "volume": "الدورة 19",
        "page": "179",
        "verification_status": "verified_institutional_decision",
        "requires_specialist_review": True,
        "notes": "يستلزم الرجوع لهيئة الرقابة الشرعية لكل مؤسسة وتدقيق آليات القبض الفعلي."
    }
]


class FiqhIngester(BaseIngester):
    def __init__(self):
        super().__init__(
            source_code="SRC-009",
            source_type="fiqh",
            title="سجل المراجع والقرارات الفقهية والمجمعية المعتمدة",
            author="مجامع الفقه الإسلامي وأئمة المذاهب",
            license_str="Public Domain / Institutional Resolutions",
        )

    def ingest(self, output_path: Path) -> List[Dict[str, Any]]:
        print("[FiqhIngester] Ingesting source-backed fiqh references...")
        records = []
        for idx, item in enumerate(FIQH_SOURCE_REFERENCES, start=1):
            text_norm = normalize_arabic_text(item["ruling_text"])
            chash = compute_sha256(f"fiqh_{idx}_{text_norm}")
            rec = {
                "id": f"fiqh_ref_{idx}",
                "source_code": self.source_code,
                "source_title": self.title,
                "source_type": "fiqh",
                "topic": item["topic"],
                "question": item["question"],
                "text": item["ruling_text"],
                "text_normalized": text_norm,
                "madhhab": item["madhhab"],
                "scholar": item["scholar"],
                "source": item["source"],
                "edition": item["edition"],
                "volume": item["volume"],
                "page": item["page"],
                "verification_status": item["verification_status"],
                "requires_specialist_review": item["requires_specialist_review"],
                "reference": f"{item['source']} ({item['scholar']}) - {item['topic']}",
                "notes": item["notes"],
                "content_hash": chash,
            }
            records.append(rec)

        stats = self.calculate_integrity_stats(records)
        print(f"[FiqhIngester] Ingested {stats['total_records']} fiqh cases. Specialist referral required: {sum(1 for r in records if r['requires_specialist_review'])}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return records
