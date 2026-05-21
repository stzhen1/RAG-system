from typing import List
from app.adapters.base import RerankerProvider
from app.config import settings


class BGERerankerProvider(RerankerProvider):
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from FlagEmbedding import FlagReranker
            self._model = FlagReranker(self.model_name, use_fp16=True)

    async def rerank(self, query: str, documents: List[str]) -> List[dict]:
        self._load_model()
        pairs = [[query, doc] for doc in documents]
        scores = self._model.compute_score(pairs)

        results = []
        for i, score in enumerate(scores):
            results.append({
                "index": i,
                "score": float(score),
                "document": documents[i],
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results


class JinaRerankerProvider(RerankerProvider):
    def __init__(self, model: str = "jina-reranker-v2-base-multilingual"):
        self.model = model

    async def rerank(self, query: str, documents: List[str]) -> List[dict]:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.jina.ai/v1/rerank",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": self.model,
                    "query": query,
                    "documents": documents,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            results = [
                {"index": r["index"], "score": r["relevance_score"], "document": documents[r["index"]]}
                for r in data["results"]
            ]
            results.sort(key=lambda r: r["score"], reverse=True)
            return results


def get_reranker() -> RerankerProvider:
    return BGERerankerProvider(model_name=settings.reranker_model)
