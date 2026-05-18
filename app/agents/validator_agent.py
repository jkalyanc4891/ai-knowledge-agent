import json
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger


class ValidatorAgent:
    """
    Validates the final answer:
    - Checks grounding
    - Detects hallucinations
    - Assigns a confidence score

    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def validate(self, answer: str, context: str) -> dict:
        default_plan = {
            "grounded": False,
            "confidence": 0.0,
            "explanation": "Validation failed"
       }

        system_prompt = (
            "You are a validation agent in a Retrieval-Augmented Generation (RAG) system. "
            "Your job is to determine whether the provided answer is grounded in the given context. "
            "Use ONLY the information in the context. Do NOT add external knowledge or assumptions. "
            "You MUST respond with a STRICT JSON object ONLY, with no explanation outside the JSON. "
            "The JSON must contain exactly these keys: "
            "  - 'grounded': a boolean indicating whether the answer is supported by the context "
            "  - 'confidence': a float between 0 and 1 "
            "  - 'explanation': a short explanation describing why the answer is or is not grounded "
        )

        user_prompt = (
            f"Answer:\n{answer}\n\n"
            f"Context:\n{context}\n\n"
            "Evaluate whether the answer is grounded in the context and respond ONLY with the JSON object described in the system instructions."
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
            content = response.choices[0].message.content
            if not content:
                logger.warning("LLM validation response content was empty; using default plan.")
                return default_plan

            return json.loads(content.strip())

        except (json.JSONDecodeError, IndexError, AttributeError, TypeError) as e:
            logger.warning("Failed to parse LLM validator plan; using default. Error: %s", e)
            return default_plan