from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_admin
from app.db.session import get_db
from app.domain.knowledge import KnowledgeIndexStatus
from app.integrations.hash_embedding import (
    HashEmbeddingProvider,
)
from app.repositories.knowledge import (
    KnowledgeRepository,
)
from app.repositories.knowledge_chunk import (
    KnowledgeChunkRepository,
)
from app.schemas.knowledge import (
    KnowledgeArticleCreate,
    KnowledgeArticleRead,
    KnowledgeArticleUpdate,
    KnowledgeIndexResponse,
)
from app.services.knowledge import (
    KnowledgeArticleNotFoundError,
    KnowledgeService,
)
from app.services.knowledge_index import (
    KnowledgeIndexService,
)
from app.services.knowledge_queue import (
    KnowledgeIndexDispatcher,
)

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base"],
    dependencies=[
        Depends(require_admin),
    ],
)


def get_knowledge_service(
    db: Session = Depends(get_db),
) -> KnowledgeService:
    repository = KnowledgeRepository(db)

    return KnowledgeService(repository)


def get_knowledge_index_service(
    db: Session = Depends(get_db),
) -> KnowledgeIndexService:
    return KnowledgeIndexService(
        article_repository=KnowledgeRepository(db),
        chunk_repository=KnowledgeChunkRepository(db),
        embedding_provider=HashEmbeddingProvider(),
    )


def get_knowledge_index_dispatcher() -> KnowledgeIndexDispatcher:
    return KnowledgeIndexDispatcher()


@router.post(
    "",
    response_model=KnowledgeArticleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_article(
    article_data: KnowledgeArticleCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
    dispatcher: KnowledgeIndexDispatcher = Depends(get_knowledge_index_dispatcher),
):
    article = service.create_article(article_data)

    dispatcher.enqueue(article.id)

    return article


@router.get(
    "",
    response_model=list[KnowledgeArticleRead],
)
def list_articles(
    service: KnowledgeService = Depends(get_knowledge_service),
):
    return service.list_articles()


@router.get(
    "/{article_id}",
    response_model=KnowledgeArticleRead,
)
def get_article(
    article_id: int,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    try:
        return service.get_article(article_id)

    except KnowledgeArticleNotFoundError:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=("Knowledge article not found"),
        )


@router.patch(
    "/{article_id}",
    response_model=KnowledgeArticleRead,
)
def update_article(
    article_id: int,
    article_data: KnowledgeArticleUpdate,
    service: KnowledgeService = Depends(get_knowledge_service),
    dispatcher: KnowledgeIndexDispatcher = Depends(get_knowledge_index_dispatcher),
):
    try:
        article = service.update_article(
            article_id=article_id,
            data=article_data,
        )

        if "content" in article_data.model_fields_set:
            dispatcher.enqueue(article.id)

        return article

    except KnowledgeArticleNotFoundError:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=("Knowledge article not found"),
        )


@router.post(
    "/{article_id}/reindex",
    response_model=KnowledgeIndexResponse,
)
def reindex_article(
    article_id: int,
    service: KnowledgeIndexService = Depends(get_knowledge_index_service),
):
    article = service.article_repository.get_by_id(article_id)

    if article is None:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=("Knowledge article not found"),
        )

    article.indexing_status = KnowledgeIndexStatus.indexing.value
    article.indexing_error = None
    article.indexed_at = None

    service.article_repository.save(article)

    try:
        chunks = service.rebuild_article_chunks(article_id)

    except Exception as exc:
        article.indexing_status = KnowledgeIndexStatus.failed.value
        article.indexing_error = str(exc)[:2000]
        article.indexed_at = None

        service.article_repository.save(article)

        raise

    article.indexing_status = KnowledgeIndexStatus.ready.value
    article.indexing_error = None
    article.indexed_at = datetime.now(timezone.utc)

    service.article_repository.save(article)

    return KnowledgeIndexResponse(
        article_id=article_id,
        chunks_indexed=len(chunks),
        embedding_model=(service.embedding_provider.model_name),
    )
