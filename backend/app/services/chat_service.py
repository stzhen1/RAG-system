from typing import List, Dict, Any, Optional, AsyncGenerator
from app.services.retrieval_service import RetrievalService
from app.adapters.llm_adapter import get_llm_provider

SYSTEM_PROMPT = """You are an enterprise knowledge assistant. Answer questions based on the provided context.

Rules:
- Answer ONLY from the provided context. If the context does not contain the answer, say "I don't have enough information to answer this question."
- Cite the source document and page when available.
- Be concise and accurate.
- Format code snippets with markdown.
- If the context is insufficient, ask clarifying questions.

Context:
{context}"""


class ChatService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.llm_provider = get_llm_provider()

    async def chat(
        self,
        query: str,
        history: List[Dict[str, str]],
        filters: Optional[Dict[str, str]] = None,
        max_context_tokens: int = 8000,
    ) -> AsyncGenerator[str, None]:
        context = await self.retrieval_service.retrieve_context(
            query, filters=filters, max_tokens=max_context_tokens
        )

        system_content = SYSTEM_PROMPT.format(context=context or "No relevant documents found.")
        messages = [{"role": "system", "content": system_content}]

        for msg in history[-20:]:
            messages.append(msg)

        messages.append({"role": "user", "content": query})

        async for chunk in self.llm_provider.chat_stream(messages, temperature=0.1):
            yield chunk
