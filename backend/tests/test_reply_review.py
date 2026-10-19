from types import SimpleNamespace

from app.domain.reply import ReplyDecision
from app.domain.user import UserRole
from app.schemas.rag import ReplySuggestionReviewRequest
from app.services.reply_review import (
    ReplyReviewService,
    ReplySuggestionAlreadyReviewedError,
    ReplySuggestionNotFoundError,
)
from app.services.ticket import TicketAccessDeniedError


class FakeReplySuggestionRepository:
    def __init__(self, suggestion):
        self.suggestion = suggestion

    def get_by_id(self, suggestion_id: int):
        if self.suggestion is None or self.suggestion.id != suggestion_id:
            return None

        return self.suggestion

    def save(self, suggestion):
        self.suggestion = suggestion
        return suggestion


class FakeTicketRepository:
    def __init__(self, ticket):
        self.ticket = ticket

    def get_by_id(self, ticket_id: int):
        if self.ticket is None or self.ticket.id != ticket_id:
            return None

        return self.ticket


def make_ticket(
    assignee_id: int | None = None,
):
    return SimpleNamespace(
        id=1,
        assignee_id=assignee_id,
    )


def make_suggestion(
    decision: str = "pending",
):
    return SimpleNamespace(
        id=10,
        ticket_id=1,
        generated_reply="Generated reply",
        final_reply=None,
        decision=decision,
        reviewed_by_id=None,
        reviewed_at=None,
    )


def make_user(
    user_id: int,
    role: UserRole,
):
    return SimpleNamespace(
        id=user_id,
        role=role,
    )


def make_service(
    suggestion=None,
    ticket=None,
):
    return ReplyReviewService(
        suggestion_repository=(FakeReplySuggestionRepository(suggestion)),
        ticket_repository=(FakeTicketRepository(ticket)),
    )


def test_admin_can_accept_suggestion():
    service = make_service(
        suggestion=make_suggestion(),
        ticket=make_ticket(),
    )

    result = service.review(
        ticket_id=1,
        suggestion_id=10,
        current_user=make_user(
            user_id=100,
            role=UserRole.admin,
        ),
        review_data=(
            ReplySuggestionReviewRequest(
                decision=ReplyDecision.accepted,
            )
        ),
    )

    assert result.decision == ReplyDecision.accepted
    assert result.final_reply == "Generated reply"
    assert result.reviewed_at is not None


def test_assigned_agent_can_edit_suggestion():
    service = make_service(
        suggestion=make_suggestion(),
        ticket=make_ticket(assignee_id=7),
    )

    result = service.review(
        ticket_id=1,
        suggestion_id=10,
        current_user=make_user(
            user_id=7,
            role=UserRole.agent,
        ),
        review_data=(
            ReplySuggestionReviewRequest(
                decision=ReplyDecision.edited,
                final_reply=("Edited final reply"),
            )
        ),
    )

    assert result.decision == ReplyDecision.edited
    assert result.final_reply == "Edited final reply"


def test_assigned_agent_can_reject_suggestion():
    service = make_service(
        suggestion=make_suggestion(),
        ticket=make_ticket(assignee_id=7),
    )

    result = service.review(
        ticket_id=1,
        suggestion_id=10,
        current_user=make_user(
            user_id=7,
            role=UserRole.agent,
        ),
        review_data=(
            ReplySuggestionReviewRequest(
                decision=ReplyDecision.rejected,
            )
        ),
    )

    assert result.decision == ReplyDecision.rejected
    assert result.final_reply is None


def test_unassigned_agent_cannot_review():
    service = make_service(
        suggestion=make_suggestion(),
        ticket=make_ticket(assignee_id=7),
    )

    try:
        service.review(
            ticket_id=1,
            suggestion_id=10,
            current_user=make_user(
                user_id=8,
                role=UserRole.agent,
            ),
            review_data=(
                ReplySuggestionReviewRequest(
                    decision=(ReplyDecision.accepted),
                )
            ),
        )

    except TicketAccessDeniedError:
        pass

    else:
        raise AssertionError("Expected TicketAccessDeniedError")


def test_missing_suggestion_raises_not_found():
    service = make_service(
        suggestion=None,
        ticket=make_ticket(),
    )

    try:
        service.review(
            ticket_id=1,
            suggestion_id=999,
            current_user=make_user(
                user_id=1,
                role=UserRole.admin,
            ),
            review_data=(
                ReplySuggestionReviewRequest(
                    decision=(ReplyDecision.accepted),
                )
            ),
        )

    except ReplySuggestionNotFoundError:
        pass

    else:
        raise AssertionError("Expected ReplySuggestionNotFoundError")


def test_already_reviewed_suggestion_conflicts():
    service = make_service(
        suggestion=make_suggestion(decision="accepted"),
        ticket=make_ticket(),
    )

    try:
        service.review(
            ticket_id=1,
            suggestion_id=10,
            current_user=make_user(
                user_id=1,
                role=UserRole.admin,
            ),
            review_data=(
                ReplySuggestionReviewRequest(
                    decision=(ReplyDecision.rejected),
                )
            ),
        )

    except ReplySuggestionAlreadyReviewedError:
        pass

    else:
        raise AssertionError("Expected ReplySuggestionAlreadyReviewedError")
