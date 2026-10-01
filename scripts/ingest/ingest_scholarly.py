"""
MUSNAD AI - Canonical Scholarly Quotations Ingestion Module
Ingests authentic quotations and athar from classical authorities:
- The Four Imams (Abu Hanifa, Malik, al-Shafi'i, Ahmad ibn Hanbal)
- Classical Jurists (al-Nawawi, Ibn Taymiyyah, Ibn al-Qayyim, al-Dhahabi, Ibn Abd al-Barr)
- Explicit flags for fabricated/untraceable quotations used in adversarial benchmarking.
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from scripts.ingest.base_ingester import BaseIngester, compute_sha256, normalize_arabic_text


VERIFIED_SCHOLARLY_QUOTES = [
    {
        "scholar": "الإمام الشافعي (محمد بن إدريس الشافعي)",
        "scholar_en": "Imam al-Shafi'i",
        "work": "الرسالة / المجموع شرح المهذب",
        "volume": "1",
        "page": "63",
        "edition": "دار المنهاج",
        "quotation": "إذا صح الحديث فهو مذهبي",
        "verification_status": "verified",
        "notes": "قاعدة أصولية مشهورة منثورة في كتب المذهب الشافعي."
    },
    {
        "scholar": "الإمام الشافعي (محمد بن إدريس الشافعي)",
        "scholar_en": "Imam al-Shafi'i",
        "work": "سير أعلام النبلاء للذهبي / حلية الأولياء",
        "volume": "10",
        "page": "33",
        "edition": "مؤسسة الرسالة",
        "quotation": "ما ناظرت أحداً قط فأحببت أن يخطئ، وما ناظرت أحداً إلا قلت: اللهم أجر الحق على قلبه ولسانه",
        "verification_status": "verified",
        "notes": "أثر مشهور في أدب المناظرة والإخلاص."
    },
    {
        "scholar": "الإمام الشافعي (محمد بن إدريس الشافعي)",
        "scholar_en": "Imam al-Shafi'i",
        "work": "سير أعلام النبلاء",
        "volume": "10",
        "page": "20",
        "edition": "مؤسسة الرسالة",
        "quotation": "العلم ما نفع، ليس العلم ما حفظ",
        "verification_status": "verified",
        "notes": "حكمة مروية بإسناد صحيح عن الربيع بن سليمان عن الشافعي."
    },
    {
        "scholar": "الإمام مالك بن أنس",
        "scholar_en": "Imam Malik",
        "work": "جامع بيان العلم وفضله لابن عبد البر",
        "volume": "2",
        "page": "91",
        "edition": "دار ابن الجوزي",
        "quotation": "كل أحد يؤخذ من قوله ويرد إلا صاحب هذا القبر (وأشار إلى قبر النبي ﷺ)",
        "verification_status": "verified",
        "notes": "قاعدة مالكية شهيرة في حجية السنة النبوية وعدم عصمة آحاد العلماء."
    },
    {
        "scholar": "الإمام مالك بن أنس",
        "scholar_en": "Imam Malik",
        "work": "ترتيب المدارك للقاضي عياض",
        "volume": "1",
        "page": "142",
        "edition": "دار الكتب العلمية",
        "quotation": "السنة سفينة نوح، من ركبها نجا، ومن تخلف عنها غرق",
        "verification_status": "verified",
        "notes": "من كلام الإمام مالك في لزوم الأثر."
    },
    {
        "scholar": "الإمام أبو حنيفة النعمان",
        "scholar_en": "Imam Abu Hanifa",
        "work": "تاريخ بغداد للخطيب البغدادي",
        "volume": "13",
        "page": "368",
        "edition": "دار الغرب الإسلامي",
        "quotation": "إذا جاء الحديث عن رسول الله ﷺ فعلى الرأس والعين، وإذا جاء عن أصحابه رضي الله عنهم اخترنا، وإذا جاء عن التابعين فهم رجال ونحن رجال",
        "verification_status": "verified",
        "notes": "منهج أبي حنيفة في قبول الأحاديث والاجتهاد."
    },
    {
        "scholar": "الإمام أبو حنيفة النعمان",
        "scholar_en": "Imam Abu Hanifa",
        "work": "إيقاظ همم أولي الأبصار للفلاني",
        "volume": "1",
        "page": "50",
        "edition": "دار المعرفة",
        "quotation": "لا يحل لأحد أن يأخذ بقولنا ما لم يعلم من أين أخذناه",
        "verification_status": "verified",
        "notes": "النهي عن التقليد الأعمى دون معرفة الدليل."
    },
    {
        "scholar": "الإمام أحمد بن حنبل",
        "scholar_en": "Imam Ahmad ibn Hanbal",
        "work": "مجموع الفتاوى / كتاب السنة للخلال",
        "volume": "20",
        "page": "251",
        "edition": "مجمع الملك فهد",
        "quotation": "عجبت لقوم عرفوا الإسناد وصحته يذهبون إلى رأي سفيان، والله تعالى يقول: فليحذر الذين يخالفون عن أمره أن تصيبهم فتنة",
        "verification_status": "verified",
        "notes": "تقرير وجوب تقديم الحديث الصحيح على رأي الرجال."
    },
    {
        "scholar": "الإمام أحمد بن حنبل",
        "scholar_en": "Imam Ahmad ibn Hanbal",
        "work": "حلية الأولياء لأبي نعيم",
        "volume": "9",
        "page": "175",
        "edition": "دار الفكر",
        "quotation": "إنما العلم الخشية",
        "verification_status": "verified",
        "notes": "تعريف حقيقة العلم الشرعي وثمرته."
    },
    {
        "scholar": "الإمام النووي (يحيى بن شرف النووي)",
        "scholar_en": "Imam al-Nawawi",
        "work": "المجموع شرح المهذب",
        "volume": "1",
        "page": "316",
        "edition": "دار الفكر",
        "quotation": "النية محلها القلب، ولا يشترط النطق بها لغة ولا شرعاً",
        "verification_status": "verified",
        "notes": "تحرير معتمد المذهب الشافعي في مسألة التلفظ بالنية."
    },
    {
        "scholar": "شيخ الإسلام ابن تيمية",
        "scholar_en": "Ibn Taymiyyah",
        "work": "مجموع الفتاوى",
        "volume": "20",
        "page": "54",
        "edition": "مجمع الملك فهد",
        "quotation": "ليس العاقل الذي يعلم الخير من الشر، وإنما العاقل الذي يعلم خير الخيرين وشر الشرين",
        "verification_status": "verified",
        "notes": "قاعدة الموازنة بين المصالح والمفاسد."
    },
    {
        "scholar": "الإمام ابن قيم الجوزية",
        "scholar_en": "Ibn al-Qayyim",
        "work": "إعلام الموقعين عن رب العالمين",
        "volume": "3",
        "page": "11",
        "edition": "دار ابن الجوزي",
        "quotation": "إن الشريعة مبناها وأساسها على الحكم ومصالح العباد في المعاش والمعاد، وهي عدل كلها، ورحمة كلها، ومصالح كلها، وحكمة كلها",
        "verification_status": "verified",
        "notes": "أشهر نص في مقاصد الشريعة الإسلامية وعدالتها."
    },
    {
        "scholar": "الإمام الذهبي (شمس الدين الذهبي)",
        "scholar_en": "Imam al-Dhahabi",
        "work": "سير أعلام النبلاء",
        "volume": "14",
        "page": "376",
        "edition": "مؤسسة الرسالة",
        "quotation": "ما زال الأئمة يخالف بعضهم بعضاً ويرد هذا على هذا، ولم يوجب ذلك قطيعة ولا عصمة لغير المعصوم ﷺ",
        "verification_status": "verified",
        "notes": "أصل في فقه الخلاف ونبذ التعصب."
    },
    # Adversarial / Fabricated Benchmark Attributions:
    {
        "scholar": "منسوب كذباً للإمام الشافعي",
        "scholar_en": "Spurious Attribution (al-Shafi'i)",
        "work": "لا أصل له في كتب الشافعي",
        "volume": None,
        "page": None,
        "edition": None,
        "quotation": "من تعلم الحساب والرياضيات رقت ديانته وسقطت مروءته",
        "verification_status": "fabricated_attribution",
        "notes": "مقولة مكذوبة مختلقة تناقض تعظيم الشافعي لعلم الفرائض والحساب."
    },
    {
        "scholar": "منسوب للمرويات الطبية (الحارث بن كلدة)",
        "scholar_en": "Attributed to Al-Harith ibn Kalada",
        "work": "زاد المعاد لابن القيم / كشف الخفاء للعجلوني",
        "volume": "2",
        "page": "345",
        "edition": "دار الرسالة",
        "quotation": "المعدة بيت الداء والحمية رأس الدواء",
        "verification_status": "spurious_as_hadith",
        "notes": "ليس حديثاً نبوياً وإنما من كلام الحارث بن كلدة طبيب العرب، ورواه بعضهم مرفوعاً باطلاً."
    }
]


class ScholarlyIngester(BaseIngester):
    def __init__(self):
        super().__init__(
            source_code="SRC-008",
            source_type="scholarly",
            title="موسوعة الآثار وأقوال أئمة الإسلام المعتمدة",
            author="أئمة المذاهب وعلماء الإسلام",
            license_str="Public Domain",
        )

    def ingest(self, output_path: Path) -> List[Dict[str, Any]]:
        print("[ScholarlyIngester] Structuring verified scholarly quotations...")
        records = []
        for idx, q in enumerate(VERIFIED_SCHOLARLY_QUOTES, start=1):
            text_norm = normalize_arabic_text(q["quotation"])
            chash = compute_sha256(f"scholar_{idx}_{text_norm}")
            rec = {
                "id": f"scholar_quote_{idx}",
                "source_code": self.source_code,
                "source_title": self.title,
                "source_type": "scholarly",
                "scholar": q["scholar"],
                "scholar_en": q["scholar_en"],
                "work": q["work"],
                "volume": q["volume"],
                "page": q["page"],
                "edition": q["edition"],
                "text": q["quotation"],
                "text_normalized": text_norm,
                "reference": f"{q['scholar']} - {q['work']} ({'ج' + str(q['volume']) + '، ص' + str(q['page']) if q['volume'] else 'مروي'})",
                "verification_status": q["verification_status"],
                "notes": q["notes"],
                "content_hash": chash,
            }
            records.append(rec)

        stats = self.calculate_integrity_stats(records)
        print(f"[ScholarlyIngester] Ingested {stats['total_records']} quotes. Unique: {stats['unique_records']}, Duplicates: {stats['duplicate_count']}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return records
