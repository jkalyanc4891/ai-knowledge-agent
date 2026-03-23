import json
from typing import List
from openai import OpenAI
from app.core.config import settings


class PlannerAgent:
    """
    Decides:
    - Whether retrieval is needed
    - How many chunks to retrieve (top_k)
    - Which documents to prioritize
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def plan(self, query: str, document_ids: List[str]) -> dict:
        system_prompt = (
            "You are a planning agent for a Retrieval-Augmented Generation (RAG) system. "
            "Your job is to decide how retrieval should be performed. "
            "You MUST respond with a STRICT JSON object ONLY, with no explanation. "
            "The JSON must contain exactly these keys: "
            "  - 'retrieve': a boolean "
            "  - 'top_k': an integer >= 1 "
            "  - 'documents': a list of document IDs to retrieve from "
            "Rules: "
            "  - 'top_k' must ALWAYS be an integer >= 1. Never return 0 or negative values. "
            "  - 'documents' must ALWAYS be a list (even if empty). "
            "  - Do NOT include any text outside the JSON. "
            "  - Do NOT include comments or trailing commas. "
            "Example valid output: "
            "{"
            "  \"retrieve\": true, "
            "  \"top_k\": 3, "
            "  \"documents\": [\"doc1\", \"doc2\"] "
            "}"
        )

        user_prompt = (
            f"User query: {query}\n"
            f"Available documents: {document_ids}\n\n"
            "Decide the retrieval strategy and respond ONLY with the JSON object described in the system instructions."
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )

        try:
            return json.loads(response.choices[0].message.content.strip())
        except Exception:
            return {"retrieve": True, "top_k": 5, "documents": document_ids}