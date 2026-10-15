from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeArticle


class KnowledgeRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def add(
        self,
        article: KnowledgeArticle,
    ) -> KnowledgeArticle:
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)

        return article

    def get_by_id(
        self,
        article_id: int,
    ) -> KnowledgeArticle | None:
        return self.db.get(
            KnowledgeArticle,
            article_id,
        )

    def get_all(
        self,
    ) -> list[KnowledgeArticle]:
        statement = select(
            KnowledgeArticle,
        ).order_by(
            KnowledgeArticle.id,
        )

        return list(self.db.scalars(statement).all())

    def save(
        self,
        article: KnowledgeArticle,
    ) -> KnowledgeArticle:
        self.db.commit()
        self.db.refresh(article)

        return article
