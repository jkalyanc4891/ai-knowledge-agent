from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings


class RAGGenerator:
    """
    Calls the LLM to generate an answer based on the constructed prompt.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Generates an answer using the configured LLM.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )

        return response.choices[0].message.content.strip()

    def extract_sources(
        self,
        retrieved_contexts: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Simple passthrough of sources from retrieved contexts.

        In more advanced setups, you might:
        - post-process
        - deduplicate
        - rank sources
        """
        sources = []
        for ctx in retrieved_contexts:
            meta = ctx.get("metadata", {})
            sources.append(
                {
                    "text": ctx.get("text", ""),
                    "metadata": meta,
                    "score": ctx.get("score"),
                }
            )
        return sources