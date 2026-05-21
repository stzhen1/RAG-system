from typing import List, Dict, Any


class ContextBuilder:
    def build(self, chunks: List[Dict[str, Any]], max_tokens: int = 8000) -> str:
        if not chunks:
            return ""

        seen_hashes = set()
        deduped = []
        for chunk in chunks:
            content_hash = hash(chunk["content"])
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                deduped.append(chunk)

        deduped.sort(key=lambda c: c.get("score", 0), reverse=True)

        merged = self._merge_adjacent(deduped)

        separator = "\n\n---\n\n"
        context = ""
        for chunk in merged:
            addition = separator + chunk["content"] if context else chunk["content"]
            if self._estimate_tokens(context + addition) > max_tokens:
                break
            context += addition

        return context

    def _merge_adjacent(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not all("chunk_index" in c for c in chunks):
            return chunks

        chunks.sort(key=lambda c: (c.get("chunk_index", 0), -c.get("score", 0)))
        merged = []
        current_group = [chunks[0]]

        for i in range(1, len(chunks)):
            prev_idx = current_group[-1].get("chunk_index", -1)
            curr_idx = chunks[i].get("chunk_index", -1)
            if curr_idx == prev_idx + 1:
                current_group.append(chunks[i])
            else:
                merged.append(self._flatten_group(current_group))
                current_group = [chunks[i]]

        merged.append(self._flatten_group(current_group))
        merged.sort(key=lambda c: max(
            g.get("score", 0) for g in ([c] if isinstance(c, dict) else c)
        ), reverse=True)
        return merged

    def _flatten_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(group) == 1:
            return group[0]
        content = " ".join(g["content"] for g in group)
        score = max(g.get("score", 0) for g in group)
        return {"content": content, "score": score}

    def _estimate_tokens(self, text: str) -> int:
        words = text.split()
        return int(len(words) / 0.75)
