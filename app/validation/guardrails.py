from dataclasses import dataclass
from typing import Dict, Any
from .policies import SafetyPolicy, SafetySeverity
from .classifiers import PIIClassifier, ToxicityClassifier
from .filters import RedactionFilter
from .audit import SafetyAuditLogger


@dataclass
class SafetyDecision:
    allowed: bool
    modified_text: str
    reasons: Dict[str, Any]


class SafetyEngine:
    """
    Central safety/guardrails engine:
    - Evaluates policies
    - Runs classifiers
    - Applies filters
    - Logs decisions
    """

    def __init__(self, policy: SafetyPolicy | None = None):
        self.policy = policy or SafetyPolicy()
        self.pii_classifier = PIIClassifier(use_llm=False)
        self.toxicity_classifier = ToxicityClassifier()
        self.redaction_filter = RedactionFilter()

    def evaluate(self, text: str, stage: str = "response") -> SafetyDecision:
        reasons: Dict[str, Any] = {}

        # PII
        pii_rules = self.policy.get_rules_by_category("pii")
        if pii_rules:
            pii_result = self.pii_classifier.classify(text)
            reasons["pii"] = pii_result

        # Toxicity / self-harm
        tox_rules = self.policy.get_rules_by_category("toxicity") + \
                    self.policy.get_rules_by_category("self_harm")
        if tox_rules:
            tox_result = self.toxicity_classifier.classify(text)
            reasons["toxicity"] = tox_result

        # Decide allow/block
        allowed = True

        if reasons.get("pii", {}).get("pii_present"):
            # For now, we redact instead of blocking
            text = self.redaction_filter.apply(text)
            reasons["action_pii"] = "redacted"

        if reasons.get("toxicity", {}).get("toxic") or reasons.get("toxicity", {}).get("self_harm"):
            # High severity → block
            allowed = False
            reasons["action_toxicity"] = "blocked"

        decision = SafetyDecision(
            allowed=allowed,
            modified_text=text,
            reasons=reasons,
        )

        SafetyAuditLogger.log_decision(stage=stage, input_text=text, decision=reasons)
        return decision