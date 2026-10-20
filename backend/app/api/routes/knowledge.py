from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_admin
from app.db.session import get_db
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


@router.post(
    "",
    response_model=KnowledgeArticleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_article(
    article_data: KnowledgeArticleCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
    index_service: KnowledgeIndexService = Depends(get_knowledge_index_service),
):
    article = service.create_article(article_data)

    index_service.rebuild_article_chunks(article.id)

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge article not found",
        )


@router.patch(
    "/{article_id}",
    response_model=KnowledgeArticleRead,
)
def update_article(
    article_id: int,
    article_data: KnowledgeArticleUpdate,
    service: KnowledgeService = Depends(get_knowledge_service),
    index_service: KnowledgeIndexService = Depends(get_knowledge_index_service),
):
    try:
        article = service.update_article(
            article_id=article_id,
            data=article_data,
        )

        if "content" in article_data.model_fields_set:
            index_service.rebuild_article_chunks(article.id)

        return article

    except KnowledgeArticleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge article not found",
        )


@router.post(
    "/{article_id}/reindex",
    response_model=KnowledgeIndexResponse,
)
def reindex_article(
    article_id: int,
    service: KnowledgeIndexService = Depends(get_knowledge_index_service),
):
    try:
        chunks = service.rebuild_article_chunks(article_id)

        return KnowledgeIndexResponse(
            article_id=article_id,
            chunks_indexed=len(chunks),
            embedding_model=(service.embedding_provider.model_name),
        )

    except KnowledgeArticleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge article not found",
        )
