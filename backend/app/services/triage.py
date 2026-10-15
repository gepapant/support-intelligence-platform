from datetime import datetime, timezone
from typing import Protocol

from app.domain.user import UserRole
from app.models.ticket import Ticket
from app.models.user import User
from app.repositories.ticket import TicketRepository
from app.schemas.triage import TicketTriageResult
from app.services.ticket import (
    TicketAccessDeniedError,
    TicketNotFoundError,
)


class TriageProvider(Protocol):
    model_name: str

    def analyze(
        self,
        title: str,
        description: str,
    ) -> TicketTriageResult: ...


class TicketTriageService:
    def __init__(
        self,
        repository: TicketRepository,
        provider: TriageProvider,
    ):
        self.repository = repository
        self.provider = provider

    def analyze_ticket(
        self,
        ticket_id: int,
        current_user: User,
    ) -> Ticket:
        ticket = self.repository.get_by_id(ticket_id)

        if ticket is None:
            raise TicketNotFoundError

        is_admin = current_user.role == UserRole.admin
        is_assignee = ticket.assignee_id == current_user.id

        if not is_admin and not is_assignee:
            raise TicketAccessDeniedError

        result = self.provider.analyze(
            title=ticket.title,
            description=ticket.description,
        )

        ticket.ai_category = result.category.value
        ticket.ai_sentiment = result.sentiment.value
        ticket.ai_suggested_priority = result.suggested_priority.value
        ticket.ai_summary = result.summary
        ticket.ai_model = self.provider.model_name
        ticket.ai_analyzed_at = datetime.now(timezone.utc)

        return self.repository.save(ticket)
