from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedKnowledgeChunk:
    chunk_id: int
    article_id: int
    chunk_index: int
    content: str
    article_title: str
    source_url: str | None
    similarity: float
