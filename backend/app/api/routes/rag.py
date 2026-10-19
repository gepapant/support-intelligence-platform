from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.integrations.hash_embedding import HashEmbeddingProvider
from app.integrations.template_reply import TemplateReplyProvider
from app.models.user import User
from app.repositories.knowledge_chunk import KnowledgeChunkRepository
from app.repositories.reply_suggestion import ReplySuggestionRepository
from app.repositories.ticket import TicketRepository
from app.schemas.rag import (
    ReplySuggestionReviewRequest,
    ReplySuggestionReviewResponse,
    SuggestedReplyResponse,
)
from app.services.knowledge_search import KnowledgeSearchService
from app.services.rag import RAGService
from app.services.reply_review import (
    ReplyReviewService,
    ReplySuggestionAlreadyReviewedError,
    ReplySuggestionNotFoundError,
)
from app.services.ticket import (
    TicketAccessDeniedError,
    TicketNotFoundError,
)

router = APIRouter(
    prefix="/tickets",
    tags=["RAG"],
)


def get_rag_service(
    db: Session = Depends(get_db),
) -> RAGService:
    chunk_repository = KnowledgeChunkRepository(db)
    ticket_repository = TicketRepository(db)
    suggestion_repository = ReplySuggestionRepository(db)

    embedding_provider = HashEmbeddingProvider()

    search_service = KnowledgeSearchService(
        repository=chunk_repository,
        embedding_provider=embedding_provider,
    )

    reply_provider = TemplateReplyProvider()

    return RAGService(
        ticket_repository=ticket_repository,
        search_service=search_service,
        reply_provider=reply_provider,
        suggestion_repository=suggestion_repository,
    )


def get_reply_review_service(
    db: Session = Depends(get_db),
) -> ReplyReviewService:
    return ReplyReviewService(
        suggestion_repository=ReplySuggestionRepository(db),
        ticket_repository=TicketRepository(db),
    )


@router.post(
    "/{ticket_id}/suggested-reply",
    response_model=SuggestedReplyResponse,
)
def suggest_reply(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    service: RAGService = Depends(get_rag_service),
):
    try:
        return service.suggest_reply(
            ticket_id=ticket_id,
            current_user=current_user,
        )

    except TicketNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    except TicketAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("You cannot generate a reply for this ticket"),
        )


@router.patch(
    "/{ticket_id}/suggested-replies/{suggestion_id}",
    response_model=ReplySuggestionReviewResponse,
)
def review_suggested_reply(
    ticket_id: int,
    suggestion_id: int,
    review_data: ReplySuggestionReviewRequest,
    current_user: User = Depends(get_current_user),
    service: ReplyReviewService = Depends(get_reply_review_service),
):
    try:
        return service.review(
            ticket_id=ticket_id,
            suggestion_id=suggestion_id,
            current_user=current_user,
            review_data=review_data,
        )

    except ReplySuggestionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply suggestion not found",
        )

    except TicketAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=("You cannot review this suggested reply"),
        )

    except ReplySuggestionAlreadyReviewedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("Reply suggestion has already been reviewed"),
        )
