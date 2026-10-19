from datetime import datetime, timezone

from app.domain.reply import ReplyDecision
from app.domain.user import UserRole
from app.models.user import User
from app.repositories.reply_suggestion import (
    ReplySuggestionRepository,
)
from app.repositories.ticket import TicketRepository
from app.schemas.rag import (
    ReplySuggestionReviewRequest,
    ReplySuggestionReviewResponse,
)
from app.services.ticket import (
    TicketAccessDeniedError,
)


class ReplySuggestionNotFoundError(Exception):
    pass


class ReplySuggestionAlreadyReviewedError(
    Exception
):
    pass


class ReplyReviewService:
    def __init__(
        self,
        suggestion_repository: ReplySuggestionRepository,
        ticket_repository: TicketRepository,
    ):
        self.suggestion_repository = (
            suggestion_repository
        )
        self.ticket_repository = (
            ticket_repository
        )

    def review(
        self,
        ticket_id: int,
        suggestion_id: int,
        current_user: User,
        review_data: ReplySuggestionReviewRequest,
    ) -> ReplySuggestionReviewResponse:
        suggestion = (
            self.suggestion_repository.get_by_id(
                suggestion_id
            )
        )

        if (
            suggestion is None
            or suggestion.ticket_id != ticket_id
        ):
            raise ReplySuggestionNotFoundError

        ticket = self.ticket_repository.get_by_id(
            ticket_id
        )

        if ticket is None:
            raise ReplySuggestionNotFoundError

        is_admin = (
            current_user.role == UserRole.admin
        )

        is_assignee = (
            ticket.assignee_id
            == current_user.id
        )

        if not is_admin and not is_assignee:
            raise TicketAccessDeniedError

        if (
            suggestion.decision
            != ReplyDecision.pending.value
        ):
            raise (
                ReplySuggestionAlreadyReviewedError
            )

        if (
            review_data.decision
            == ReplyDecision.accepted
        ):
            suggestion.final_reply = (
                suggestion.generated_reply
            )

        elif (
            review_data.decision
            == ReplyDecision.edited
        ):
            suggestion.final_reply = (
                review_data.final_reply
            )

        else:
            suggestion.final_reply = None

        suggestion.decision = (
            review_data.decision.value
        )

        suggestion.reviewed_by_id = (
            current_user.id
        )

        suggestion.reviewed_at = datetime.now(
            timezone.utc
        )

        stored = (
            self.suggestion_repository.save(
                suggestion
            )
        )

        return ReplySuggestionReviewResponse(
            suggestion_id=stored.id,
            decision=ReplyDecision(
                stored.decision
            ),
            final_reply=stored.final_reply,
            reviewed_at=stored.reviewed_at,
        )