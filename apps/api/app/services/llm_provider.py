"""
MUSNAD AI - LLM & Embedding Provider (v2)
Abstraction layer over Google Gemini API with full heuristic fallback.

Heuristic Extractor v2 improvements:
  - Smart sentence segmentation (split at . ؟ ! not ، )
  - 9-layer classification covering all Islamic claim types
  - Preserved quoted blocks «...» as atomic units
  - CLAIM_EXTRACTION_FAILURE telemetry
  - Minimum word filter for fragments
"""
import json
import re
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMCallError(Exception):
    pass


class LLMValidationError(Exception):
    pass


# Arabic function words — pure stop-word segments are rejected
_AR_STOP = {
    "و", "أو", "ثم", "أن", "إن", "في", "من", "إلى", "على", "عن",
    "مع", "هو", "هي", "هم", "هذا", "هذه", "ذلك", "التي", "الذي",
    "كان", "يكون", "لا", "ما", "لم", "لن", "قد", "قط", "أما", "بل",
}


class LLMProvider:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self._client_available = True
        else:
            self._client_available = False

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calls Gemini to generate structured JSON.
        Falls back to heuristic extractor on quota / network errors.
        """
        if self._client_available and self.api_key and not settings.DEMO_MODE:
            try:
                model = genai.GenerativeModel(
                    model_name=settings.GEMINI_MODEL,
                    system_instruction=system_prompt,
                    generation_config={
                        "temperature": settings.GEMINI_TEMPERATURE,
                        "max_output_tokens": settings.GEMINI_MAX_TOKENS,
                        "response_mime_type": "application/json",
                    },
                )
                response = await model.generate_content_async(user_prompt)
                parsed = json.loads(response.text)
                logger.info("gemini_extraction_success", request_id=request_id,
                            claims_count=len(parsed.get("claims", [])))
                return parsed
            except Exception as e:
                logger.warning("gemini_call_failed_fallback_to_heuristic",
                               error=str(e), request_id=request_id)

        result = self._heuristic_claim_extraction(user_prompt)
        logger.info("heuristic_extraction_used", request_id=request_id,
                    claims_count=len(result.get("claims", [])))
        return result

    # =========================================================================
    # HEURISTIC EXTRACTION ENGINE v2
    # =========================================================================

    def _heuristic_claim_extraction(self, user_prompt: str) -> Dict[str, Any]:
        """
        General-purpose Arabic Islamic claim extractor.
        Steps:
          1. Extract text from triple-quoted prompt format.
          2. Smart-segment at sentence boundaries (not commas).
          3. Classify each segment using a 9-layer deterministic ruleset.
          4. Filter trivial/short fragments.
          5. Emit CLAIM_EXTRACTION_FAILURE telemetry if signals present but 0 claims.
        """
        match = re.search(r'"""(.*?)"""', user_prompt, re.DOTALL)
        content = match.group(1).strip() if match else user_prompt.strip()

        if not content:
            return {"claims": [], "language_detected": "ar",
                    "processing_notes": "Empty input"}

        segments = self._smart_segment(content)
        claims = []
        for idx, seg in enumerate(segments, start=1):
            result = self._classify_segment(seg, idx)
            if result is not None:
                claims.append(result)

        # Fallback: whole text as one claim if signal present but nothing extracted
        if not claims:
            if self._has_islamic_signal(content):
                claims.append(self._make_claim(1, content, "general_islamic_claim"))
                logger.error("CLAIM_EXTRACTION_FAILURE",
                             reason="Islamic signals present but segments all filtered",
                             content_sample=content[:120])
            else:
                claims.append(self._make_claim(1, content, "unknown", confidence=0.3))

        return {
            "claims": claims,
            "language_detected": "ar",
            "processing_notes": (
                f"Extracted via MUSNAD heuristic engine v2 ({len(claims)} claims)"
            ),
        }

    def _smart_segment(self, text: str) -> List[str]:
        """
        Split Arabic text at SENTENCE boundaries only.
        - Splits at: period (.), ؟, !, double newline
        - Does NOT split at: ، (Arabic comma), ؛ (semicolon)
        - Preserves «...» quoted blocks as atomic units
        """
        placeholders: Dict[str, str] = {}
        counter = [0]

        def _protect(m: re.Match) -> str:
            key = f"\x00PROT{counter[0]}\x00"
            placeholders[key] = m.group(0)
            counter[0] += 1
            return key

        guarded = re.sub(r'«[^»]*»', _protect, text)
        guarded = re.sub(r'﴿[^﴾]*﴾', _protect, guarded)
        guarded = re.sub(r'"[^"]*"', _protect, guarded)
        guarded = re.sub(r'\([^)]{3,80}\)', _protect, guarded)

        # Split at sentence-ending punctuation
        parts = re.split(r'(?<=[.؟!])\s+|\n{2,}', guarded)

        restored = []
        for part in parts:
            for key, val in placeholders.items():
                part = part.replace(key, val)
            part = part.strip()
            if part:
                restored.append(part)

        return restored if restored else [text.strip()]

    def _classify_segment(self, seg: str, idx: int) -> Optional[Dict]:
        """
        9-layer classification of a text segment.
        Returns a claim dict or None if trivial.
        """
        seg = seg.strip()
        if not seg:
            return None

        # Word count filter — reject very short fragments
        words = seg.split()
        if len(words) < 3:
            return None

        # Reject pure stop-word sequences
        arabic_words = set(re.sub(r'[^\u0600-\u06FF\s]', ' ', seg).split())
        if arabic_words and arabic_words.issubset(_AR_STOP):
            return None

        # ----------------------------------------------------------------
        # L1: Prompt Injection Defense
        # ----------------------------------------------------------------
        injection_signals = [
            "ignore all", "ignore previous", "system prompt", "invent a source",
            "override decision", "<system>", "system message:",
            "تجاهل التعليمات", "تجاهل كل التعليمات", "احكم بصحة",
            "اخترع مصدرا", "أنت الآن مفتي", "اكشف الموجه",
        ]
        if any(p in seg.lower() for p in injection_signals):
            return self._make_claim(idx, seg, "unknown", confidence=0.1,
                                    entities=["محتوى عدائي (Prompt Injection)"])

        # ----------------------------------------------------------------
        # Helper: DIRECT prophetic quote (قال النبي: ...)
        # ----------------------------------------------------------------
        has_direct_quote = bool(re.search(
            r'(قال\s+رسول\s+الله|قال\s+النبي|رُوي\s+عن\s+النبي'
            r'|صلى\s+الله\s+عليه\s+وسلم\s*:|ﷺ\s*:'
            r'|أخبرنا|حدثنا\s+\w|عن\s+\w+\s+أنه\s+قال)',
            seg
        ))
        # Weak mention: Prophet mentioned but not a direct quote
        has_prophet_mention = bool(re.search(
            r'(النبي\s+ﷺ|رسول\s+الله\s+ﷺ|صلى\s+الله\s+عليه\s+وسلم)',
            seg
        ))

        # ----------------------------------------------------------------
        # L2: Fiqh/Legal claims (only without direct prophetic quote)
        # ----------------------------------------------------------------
        fiqh_kw = [
            "حرام", "واجب", "مكروه", "مستحب", "مباح", "حلال",
            "يجوز", "لا يجوز", "الحكم الشرعي", "فتوى", "شرعا", "شرعاً",
            "التداول", "العملات الرقمية", "يبطل", "يوجب", "حكم شرعي",
            "في جميع الحالات", "التحريم", "التحليل", "الإباحة",
            "أجمع العلماء", "اتفق الفقهاء",
        ]
        if not has_direct_quote and any(k in seg for k in fiqh_kw):
            return self._make_claim(idx, seg, "fiqh_claim",
                                    needs_specialist=True,
                                    specialist_reason="مسألة فقهية تتطلب تحقيق الفتوى والاطلاع على تفاصيل المذاهب")

        # ----------------------------------------------------------------
        # L3: Quran verse
        # ----------------------------------------------------------------
        if re.search(
            r'(قال\s+الله\s+تعال[ىي]|قوله\s+تعال[ىي]|قال\s+تعال[ىي]'
            r'|سورة\s+[\u0600-\u06FF]|آية\s+\d+|في\s+المصحف'
            r'|﴿[^﴾]+﴾|بسم\s+الله\s+الرحمن\s+الرحيم|قل\s+هو\s+الله\s+أحد'
            r'|القرآن\s+الكريم|نص\s+قرآني|اقتباس\s+قرآني)',
            seg
        ):
            return self._make_claim(idx, seg, "quran_verse",
                                    entities=["القرآن الكريم"])

        # ----------------------------------------------------------------
        # L4: Hadith (DIRECT prophetic attribution only)
        # ----------------------------------------------------------------
        hadith_kw = [
            "في الحديث", "كما صح في الحديث", "كما ورد في الحديث",
            "الحديث الشريف", "قوله عليه الصلاة والسلام",
        ]
        if has_direct_quote or any(k in seg for k in hadith_kw):
            return self._make_claim(idx, seg, "hadith",
                                    attributions=["رسول الله صلى الله عليه وسلم"])


        # ----------------------------------------------------------------
        # L5: Source attribution ("ورد في البخاري", "رواه مسلم", etc.)
        # ----------------------------------------------------------------
        source_kw = [
            "صحيح البخاري", "صحيح مسلم", "سنن أبي داود", "سنن الترمذي",
            "سنن ابن ماجه", "مسند أحمد", "الموطأ", "الأربعين النووية",
            "أخرجه البخاري", "رواه مسلم", "رواه البخاري", "أخرجه مسلم",
            "أخرجه أبو داود", "رواه الترمذي", "خرّجه", "في المسند",
        ]
        source_pattern = re.compile(
            r'(ورد\s+(?:هذا\s+)?(?:الحديث|النص|القول)\s+في'
            r'|أخرجه\s+|رواه\s+|خرّجه\s+|في\s+صحيح\s+'
            r'|في\s+السنن|هذا\s+الحديث\s+(?:رواه|صحيح|حسن|ضعيف|موضوع)'
            r'|حديث\s+(?:صحيح|حسن|ضعيف|موضوع))'
        )
        if source_pattern.search(seg) or any(k in seg for k in source_kw):
            return self._make_claim(idx, seg, "source_claim",
                                    entities=["مصدر حديثي"])

        # ----------------------------------------------------------------
        # L6: Scholar attribution
        # ----------------------------------------------------------------
        scholar_re = re.compile(
            r'(?:قال|نص|ذكر|ذهب|روى|كتب|أفتى|يرى|قول|كلام)\s+'
            r'(?:الإمام\s+)?'
            r'(الشافعي|مالك|أحمد\s+بن\s+حنبل|أبي?\s+حنيفة|النووي'
            r'|ابن\s+تيمية|ابن\s+القيم|ابن\s+حجر|القرطبي|ابن\s+كثير'
            r'|الطبري|السيوطي|ابن\s+رشد|الغزالي|الماوردي|ابن\s+عبد\s+البر)'
        )
        scholar_name_re = re.compile(
            r'(?:الإمام\s+)'
            r'(الشافعي|مالك|أحمد\s+بن\s+حنبل|أبي?\s+حنيفة|النووي'
            r'|ابن\s+تيمية|ابن\s+القيم|ابن\s+حجر|القرطبي|ابن\s+كثير'
            r'|الطبري|السيوطي|ابن\s+رشد|الغزالي|الماوردي)'
        )
        demonyms = {"النووية", "النوويين", "الشافعية", "الحنفية",
                    "المالكية", "الحنابلة", "الماوردية"}
        if (scholar_re.search(seg) or scholar_name_re.search(seg)) and \
                not any(w in seg for w in demonyms):
            return self._make_claim(idx, seg, "scholarly_quote",
                                    attributions=["عالم إسلامي"])

        # ----------------------------------------------------------------
        # L7: General Islamic claim
        # ----------------------------------------------------------------
        islamic_kw = [
            "الإسلام", "المسلمين", "النبي", "الصحابة", "الدين",
            "الشريعة", "الإيمان", "العبادة", "الأخلاق", "السنة",
            "التوحيد", "القيامة", "الآخرة", "الجنة", "النار",
            "الصلاة", "الزكاة", "الصوم", "الحج", "الجهاد",
            "الصدق", "الأمانة", "التقوى", "العدل", "الرحمة",
        ]
        if any(k in seg for k in islamic_kw):
            return self._make_claim(idx, seg, "general_islamic_claim")

        # ----------------------------------------------------------------
        # L8: Historical Islamic
        # ----------------------------------------------------------------
        historical_kw = [
            "غزوة", "صلح", "معركة", "الهجرة النبوية", "للهجرة",
            "السنة الثانية", "السنة السادسة", "فتح مكة", "بدر", "أحد",
        ]
        if any(k in seg for k in historical_kw):
            return self._make_claim(idx, seg, "historical_claim",
                                    entities=["تاريخ وسيرة إسلامية"])

        # ----------------------------------------------------------------
        # L9: Unknown — only keep if enough words
        # ----------------------------------------------------------------
        if len(words) >= 6:
            return self._make_claim(idx, seg, "unknown", confidence=0.3)

        return None

    @staticmethod
    def _make_claim(
        idx: int,
        text: str,
        claim_type: str,
        needs_specialist: bool = False,
        specialist_reason: Optional[str] = None,
        entities: Optional[List[str]] = None,
        attributions: Optional[List[str]] = None,
        confidence: float = 0.92,
    ) -> Dict[str, Any]:
        return {
            "claim_index": idx,
            "original_text": text.strip(),
            "claim_type": claim_type,
            "entities": entities or [],
            "attributions": attributions or [],
            "references": [],
            "needs_specialist": needs_specialist,
            "specialist_reason": specialist_reason,
            "extraction_confidence": confidence,
        }

    @staticmethod
    def _has_islamic_signal(text: str) -> bool:
        signals = [
            "الله", "النبي", "رسول", "حديث", "قرآن", "آية", "سورة",
            "إسلام", "مسلم", "صلاة", "زكاة", "حج", "صوم", "جهاد",
            "حرام", "حلال", "واجب", "فتوى", "فقه", "شريعة",
            "بخاري", "مسلم", "ترمذي", "داود", "نووي", "تيمية",
            "شافعي", "مالك", "حنبل", "حنيفة", "ﷺ", "صلى الله",
        ]
        return any(s in text for s in signals)

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding using Gemini or deterministic mock fallback."""
        if self._client_available and self.api_key:
            try:
                res = genai.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    content=text,
                    task_type="retrieval_document",
                )
                return res["embedding"]
            except Exception as e:
                logger.warning("gemini_embed_failed", error=str(e))

        import numpy as np
        rng = np.random.RandomState(abs(hash(text)) % (2**32))
        vec = rng.randn(768)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    async def embed_query(self, text: str) -> List[float]:
        return await self.embed_text(text)


llm_provider = LLMProvider()
