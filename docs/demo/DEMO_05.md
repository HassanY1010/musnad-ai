# LIVE DEMO 05 — Unsupported Claim & Safe Scientific Abstention

**Scenario Title:** Safe Abstention on Unindexed Claims  
**Purpose:** Demonstrate that MUSNAD does not hallucinate sources, and does NOT claim a text is fabricated simply because it is absent from the local database.

---

### Exact Input
```arabic
قال رسول الله: اطلبوا العلم ولو في المريخ فإن حب الاستكشاف واجب
```

### Expected Behavior
- **Zero Hallucination:** No fake citation or source fabricated.
- **Status:** `insufficient_evidence`.
- **Honest Boundary Communication:** Clarifies that lack of evidence does not prove falsity.

### Actual Verified System Result
- **Classification:** `hadith`
- **Retrieved Chunks:** 0
- **Status:** `insufficient_evidence`
- **Explanation:**  
  `لم نتمكن من إثبات هذا الادعاء من المصادر المتاحة للنظام. هذا لا يعني بالضرورة أن الادعاء خاطئ أو باطل في نفسه، بل يقتضي الرجوع إلى المصادر الموسعة أو المتخصصين.`

### Why This Result Matters
Directly prevents AI from fabricating Hadith books, page numbers, or authenticity rulings. Respects the Islamic scholarly rule: *The absence of evidence is not evidence of absence* (عدم الوجدان لا يستلزم عدم الوجود).

### Possible Judge Question
*"Why doesn't the system declare this hadith to be fabricated (موضوع) since it mentions Mars?"*

### Recommended Answer
*"Because declaring a text 'theologically fabricated' requires positive historical and chain evidence from classical compendia of fabrications (كتب الموضوعات). A computer system cannot declare a statement fabricated solely because its local index lacks the record. Scientific honesty requires returning 'insufficient evidence' with specialist referral."*
