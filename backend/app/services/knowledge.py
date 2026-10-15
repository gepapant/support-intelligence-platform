from app.models.knowledge import KnowledgeArticle
from app.repositories.knowledge import (
    KnowledgeRepository,
)
from app.schemas.knowledge import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
)


class KnowledgeArticleNotFoundError(Exception):
    pass


class KnowledgeService:
    def __init__(
        self,
        repository: KnowledgeRepository,
    ):
        self.repository = repository

    def create_article(
        self,
        data: KnowledgeArticleCreate,
    ) -> KnowledgeArticle:
        article = KnowledgeArticle(
            title=data.title,
            content=data.content,
            source_url=(str(data.source_url) if data.source_url else None),
        )

        return self.repository.add(article)

    def list_articles(
        self,
    ) -> list[KnowledgeArticle]:
        return self.repository.get_all()

    def get_article(
        self,
        article_id: int,
    ) -> KnowledgeArticle:
        article = self.repository.get_by_id(article_id)

        if article is None:
            raise KnowledgeArticleNotFoundError

        return article

    def update_article(
        self,
        article_id: int,
        data: KnowledgeArticleUpdate,
    ) -> KnowledgeArticle:
        article = self.get_article(article_id)

        updates = data.model_dump(
            exclude_unset=True,
        )

        if "source_url" in updates:
            updates["source_url"] = (
                str(updates["source_url"]) if updates["source_url"] else None
            )

        for field_name, value in updates.items():
            setattr(
                article,
                field_name,
                value,
            )

        return self.repository.save(article)
