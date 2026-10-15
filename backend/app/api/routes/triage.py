from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.config import ai_settings
from app.db.session import get_db
from app.integrations.openai_triage import (
    OpenAITriageProvider,
    TriageProviderError,
)
from app.integrations.rule_based_triage import (
    RuleBasedTriageProvider,
)
from app.models.user import User
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketRead
from app.services.ticket import (
    TicketAccessDeniedError,
    TicketNotFoundError,
)
from app.services.triage import (
    TicketTriageService,
    TriageProvider,
)

router = APIRouter(
    prefix="/tickets",
    tags=["AI Triage"],
)


def get_triage_provider() -> TriageProvider:
    if ai_settings.provider == "rule_based":
        return RuleBasedTriageProvider()

    if ai_settings.provider == "openai":
        if ai_settings.api_key is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI triage is not configured",
            )

        return OpenAITriageProvider(
            api_key=ai_settings.api_key.get_secret_value(),
            model=ai_settings.model,
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Unknown AI triage provider",
    )


def get_triage_service(
    db: Session = Depends(get_db),
    provider: TriageProvider = Depends(get_triage_provider),
) -> TicketTriageService:
    repository = TicketRepository(db)

    return TicketTriageService(
        repository=repository,
        provider=provider,
    )


@router.post(
    "/{ticket_id}/triage",
    response_model=TicketRead,
)
def triage_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    service: TicketTriageService = Depends(get_triage_service),
):
    try:
        return service.analyze_ticket(
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
            detail="You cannot analyze this ticket",
        )

    except TriageProviderError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI triage provider failed",
        )
