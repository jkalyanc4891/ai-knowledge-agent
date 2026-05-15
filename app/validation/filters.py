from abc import ABC, abstractmethod
from typing import Dict, Any
import re


class SafetyFilter(ABC):
    """
    Base filter interface to transform or block content.
    """

    @abstractmethod
    def apply(self, text: str, context: Dict[str, Any] | None = None) -> str:
        ...


class RedactionFilter(SafetyFilter):
    """
    Simple redaction filter for PII-like patterns.
    """

    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_REGEX = re.compile(r"\+?\d[\d\-\s]{7,}\d")

    def apply(self, text: str, context: Dict[str, Any] | None = None) -> str:
        text = self.EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
        text = self.PHONE_REGEX.sub("[REDACTED_PHONE]", text)
        return text