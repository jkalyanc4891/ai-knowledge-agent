from typing import List, Dict


class PromptBuilder:
    """
    Builds prompts for the RAG generator using retrieved context.
    """

    @staticmethod
    def build_system_prompt() -> str:
        return (
            "You are an AI assistant that answers questions based ONLY on the provided context. "
            "If the answer is not in the context, say you don't know. "
            "Be concise, accurate, and cite the relevant sources when possible."
        )

    @staticmethod
    def build_user_prompt(query: str, contexts: List[Dict]) -> str:
        """
        Build the user-facing prompt with embedded context.

        contexts: list of dicts with at least "text" and optional "metadata".
        """
        context_blocks = []
        for idx, ctx in enumerate(contexts):
            text = ctx.get("text", "")
            meta = ctx.get("metadata", {})
            source = meta.get("filename") or meta.get("document_id") or f"chunk-{idx}"
            block = f"[Source {idx+1} | {source}]\n{text}"
            context_blocks.append(block)

        context_str = "\n\n".join(context_blocks)

        prompt = (
            f"Context:\n{context_str}\n\n"
            f"Question: {query}\n\n"
            "Answer using ONLY the context above. If the answer is not present, say you don't know."
        )

        return prompt