from dataclasses import dataclass
from typing import List, Dict, Any

from app.vectorstore.base import BaseVectorStore
from app.rag.retriever import RAGRetriever
from app.rag.prompt_builder import PromptBuilder
from app.rag.generator import RAGGenerator


@dataclass
class RAGResult:
    answer: str
    sources: List[Dict[str, Any]]


class RAGPipeline:
    """
    End-to-end RAG pipeline:
    - Retrieve relevant chunks
    - Build prompts
    - Call LLM
    - Return answer + sources
    """

    def __init__(
        self,
        vector_store: BaseVectorStore,
        top_k: int = 5,
    ):
        self.retriever = RAGRetriever(vector_store=vector_store, top_k=top_k)
        self.prompt_builder = PromptBuilder()
        self.generator = RAGGenerator()

    def run(
        self,
        query: str,
        document_ids: List[str] | None = None,
    ) -> RAGResult:
        # 1. Retrieve
        retrieved = self.retriever.retrieve(query=query, document_ids=document_ids)

        # 2. Build prompts
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(query=query, contexts=retrieved)

        # 3. Generate answer
        answer = self.generator.generate(system_prompt=system_prompt, user_prompt=user_prompt)

        # 4. Collect sources
        sources = self.generator.extract_sources(retrieved)

        return RAGResult(answer=answer, sources=sources)