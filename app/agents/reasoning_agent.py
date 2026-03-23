from openai import OpenAI
from app.core.config import settings


class ReasoningAgent:
    """
    Performs multi-step reasoning on top of retrieved context.
    Useful for:
    - Chain-of-thought style reasoning
    - Multi-hop question answering
    - Complex synthesis
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def reason(self, query: str, context: str) -> str:
        system_prompt = (
            "You are a reasoning agent in a Retrieval-Augmented Generation (RAG) system. "
            "Your job is to perform multi-step reasoning ONLY using the provided context. "
            "You MUST NOT use outside knowledge, assumptions, or invented facts. "
            "If the context does not contain enough information to answer or reason, "
            "you MUST explicitly say: 'The context does not provide enough information.' "
            "Rules: "
            " - Use ONLY the provided context. "
            " - Do NOT add facts that are not present in the context. "
            " - Do NOT guess or infer beyond what the context supports. "
            " - Break down your reasoning into clear, logical steps. "
            " - If context is empty, return an empty reasoning string. "
            "Your output should be a short reasoning trace, not the final answer."
        )

        user_prompt = (
            f"Question: {query}\n\n"
            f"Context:\n{context}\n\n"
            "Provide a clear, step-by-step reasoning process based ONLY on the context above. "
            "Do NOT provide a final answer, only the reasoning steps."
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()