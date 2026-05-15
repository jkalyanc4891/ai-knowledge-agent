from typing import Dict, Any
from datetime import datetime
from app.core.logging import logger


class SafetyAuditLogger:
    """
    Centralized safety audit logger for governance, compliance, and traceability.

    Responsibilities:
    - Log every safety decision (PII detection, toxicity, redaction, blocking)
    - Provide structured, machine‑readable audit entries
    """

    @staticmethod
    def log_decision(
        stage: str,
        input_text: str,
        decision: Dict[str, Any],
    ) -> None:
        """
        Parameters:
        - stage: The pipeline stage (e.g., "ingestion", "retrieval", "generation", "response")
        - input_text: The text evaluated by the safety engine
        - decision: Dict containing classifier results, actions, and rule triggers
        """
        logger.info(
            "SafetyDecision | stage=%s | decision=%s | snippet=%s",
            stage,
            decision,
            input_text[:200].replace("\n", " "),
        )
