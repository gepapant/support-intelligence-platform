from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_admin
from app.db.session import get_db
from app.repositories.knowledge import (
    KnowledgeRepository,
)
from app.schemas.knowledge import (
    KnowledgeArticleCreate,
    KnowledgeArticleRead,
    KnowledgeArticleUpdate,
)
from app.services.knowledge import (
    KnowledgeArticleNotFoundError,
    KnowledgeService,
)
from app.services.knowledge_queue import (
    KnowledgeIndexDispatcher,
    KnowledgeIndexDispatchError,
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

    try:
        dispatcher.enqueue(article.id)

    except KnowledgeIndexDispatchError as exc:
        article = service.mark_indexing_failed(
            article.id,
            str(exc),
        )

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
            try:
                dispatcher.enqueue(article.id)

            except KnowledgeIndexDispatchError as exc:
                article = service.mark_indexing_failed(
                    article.id,
                    str(exc),
                )

        return article

    except KnowledgeArticleNotFoundError:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=("Knowledge article not found"),
        )


@router.post(
    "/{article_id}/reindex",
    response_model=KnowledgeArticleRead,
)
def reindex_article(
    article_id: int,
    service: KnowledgeService = Depends(get_knowledge_service),
    dispatcher: KnowledgeIndexDispatcher = Depends(get_knowledge_index_dispatcher),
):
    try:
        article = service.mark_indexing_queued(article_id)

        try:
            dispatcher.enqueue(article.id)

        except KnowledgeIndexDispatchError as exc:
            service.mark_indexing_failed(
                article.id,
                str(exc),
            )

            raise HTTPException(
                status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
                detail=str(exc),
            )

        return article

    except KnowledgeArticleNotFoundError:
        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail=("Knowledge article not found"),
        )
