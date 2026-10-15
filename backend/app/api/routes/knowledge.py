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


@router.post(
    "",
    response_model=KnowledgeArticleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_article(
    article_data: KnowledgeArticleCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    return service.create_article(article_data)


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
):
    try:
        return service.update_article(
            article_id=article_id,
            data=article_data,
        )

    except KnowledgeArticleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge article not found",
        )
