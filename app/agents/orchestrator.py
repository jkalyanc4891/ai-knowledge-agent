import logging
from typing import List
from pydantic import ValidationError

from .planner_agent import PlannerAgent
from .retrieval_agent import RetrievalAgent
from .reasoning_agent import ReasoningAgent
from .schemas import AgentPlan
from app.rag.pipeline import RAGPipeline
from app.validation.guardrails import run_guardrails

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Controls the full agent workflow:
    1. Planner decides retrieval strategy
    2. Retrieval agent fetches chunks
    3. Reasoning agent synthesizes multi-step reasoning
    4. RAG pipeline generates final answer
    5. Guardrails check safety, PII, and grounding
    """

    def __init__(self, rag_pipeline: RAGPipeline, vector_store):
        self.planner = PlannerAgent()
        self.retriever = RetrievalAgent(vector_store)
        self.reasoner = ReasoningAgent()
        self.rag = rag_pipeline

    def run(self, query: str, document_ids: List[str]):
        # 1. Planner decides retrieval strategy
        raw_plan = self.planner.plan(query, document_ids)

        # ---------------------------
        # ⭐ FALLBACK PLAN PROTECTION
        # ---------------------------
        try:
            # This handles all type checking, defaults, and coercion in one go
            plan = AgentPlan.model_validate(raw_plan)
        except (ValidationError, TypeError) as e:
            # If the LLM output is total garbage,
            # use a completely empty model which uses all defaults.
            logger.warning(f"Planner returned invalid schema. Falling back to defaults. Error: {e}")
            plan = AgentPlan()

        # Handle the dynamic fallback for document IDs
        final_docs = plan.documents if plan.documents else document_ids

        # ---------------------------
        # 2. Retrieve chunks
        # ---------------------------
        retrieved = self.retriever.retrieve(
            query=query,
            document_ids=final_docs,
            top_k=plan.top_k,
        )

        # Build context for reasoning agent
        context_text = "\n\n".join([c["text"] for c in retrieved])

        # 3. Reasoning agent performs multi-step reasoning
        reasoning_output = self.reasoner.reason(query, context_text)

        # 4. RAG pipeline generates final answer
        rag_result = self.rag.run(query=query, document_ids=document_ids)

        # 5. Run Full Safety Guardrails
        # The guardrails runs PII checks, Toxicity checks and the ValidatorAgent grounding check.
        safety_report = run_guardrails(
            answer=rag_result.answer,
            context=context_text,
        )

        # Extract the hallucination/grounding data from the unified report
        hallucination_data = safety_report.get("hallucination", {})

        return {
            "answer": safety_report.get("scrubbed_answer", rag_result.answer),
            "reasoning": reasoning_output,
            "sources": rag_result.sources,
            "confidence": hallucination_data.get("confidence"),
            "grounded": hallucination_data.get("grounded"),
            "safe": safety_report.get("safe"),
            "safety_report": safety_report,
        }