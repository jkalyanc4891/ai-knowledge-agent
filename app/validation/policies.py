from enum import Enum
from dataclasses import dataclass
from typing import List


class SafetySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyRule:
    id: str
    description: str
    category: str
    severity: SafetySeverity
    enabled: bool = True


class SafetyPolicy:
    """
    Defines safety rules and governance configuration.
    """

    def __init__(self, rules: List[SafetyRule] | None = None):
        self.rules = rules or self._default_rules()

    def _default_rules(self) -> List[SafetyRule]:
        return [
            SafetyRule(
                id="no_pii_leakage",
                description="Do not expose sensitive PII in responses.",
                category="pii",
                severity=SafetySeverity.CRITICAL,
            ),
            SafetyRule(
                id="no_hate_toxicity",
                description="Do not generate hateful or toxic content.",
                category="toxicity",
                severity=SafetySeverity.CRITICAL,
            ),
            SafetyRule(
                id="no_self_harm",
                description="Do not encourage or instruct self-harm.",
                category="self_harm",
                severity=SafetySeverity.CRITICAL,
            ),
        ]

    def get_rules_by_category(self, category: str) -> List[SafetyRule]:
        return [r for r in self.rules if r.category == category and r.enabled]

    def all_rules(self) -> List[SafetyRule]:
        return [r for r in self.rules if r.enabled]