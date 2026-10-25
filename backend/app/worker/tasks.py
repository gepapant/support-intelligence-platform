from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.domain.knowledge import (
    KnowledgeIndexStatus,
)
from app.integrations.hash_embedding import (
    HashEmbeddingProvider,
)
from app.repositories.knowledge import (
    KnowledgeRepository,
)
from app.repositories.knowledge_chunk import (
    KnowledgeChunkRepository,
)
from app.services.knowledge import (
    KnowledgeArticleNotFoundError,
)
from app.services.knowledge_index import (
    KnowledgeIndexService,
)
from app.worker.celery_app import celery_app


def mark_knowledge_index_queued(
    article_id: int,
) -> None:
    db = SessionLocal()

    try:
        repository = KnowledgeRepository(db)

        article = repository.get_by_id(article_id)

        if article is None:
            raise KnowledgeArticleNotFoundError

        article.indexing_status = KnowledgeIndexStatus.queued.value
        article.indexing_error = None
        article.indexed_at = None

        repository.save(article)

    finally:
        db.close()


def mark_knowledge_index_failed(
    article_id: int,
    error: Exception,
) -> None:
    db = SessionLocal()

    try:
        repository = KnowledgeRepository(db)

        article = repository.get_by_id(article_id)

        if article is None:
            raise KnowledgeArticleNotFoundError

        article.indexing_status = KnowledgeIndexStatus.failed.value

        article.indexing_error = str(error)[:2000]

        article.indexed_at = None

        repository.save(article)

    finally:
        db.close()


def index_knowledge_article_now(
    article_id: int,
) -> dict[str, int | str]:
    db = SessionLocal()

    try:
        article_repository = KnowledgeRepository(db)

        article = article_repository.get_by_id(article_id)

        if article is None:
            raise KnowledgeArticleNotFoundError

        article.indexing_status = KnowledgeIndexStatus.indexing.value
        article.indexing_error = None
        article.indexed_at = None

        article_repository.save(article)

        embedding_provider = HashEmbeddingProvider()

        service = KnowledgeIndexService(
            article_repository=(article_repository),
            chunk_repository=(KnowledgeChunkRepository(db)),
            embedding_provider=(embedding_provider),
        )

        chunks = service.rebuild_article_chunks(article_id)

        article.indexing_status = KnowledgeIndexStatus.ready.value
        article.indexing_error = None
        article.indexed_at = datetime.now(timezone.utc)

        article_repository.save(article)

        return {
            "article_id": article_id,
            "chunks_indexed": len(chunks),
            "embedding_model": (embedding_provider.model_name),
        }

    finally:
        db.close()


@celery_app.task(
    name="worker.ping",
)
def ping() -> str:
    return "pong"


@celery_app.task(
    bind=True,
    name="knowledge.index_article",
    max_retries=3,
)
def index_knowledge_article(
    self,
    article_id: int,
) -> dict[str, int | str]:
    try:
        return index_knowledge_article_now(article_id)

    except KnowledgeArticleNotFoundError:
        raise

    except Exception as exc:
        if self.request.retries >= self.max_retries:
            mark_knowledge_index_failed(
                article_id,
                exc,
            )
            raise

        mark_knowledge_index_queued(article_id)

        raise self.retry(
            exc=exc,
            countdown=5,
        )
