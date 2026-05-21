from typing import List


def recursive_chunk(text: str, chunk_size: int = 400, chunk_overlap: int = 50) -> List[str]:
    """Split text recursively using separator priority."""
    if not text.strip():
        return []

    separators = ["\n\n", "\n", ". ", " ", ""]

    if len(text) <= chunk_size:
        return [text]

    for separator in separators:
        if separator == "":
            chunks = _split_by_size(text, chunk_size, chunk_overlap)
        else:
            chunks = _split_by_separator(text, separator, chunk_size, chunk_overlap)

        if len(chunks) > 1 or separator == "":
            return chunks

    return [text]


def _split_by_separator(text: str, separator: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    splits = text.split(separator)
    chunks = []
    current = ""

    for split in splits:
        candidate = current + (separator if current else "") + split
        if len(candidate) > chunk_size and current:
            chunks.append(current)
            current = split
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def _split_by_size(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks


def semantic_chunk(text: str, max_sentences: int = 5) -> List[str]:
    """Chunk text by sentence boundaries with a max sentence count per chunk."""
    if not text.strip():
        return []

    sentences = _split_sentences(text)
    chunks = []

    for i in range(0, len(sentences), max_sentences):
        chunk_sentences = sentences[i:i + max_sentences]
        chunks.append(". ".join(chunk_sentences) + ("." if chunk_sentences else ""))

    return chunks


def _split_sentences(text: str) -> List[str]:
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]
