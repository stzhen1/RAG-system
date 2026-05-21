import uuid
from typing import Dict, Any
from app.celery_app.worker import celery_app
from app.services.parsing_service import ParsingService
from app.core.chunking import recursive_chunk
from app.adapters.embedding_adapter import get_embedding_provider
from app.config import settings


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def parse_document(self, document_id: str, file_content: bytes, filename: str) -> Dict[str, Any]:
    try:
        service = ParsingService()
        result = service.parse(file_content, filename)

        if "error" in result:
            if "exceeds max pages" in result["error"]:
                return {"status": "failed", "error": result["error"], "document_id": document_id}
            raise Exception(result["error"])

        return {
            "status": "parsed",
            "document_id": document_id,
            "text": result.get("text", ""),
            "page_count": result.get("page_count", 1),
            "file_type": result.get("file_type", ""),
        }
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def chunk_document(self, parsed_result: Dict[str, Any]) -> Dict[str, Any]:
    try:
        text = parsed_result.get("text", "")
        if not text:
            return {"status": "failed", "error": "Empty text", **parsed_result}

        child_chunks = recursive_chunk(
            text,
            chunk_size=settings.child_chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        parent_chunks = recursive_chunk(
            text,
            chunk_size=settings.parent_chunk_size,
            chunk_overlap=settings.chunk_overlap * 2,
        )

        chunks_data = []
        for i, child in enumerate(child_chunks):
            parent_idx = min(i * len(parent_chunks) // len(child_chunks), len(parent_chunks) - 1)
            chunks_data.append({
                "chunk_id": str(uuid.uuid4()),
                "parent_content": parent_chunks[parent_idx],
                "child_content": child,
                "chunk_index": i,
                "chunk_type": "text",
            })

        return {
            "status": "chunked",
            "chunks": chunks_data,
            **{k: v for k, v in parsed_result.items() if k != "status"},
        }
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def embed_chunks(self, chunked_result: Dict[str, Any]) -> Dict[str, Any]:
    try:
        chunks = chunked_result.get("chunks", [])
        child_texts = [c["child_content"] for c in chunks]

        provider = get_embedding_provider()
        import asyncio
        loop = asyncio.get_event_loop()
        embeddings = loop.run_until_complete(provider.embed(child_texts))

        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]
            chunk["embedding_model"] = settings.embedding_model
            chunk["embedding_version"] = 1

        return {
            "status": "embedded",
            "chunks": chunks,
            **{k: v for k, v in chunked_result.items() if k not in ("status", "chunks")},
        }
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def index_chunks(self, embedded_result: Dict[str, Any]) -> Dict[str, Any]:
    document_id = embedded_result.get("document_id")
    chunks = embedded_result.get("chunks", [])

    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, Distance, VectorParams

    client = QdrantClient(url=settings.qdrant_url)

    try:
        client.get_collection(settings.qdrant_collection)
    except Exception:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
        )

    points = []
    for chunk in chunks:
        point_id = str(uuid.uuid4())
        chunk["qdrant_point_id"] = point_id
        points.append(PointStruct(
            id=point_id,
            vector=chunk["embedding"],
            payload={
                "chunk_id": chunk["chunk_id"],
                "document_id": document_id,
                "content": chunk["child_content"],
                "parent_content": chunk["parent_content"],
                "chunk_index": chunk["chunk_index"],
                "chunk_type": chunk["chunk_type"],
                "embedding_model": chunk.get("embedding_model", ""),
                "embedding_version": chunk.get("embedding_version", 1),
            },
        ))

    client.upsert(collection_name=settings.qdrant_collection, points=points)
    _store_chunks_sync(document_id, chunks)

    return {
        "status": "indexed",
        "document_id": document_id,
        "indexed_chunks": len(chunks),
    }


def _store_chunks_sync(document_id: str, chunks: list):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.db.models import Chunk

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        for chunk in chunks:
            db_chunk = Chunk(
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                content=chunk["child_content"],
                chunk_type=chunk.get("chunk_type", "text"),
                embedding_model=chunk.get("embedding_model", ""),
                embedding_version=chunk.get("embedding_version", 1),
                qdrant_point_id=chunk.get("qdrant_point_id"),
            )
            session.add(db_chunk)
        session.commit()


def run_ingestion_pipeline(document_id: str, file_content: bytes, filename: str):
    from celery import chain

    workflow = chain(
        parse_document.s(document_id, file_content, filename),
        chunk_document.s(),
        embed_chunks.s(),
        index_chunks.s(),
    )
    workflow.apply_async()
