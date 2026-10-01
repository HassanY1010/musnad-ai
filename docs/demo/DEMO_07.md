# LIVE DEMO 07 — Fabricated / Unverified Scholarly Attribution

**Scenario Title:** Preventing Misattribution to Classical Scholars  
**Purpose:** Demonstrate that mentioning a famous scholar (e.g., Al-Shafi'i, Malik, Ibn Taymiyyah) does not trick the engine into validating an ungrounded claim.

---

### Exact Input
```arabic
قال الإمام الشافعي رحمه الله: من تعلم لغة البرمجة بايثون فقد حاز شرف علوم الآلة
```

### Expected Behavior
- **Classification:** `scholarly_quote`.
- **Retrieval Match:** Zero verified occurrences in canonical works (*Al-Umm*, *Al-Risala*).
- **Status:** `needs_review` / `insufficient_evidence`.
- **Zero Invention:** Engine does not invent a fictional book or page number.

### Actual Verified System Result
- **Classification:** `scholarly_quote`
- **Retrieved Chunks:** 0
- **Status:** `needs_review`
- **Explanation:**  
  `هذا الادعاء يتعلق بنسبة قول لعالم معين؛ يتطلب الرجوع لكتب التراجم والمصنفات المعتمدة للتحقق من ثبوته وسياقه. لم يتم العثور على أصل مثبت للقول في المصادر المفهرسة.`

### Why This Result Matters
Social media frequently attributes modern self-help quotes, motivational phrases, or political rhetoric to classical imams. MUSNAD flags unverified attributions for rigorous historical review.

### Possible Judge Question
*"What sources are needed to verify scholarly quotes in full production?"*

### Recommended Answer
*"Full production requires indexing comprehensive biographical dictionaries (كتب التراجم والسير) such as Siyar A'lam al-Nubala by Al-Dhahabi and Tabaqat al-Shafi'iyya, along with verified digital recensions of the complete works of the major imams."*
