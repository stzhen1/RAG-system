from app.core.context_builder import ContextBuilder


def test_deduplicate_removes_duplicates():
    builder = ContextBuilder()
    chunks = [
        {"content": "Chunk A content", "score": 0.9},
        {"content": "Chunk A content", "score": 0.8},
        {"content": "Chunk B content", "score": 0.7},
    ]
    result = builder.build(chunks, max_tokens=10000)
    assert result.count("Chunk A content") == 1


def test_token_budget_truncates():
    builder = ContextBuilder()
    long_text = "word " * 2000
    chunks = [{"content": long_text, "score": 0.9}]
    result = builder.build(chunks, max_tokens=500)
    assert len(result.split()) < 1000


def test_empty_chunks_returns_empty():
    builder = ContextBuilder()
    result = builder.build([], max_tokens=1000)
    assert result == ""


def test_window_merge_combines_adjacent():
    builder = ContextBuilder()
    chunks = [
        {"content": "Paragraph one about topic.", "score": 0.8, "chunk_index": 0},
        {"content": "Paragraph two about topic.", "score": 0.7, "chunk_index": 1},
        {"content": "Paragraph three unrelated.", "score": 0.3, "chunk_index": 5},
    ]
    result = builder.build(chunks, max_tokens=1000)
    assert "Paragraph one" in result
    assert "Paragraph two" in result


def test_preserves_order_by_score():
    builder = ContextBuilder()
    chunks = [
        {"content": "Best match.", "score": 0.95},
        {"content": "Second best.", "score": 0.8},
        {"content": "Third.", "score": 0.6},
    ]
    result = builder.build(chunks, max_tokens=1000)
    pos_best = result.find("Best match")
    pos_second = result.find("Second best")
    assert pos_best < pos_second
