import re
from typing import Dict, Any
from abc import ABC, abstractmethod
from openai import OpenAI

from app.core.config import settings
from app.agents.validator_agent import ValidatorAgent


# ============================================================
# Base Interface
# ============================================================

class SafetyClassifier(ABC):
    """
    Base interface for all safety classifiers.
    """

    @abstractmethod
    def classify(self, text: str) -> Dict[str, Any]:
        ...


# ============================================================
# PII Classifier
# ============================================================

class PIIClassifier(SafetyClassifier):
    """
    Detects emails, phone numbers, and optionally uses LLM refinement.
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

        # Optional LLM refinement
        if self.use_llm and self.client:
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


# ============================================================
# Toxicity Classifier
# ============================================================

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
        content = resp.choices[0].message.content.lower()

        return {
            "toxic": "true" in content or "toxic" in content,
            "self_harm": "true" in content or "self_harm" in content,
        }


# ============================================================
# Hallucination / Grounding Classifier
# ============================================================

class HallucinationClassifier(SafetyClassifier):
    """
    Wraps your existing ValidatorAgent to check grounding.
    """

    def __init__(self):
        self.validator = ValidatorAgent()

    def classify(self, answer: str, context: str) -> Dict[str, Any]:
        """
        Returns:
            {
                "grounded": bool,
                "confidence": float,
                "explanation": str
            }
        """
        return self.validator.validate(answer, context)


# ============================================================
# Unified Safety Engine
# ============================================================

class SafetyEngine:
    """
    Runs all safety checks:
    - PII
    - Toxicity
    - Hallucination / grounding
    """

    def __init__(self, use_llm_for_pii: bool = False):
        self.pii = PIIClassifier(use_llm=use_llm_for_pii)
        self.toxicity = ToxicityClassifier()
        self.hallucination = HallucinationClassifier()

    def run(self, answer: str, context: str) -> Dict[str, Any]:
        """
        Runs all guardrails and returns a unified safety report.
        """

        pii_result = self.pii.classify(answer)
        toxicity_result = self.toxicity.classify(answer)
        hallucination_result = self.hallucination.classify(answer, context)

        return {
            "pii": pii_result,
            "toxicity": toxicity_result,
            "hallucination": hallucination_result,
            "safe": (
                not pii_result.get("pii_present", False)
                and not toxicity_result.get("toxic", False)
                and hallucination_result.get("grounded", False)
            ),
        }


# ============================================================
# Convenience Function (Used by Orchestrator)
# ============================================================

def run_guardrails(answer: str, context: str) -> Dict[str, Any]:
    """
    Single entry point used by the orchestrator.
    """
    engine = SafetyEngine()
    return engine.run(answer, context)
