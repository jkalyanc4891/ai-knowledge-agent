from typing import List
from .planner_agent import PlannerAgent
from .retrieval_agent import RetrievalAgent
from .reasoning_agent import ReasoningAgent
from .validator_agent import ValidatorAgent
from app.rag.pipeline import RAGPipeline


class AgentOrchestrator:
    """
    Controls the full agent workflow:
    1. Planner decides retrieval strategy
    2. Retrieval agent fetches chunks
    3. Reasoning agent synthesizes multi-step reasoning
    4. RAG pipeline generates final answer
    5. Validator checks grounding + confidence
    """

    def __init__(self, rag_pipeline: RAGPipeline, vector_store):
        self.planner = PlannerAgent()
        self.retriever = RetrievalAgent(vector_store)
        self.reasoner = ReasoningAgent()
        self.validator = ValidatorAgent()
        self.rag = rag_pipeline

    def run(self, query: str, document_ids: List[str]):
        # 1. Planner decides retrieval strategy
        plan = self.planner.plan(query, document_ids)

        # ---------------------------
        # ⭐ FALLBACK PLAN PROTECTION
        # ---------------------------

        # Ensure plan is a dict
        if not isinstance(plan, dict):
            plan = {}

        # Validate retrieve flag
        retrieve_flag = plan.get("retrieve", True)
        if not isinstance(retrieve_flag, bool):
            retrieve_flag = True

        # Validate top_k
        top_k = plan.get("top_k", 5)
        if not isinstance(top_k, int) or top_k < 1:
            top_k = 5

        # Validate documents list
        docs = plan.get("documents", document_ids)
        if not isinstance(docs, list) or len(docs) == 0:
            docs = document_ids

        # ---------------------------
        # 2. Retrieve chunks
        # ---------------------------
        retrieved = self.retriever.retrieve(
            query=query,
            document_ids=docs,
            top_k=top_k,
        )

        # Build context for reasoning agent
        context_text = "\n\n".join([c["text"] for c in retrieved])

        # 3. Reasoning agent performs multi-step reasoning
        reasoning_output = self.reasoner.reason(query, context_text)

        # 4. RAG pipeline generates final answer
        rag_result = self.rag.run(query=query, document_ids=document_ids)

        # 5. Validator checks grounding
        validation = self.validator.validate(
            answer=rag_result.answer,
            context=context_text,
        )

        return {
            "answer": rag_result.answer,
            "reasoning": reasoning_output,
            "sources": rag_result.sources,
            "confidence": validation.get("confidence"),
            "grounded": validation.get("grounded"),
        }