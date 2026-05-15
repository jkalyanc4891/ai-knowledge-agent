import re
from abc import ABC, abstractmethod
from typing import Dict, Any
from openai import OpenAI
from app.core.config import settings


class SafetyClassifier(ABC):
    """
    Base classifier interface.
    """

    @abstractmethod
    def classify(self, text: str) -> Dict[str, Any]:
        ...


class PIIClassifier(SafetyClassifier):
    """
    Simple PII classifier using regex + optional LLM refinement.
    """

    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_REGEX = re.compile(r"\+?\d[\d\-\s]{7,}\d")

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if use_llm else None
        self.model = settings.OPENAI_MODEL

    def classify(self, text: str) -> Dict[str, Any]:
        findings = {
            "email": bool(self.EMAIL_REGEX.search(text)),
            "phone": bool(self.PHONE_REGEX.search(text)),
        }

        if self.use_llm and self.client:
            # Optional: LLM-based PII detection refinement
            prompt = (
                "Identify if the following text contains sensitive PII "
                "(names, addresses, IDs, financial info). Respond with JSON: "
                "{'pii_present': bool}.\n\n"
                f"Text:\n{text}"
            )
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            findings["llm_pii"] = "true" in resp.choices[0].message.content.lower()

        findings["pii_present"] = any(v for v in findings.values())
        return findings


class ToxicityClassifier(SafetyClassifier):
    """
    LLM-based toxicity / harmful content classifier.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def classify(self, text: str) -> Dict[str, Any]:
        prompt = (
            "Classify whether the following text is toxic, hateful, or promotes self-harm. "
            "Respond with JSON: {'toxic': bool, 'self_harm': bool}.\n\n"
            f"Text:\n{text}"
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        content = resp.choices[0].message.content
        # In production, parse JSON robustly; here we do a simple heuristic fallback
        return {
            "toxic": "toxic" in content.lower(),
            "self_harm": "self_harm" in content.lower(),
        }