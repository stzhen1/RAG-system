import pytest
from app.adapters.embedding_adapter import BGEM3EmbeddingProvider, OpenAIEmbeddingProvider


@pytest.mark.asyncio
async def test_bge_m3_embeds_texts():
    provider = BGEM3EmbeddingProvider(model_name="BAAI/bge-m3")
    texts = ["This is a test sentence.", "Another sentence for embedding."]
    embeddings = await provider.embed(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == provider.dimension()
    assert provider.dimension() == 1024


@pytest.mark.asyncio
async def test_bge_m3_single_text():
    provider = BGEM3EmbeddingProvider(model_name="BAAI/bge-m3")
    embeddings = await provider.embed(["Hello world"])
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 1024


@pytest.mark.asyncio
async def test_openai_embedding_returns_correct_shape():
    provider = OpenAIEmbeddingProvider(model="text-embedding-3-small", api_key="test-key")
    assert provider.dimension() == 1536
