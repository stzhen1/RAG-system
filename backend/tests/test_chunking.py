from app.core.chunking import recursive_chunk, semantic_chunk


def test_recursive_chunk_splits_long_text():
    text = "First paragraph.\n\n" * 50
    chunks = recursive_chunk(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 220


def test_recursive_chunk_short_text_returns_single():
    text = "This is a short text."
    chunks = recursive_chunk(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_recursive_chunk_respects_separators():
    text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five."
    chunks = recursive_chunk(text, chunk_size=50, chunk_overlap=5)
    for chunk in chunks:
        assert len(chunk) <= 60


def test_semantic_chunk_splits_on_sentence_boundaries():
    text = (
        "RAG is powerful. It combines search with LLMs. "
        "Vector search finds relevant documents. "
        "The LLM generates answers from context."
    )
    chunks = semantic_chunk(text, max_sentences=2)
    assert len(chunks) == 2
    for chunk in chunks:
        sentences = [s for s in chunk.split(". ") if s]
        assert len(sentences) <= 2


def test_recursive_chunk_empty_text():
    chunks = recursive_chunk("", chunk_size=200, chunk_overlap=20)
    assert chunks == []


def test_recursive_chunk_overlap_maintains_context():
    text = (
        "Section A content here. " * 10
        + "\n\n"
        + "Section B content here. " * 10
    )
    chunks = recursive_chunk(text, chunk_size=300, chunk_overlap=50)
    assert len(chunks) >= 2
    if len(chunks) >= 2:
        words_chunk0 = set(chunks[0].split())
        words_chunk1 = set(chunks[1].split())
        assert len(words_chunk0 & words_chunk1) > 0
