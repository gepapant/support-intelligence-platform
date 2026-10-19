from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.embedding import EMBEDDING_DIMENSIONS


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "chunk_index",
            name="uq_knowledge_chunks_article_index",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey(
            "knowledge_articles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS),
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
