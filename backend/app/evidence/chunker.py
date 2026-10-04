"""Evidence document chunker for semantic retrieval."""

from typing import Any, Dict, List
from app.utils.text import clean_text


class DocumentChunker:
    """Splits normalized text into overlapping chunks for granular search."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        cleaned = clean_text(text)
        if not cleaned:
            return []

        paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_index = 0

        for para in paragraphs:
            # If a single paragraph is larger than chunk_size, split by sentences or lines
            if len(para) > self.chunk_size:
                lines = para.split("\n")
                for line in lines:
                    if current_length + len(line) > self.chunk_size and current_chunk:
                        chunk_text = " ".join(current_chunk).strip()
                        chunks.append(self._create_chunk_dict(chunk_index, chunk_text, base_metadata))
                        chunk_index += 1
                        # Retain overlap from end of current_chunk
                        current_chunk = [current_chunk[-1]] if current_chunk else []
                        current_length = sum(len(x) for x in current_chunk)

                    current_chunk.append(line)
                    current_length += len(line)
            else:
                if current_length + len(para) > self.chunk_size and current_chunk:
                    chunk_text = "\n\n".join(current_chunk).strip()
                    chunks.append(self._create_chunk_dict(chunk_index, chunk_text, base_metadata))
                    chunk_index += 1
                    current_chunk = [current_chunk[-1]] if current_chunk else []
                    current_length = sum(len(x) for x in current_chunk)

                current_chunk.append(para)
                current_length += len(para)

        if current_chunk:
            chunk_text = "\n\n".join(current_chunk).strip()
            chunks.append(self._create_chunk_dict(chunk_index, chunk_text, base_metadata))

        return chunks

    def _create_chunk_dict(self, index: int, content: str, base_meta: Dict[str, Any] = None) -> Dict[str, Any]:
        meta = dict(base_meta or {})
        meta["char_length"] = len(content)
        return {
            "chunk_index": index,
            "content": content,
            "metadata_json": meta,
        }
