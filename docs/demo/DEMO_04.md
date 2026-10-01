# LIVE DEMO 04 — Textual Variant Analysis (Hadith)

**Scenario Title:** Detecting Minor Textual Variation Without False Fabrication Claims  
**Purpose:** Demonstrate structured textual variant analysis when user citation diverges slightly from canonical wording (singular vs plural).

---

### Exact Input
```arabic
إنما الأعمال بالنية ولكل امرئ ما نوى
```
*(Uses singular `بالنية` instead of canonical plural `بالنيات`)*

### Expected Behavior
- **Divergence Detection:** Engine recognizes high thematic similarity ($0.71$) but flags the textual difference.
- **Status:** `partially_supported`.
- **Structured Difference Analysis:** Identifies singular vs. plural difference.

### Actual Verified System Result
- **Status:** `partially_supported`
- **Matched Source:** صحيح البخاري #1
- **Difference Breakdown:**
  ```text
  User Text:             إنما الأعمال بالنية ولكل امرئ ما نوى
  Canonical Text:        إنما الأعمال بالنيات وإنما لكل امرئ ما نوى
  Differing User Words:  ['بالنية', 'ولكل']
  Differing Canonical:   ['بالنيات', 'وانما']
  Difference Type:       مفرد مقابل جمع (singular vs plural)
  Similarity:            0.71
  ```
- **Explanation:**
  `النصوص المسترجعة تؤيد المعنى العام للادعاء مع وجود فروق في السياق أو الصياغة.`  
  `[تحليل الفروق: مفرد مقابل جمع — اللفظ الوارد: بالنية، ولكل مقابل اللفظ المعتمد: بالنيات، وانما]`

### Why This Result Matters
Avoids two extremes: blindly validating altered citations as identical, or falsely accusing a well-known narration variant of being "fabricated" (*Mawdu'*).

### Possible Judge Question
*"Why didn't you just mark this test as supported?"*

### Recommended Answer
*"In Hadith textual criticism, transmitting by meaning (الرواية بالمعنى) or subtle lexical variances must be transparently noted to scholars and researchers. Certifying an altered word as the literal canonical text would violate scientific and theological standards."*
