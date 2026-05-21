from typing import List, Dict, Any, Optional
from app.adapters.embedding_adapter import get_embedding_provider
from app.adapters.reranker_adapter import get_reranker
from app.core.context_builder import ContextBuilder
from app.config import settings


class RetrievalService:
    def __init__(self):
        self.embedding_provider = get_embedding_provider()
        self.reranker = get_reranker()
        self.context_builder = ContextBuilder()

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, str]] = None,
        top_k: int = None,
        rerank_top_n: int = None,
    ) -> List[Dict[str, Any]]:
        top_k = top_k or settings.retrieval_top_k
        rerank_top_n = rerank_top_n or settings.rerank_top_n

        vector_results = await self._vector_search(query, top_k=top_k, filter=filters)
        bm25_results = await self._bm25_search(query, top_k=top_k, filter=filters)
        merged = self._merge_results(vector_results, bm25_results, top_k * 2)

        if merged:
            documents = [r["content"] for r in merged]
            reranked = await self._rerank(query, documents)
            merged = reranked[:rerank_top_n]

        return merged

    async def retrieve_context(
        self,
        query: str,
        filters: Optional[Dict[str, str]] = None,
        max_tokens: int = 8000,
    ) -> str:
        results = await self.search(query, filters=filters)
        return self.context_builder.build(results, max_tokens=max_tokens)

    async def _vector_search(
        self, query: str, top_k: int = 30, filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        from qdrant_client import AsyncQdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        query_embedding = (await self.embedding_provider.embed([query]))[0]

        qdrant_filter = None
        if filter:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter.items()
            ]
            qdrant_filter = Filter(must=conditions)

        client = AsyncQdrantClient(url=settings.qdrant_url)
        try:
            results = await client.search(
                collection_name=settings.qdrant_collection,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=qdrant_filter,
                with_payload=True,
            )
            return [
                {
                    "chunk_id": r.payload.get("chunk_id", ""),
                    "content": r.payload.get("content", ""),
                    "score": float(r.score),
                    "page": r.payload.get("page"),
                    "source": "vector",
                }
                for r in results
            ]
        finally:
            await client.close()

    async def _bm25_search(
        self, query: str, top_k: int = 30, filter: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        from sqlalchemy import text
        from app.db.session import async_session

        ts_query = " & ".join(query.split())
        sql = text("""
            SELECT
                id::text AS chunk_id,
                content,
                ts_rank(content_tsv, to_tsquery('english', :query)) AS score,
                page
            FROM chunks
            WHERE content_tsv @@ to_tsquery('english', :query)
              AND deleted_at IS NULL
            ORDER BY score DESC
            LIMIT :limit
        """)

        async with async_session() as session:
            result = await session.execute(sql, {"query": ts_query, "limit": top_k})
            rows = result.fetchall()

        return [
            {
                "chunk_id": row.chunk_id,
                "content": row.content,
                "score": float(row.score),
                "page": row.page,
                "source": "bm25",
            }
            for row in rows
        ]

    def _merge_results(
        self, vector: List[Dict], bm25: List[Dict], max_total: int
    ) -> List[Dict]:
        seen_ids = set()
        merged = []

        max_bm25 = max((r["score"] for r in bm25), default=1.0)

        for r in sorted(vector + bm25, key=lambda r: r["score"], reverse=True):
            cid = r["chunk_id"]
            if cid not in seen_ids:
                seen_ids.add(cid)
                if r["source"] == "bm25":
                    r["score"] = r["score"] / max_bm25 * 0.8 if max_bm25 > 0 else 0
                merged.append(r)
            if len(merged) >= max_total:
                break

        return merged

    async def _rerank(self, query: str, documents: List[str]) -> List[Dict[str, Any]]:
        results = await self.reranker.rerank(query, documents)
        return [
            {
                "chunk_id": "",
                "content": r["document"],
                "score": r["score"],
                "source": "reranked",
            }
            for r in results
        ]
