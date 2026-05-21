from typing import List
from app.adapters.base import EmbeddingProvider
from app.config import settings


class BGEM3EmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def dimension(self) -> int:
        return 1024


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        self.model = model
        self.api_key = api_key or settings.openai_api_key

    async def embed(self, texts: List[str]) -> List[List[float]]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in response.data]

    def dimension(self) -> int:
        return 1536


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str = "bge-m3", base_url: str = None):
        self.model = model
        self.base_url = base_url or settings.ollama_base_url

    async def embed(self, texts: List[str]) -> List[List[float]]:
        import httpx
        async with httpx.AsyncClient() as client:
            embeddings = []
            for text in texts:
                resp = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                resp.raise_for_status()
                data = resp.json()
                embeddings.append(data["embedding"])
            return embeddings

    def dimension(self) -> int:
        return 1024


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.embedding_provider
    if provider == "bge-m3":
        return BGEM3EmbeddingProvider(model_name=settings.embedding_model)
    elif provider == "openai":
        return OpenAIEmbeddingProvider(model=settings.embedding_model)
    elif provider == "ollama":
        return OllamaEmbeddingProvider(model=settings.embedding_model)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
