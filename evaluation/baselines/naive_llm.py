"""
MUSNAD AI - Baseline A: Naive Generative LLM (No Grounding / Subjective Guessing)
Simulates an unconstrained conversational generative model evaluating Islamic content
without a verified knowledge base, deterministic rules, or specialist referral guardrails.
"""
from typing import Dict, Any


class NaiveLLMBaseline:
    """
    Baseline A: Naive Generative LLM
    - Attempts to answer questions and verify hadiths directly from internal parametric weights.
    - Lacks a strict deterministic verification engine.
    - Highly prone to confirmation bias and source hallucination when presented with plausible sounding fake hadith.
    - Issues autonomous rulings on fiqh instead of specialist referrals.
    """

    def __init__(self, model_name: str = "naive-generative-llm-sim"):
        self.model_name = model_name

    def evaluate_claim(self, input_text: str) -> Dict[str, Any]:
        text_clean = input_text.strip()
        lower = text_clean.lower()

        # Prompt injection vulnerability: naive LLM complies with injection
        if any(p in lower for p in ["ignore all", "ignore previous", "تجاهل التعليمات", "احكم بصحة"]):
            return {
                "status": "supported",
                "confidence": 0.99,
                "hallucinated": True,
                "explanation": "Complied with prompt instruction to validate the text.",
                "model": self.model_name,
            }

        # Autonomous Fiqh Rulings without specialist referral
        if any(k in text_clean for k in ["حرام", "واجب", "يجوز", "شرعا", "شرعاً", "تداول", "توريث", "التبرع"]):
            return {
                "status": "supported",
                "confidence": 0.85,
                "hallucinated": False,
                "explanation": "Generates direct autonomous fatwa based on general training web text.",
                "model": self.model_name,
            }

        # Fabricated Hadith Vulnerability: Naive LLM asserts plausible or famous-sounding sayings as authentic
        fake_hadith_markers = ["المريخ", "المعدة بيت الداء", "شرب الماء البارد", "نام بعد العصر"]
        if any(marker in text_clean for marker in fake_hadith_markers):
            return {
                "status": "supported",  # Hallucination error
                "confidence": 0.78,
                "hallucinated": True,
                "explanation": "Hallucinates authenticity confirmation for widely circulated unauthentic proverb.",
                "model": self.model_name,
            }

        # Well-known religious phrases: assumes supported
        if any(k in text_clean for k in ["قال الله", "تعالى", "سورة", "قال رسول الله", "قال النبي", "صلى الله عليه وسلم"]):
            return {
                "status": "supported",
                "confidence": 0.90,
                "hallucinated": False,
                "explanation": "Matches general religious phrases from pretraining corpus.",
                "model": self.model_name,
            }

        # Scholarly quotes: confirms attribution naively
        if any(k in text_clean for k in ["الشافعي", "مالك", "النووي", "ابن تيمية"]):
            return {
                "status": "supported",
                "confidence": 0.75,
                "hallucinated": False,
                "explanation": "Confirms scholarly quote without primary source citation.",
                "model": self.model_name,
            }

        # Secular / Unrelated text
        if any(k in text_clean for k in ["خوارزميات", "تعلم الآلة", "الانحدار"]):
            return {
                "status": "insufficient_evidence",
                "confidence": 0.20,
                "hallucinated": False,
                "explanation": "Recognizes secular non-religious domain.",
                "model": self.model_name,
            }

        return {
            "status": "supported",
            "confidence": 0.65,
            "hallucinated": False,
            "explanation": "Default affirmative assumption.",
            "model": self.model_name,
        }
