from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Return embeddings for each input text."""
        ...

    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding vector dimension."""
        ...


class LLMProvider(ABC):
    @abstractmethod
    async def chat_stream(self, messages: List[dict], **kwargs):
        """Yield response chunks as strings."""
        ...


class RerankerProvider(ABC):
    @abstractmethod
    async def rerank(self, query: str, documents: List[str]) -> List[dict]:
        """Return [{index, score, document}, ...] sorted by score descending."""
        ...
