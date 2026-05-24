from typing import Dict, Any
from app.validation.classifiers import PIIClassifier, ToxicityClassifier
from app.validation.filters import RedactionFilter
from app.validation.audit import SafetyAuditLogger
from app.validation.policies import SafetyPolicy
from app.agents.validator_agent import ValidatorAgent


# ============================================================
# Hallucination Classifier (Specific to RAG context)
# ============================================================

class HallucinationClassifier:
    """Wraps existing ValidatorAgent to check grounding."""

    def __init__(self):
        self.validator = ValidatorAgent()

    def classify(self, answer: str, context: str) -> Dict[str, Any]:
        return self.validator.validate(answer, context)


# ============================================================
# Unified Safety Engine
# ============================================================

class SafetyEngine:
    """
    Orchestrates the entire Validation directory:
    - Loads Rules (policies.py)
    - Runs Detection (classifiers.py)
    - Applies Masking (filters.py)
    - Records Actions (audit.py)
    """

    def __init__(self, use_llm_for_pii: bool = False):
        # ⭐ 2. Initialize Policies
        self.policy = SafetyPolicy()

        # ⭐ 3. Initialize Modular Classifiers
        self.pii = PIIClassifier(use_llm=use_llm_for_pii)
        self.toxicity = ToxicityClassifier()
        self.hallucination = HallucinationClassifier()

        # ⭐ 4. Initialize Modular Filters
        self.redactor = RedactionFilter()

    def run(self, answer: str, context: str) -> Dict[str, Any]:
        # Run detection
        pii_result = self.pii.classify(answer)
        toxicity_result = self.toxicity.classify(answer)
        hallucination_result = self.hallucination.classify(answer, context)

        # Apply redaction
        scrubbed_answer = self.redactor.apply(answer)

        # Compile report
        report = {
            "pii": pii_result,
            "toxicity": toxicity_result,
            "hallucination": hallucination_result,
            "safe": (
                    not pii_result.get("pii_present", False)
                    and not toxicity_result.get("toxic", False)
                    and hallucination_result.get("grounded", False)
            ),
            "scrubbed_answer": scrubbed_answer,
        }

        # ⭐ 5. Trigger the Audit Logger
        SafetyAuditLogger.log_decision(
            stage="generation_guardrails",
            input_text=answer,
            decision=report
        )

        return report


# ============================================================
# Convenience Function (Used by Orchestrator)
# ============================================================

def run_guardrails(answer: str, context: str) -> Dict[str, Any]:
    engine = SafetyEngine()
    return engine.run(answer, context)