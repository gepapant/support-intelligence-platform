from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.domain.retrieval import (
    RetrievedKnowledgeChunk,
)
from app.models.knowledge import KnowledgeArticle
from app.models.knowledge_chunk import KnowledgeChunk


class KnowledgeChunkRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def replace_for_article(
        self,
        article_id: int,
        chunks: list[KnowledgeChunk],
    ) -> list[KnowledgeChunk]:
        statement = delete(KnowledgeChunk).where(
            KnowledgeChunk.article_id == article_id
        )

        self.db.execute(statement)

        self.db.add_all(chunks)
        self.db.commit()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks

    def get_by_article(
        self,
        article_id: int,
    ) -> list[KnowledgeChunk]:
        statement = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.article_id == article_id)
            .order_by(KnowledgeChunk.chunk_index)
        )

        return list(self.db.scalars(statement).all())

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 3,
    ) -> list[RetrievedKnowledgeChunk]:
        distance = KnowledgeChunk.embedding.cosine_distance(query_embedding).label(
            "distance"
        )

        statement = (
            select(
                KnowledgeChunk.id,
                KnowledgeChunk.article_id,
                KnowledgeChunk.chunk_index,
                KnowledgeChunk.content,
                KnowledgeArticle.title,
                KnowledgeArticle.source_url,
                distance,
            )
            .join(
                KnowledgeArticle,
                KnowledgeArticle.id == KnowledgeChunk.article_id,
            )
            .where(
                KnowledgeArticle.is_active.is_(True),
                KnowledgeChunk.embedding.is_not(None),
            )
            .order_by(distance)
            .limit(limit)
        )

        rows = self.db.execute(statement).all()

        return [
            RetrievedKnowledgeChunk(
                chunk_id=row.id,
                article_id=row.article_id,
                chunk_index=row.chunk_index,
                content=row.content,
                article_title=row.title,
                source_url=row.source_url,
                similarity=(1.0 - float(row.distance)),
            )
            for row in rows
        ]
