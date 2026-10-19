from types import SimpleNamespace

from app.domain.retrieval import RetrievedKnowledgeChunk
from app.domain.user import UserRole
from app.services.rag import RAGService
from app.services.ticket import (
    TicketAccessDeniedError,
    TicketNotFoundError,
)


class FakeTicketRepository:
    def __init__(self, ticket):
        self.ticket = ticket

    def get_by_id(self, ticket_id: int):
        if self.ticket is None or self.ticket.id != ticket_id:
            return None

        return self.ticket


class FakeKnowledgeSearchService:
    def __init__(self):
        self.query = None
        self.limit = None

    def search(
        self,
        query: str,
        limit: int = 3,
    ):
        self.query = query
        self.limit = limit

        return [
            RetrievedKnowledgeChunk(
                chunk_id=1,
                article_id=10,
                chunk_index=0,
                content=("Duplicate charges should be refunded."),
                article_title=("Duplicate charge policy"),
                source_url=("https://example.com/refunds"),
                similarity=0.9,
            )
        ]


class FakeReplyProvider:
    provider_name = "fake-rag-provider"

    def generate(
        self,
        ticket_title: str,
        ticket_description: str,
        context,
    ) -> str:
        return "Suggested support reply."


class FakeReplySuggestionRepository:
    def __init__(self):
        self.saved_suggestion = None

    def add(self, suggestion):
        suggestion.id = 123
        self.saved_suggestion = suggestion

        return suggestion


def make_ticket(
    assignee_id: int | None = None,
):
    return SimpleNamespace(
        id=1,
        title="Charged twice",
        description=("I was charged twice for my purchase."),
        assignee_id=assignee_id,
    )


def make_user(
    user_id: int,
    role: UserRole,
):
    return SimpleNamespace(
        id=user_id,
        role=role,
    )


def make_service(ticket):
    return RAGService(
        ticket_repository=(FakeTicketRepository(ticket)),
        search_service=(FakeKnowledgeSearchService()),
        reply_provider=FakeReplyProvider(),
        suggestion_repository=(FakeReplySuggestionRepository()),
    )


def test_admin_can_generate_suggested_reply():
    service = make_service(make_ticket())

    result = service.suggest_reply(
        ticket_id=1,
        current_user=make_user(
            user_id=100,
            role=UserRole.admin,
        ),
    )

    assert result.suggestion_id == 123

    assert result.reply == "Suggested support reply."

    assert result.provider == "fake-rag-provider"

    assert len(result.sources) == 1

    assert result.sources[0].article_title == "Duplicate charge policy"


def test_assigned_agent_can_generate_reply():
    service = make_service(make_ticket(assignee_id=7))

    result = service.suggest_reply(
        ticket_id=1,
        current_user=make_user(
            user_id=7,
            role=UserRole.agent,
        ),
    )

    assert result.suggestion_id == 123

    assert result.reply == "Suggested support reply."


def test_unassigned_agent_cannot_generate_reply():
    service = make_service(make_ticket(assignee_id=7))

    try:
        service.suggest_reply(
            ticket_id=1,
            current_user=make_user(
                user_id=8,
                role=UserRole.agent,
            ),
        )

    except TicketAccessDeniedError:
        pass

    else:
        raise AssertionError("Expected TicketAccessDeniedError")


def test_missing_ticket_raises_not_found():
    service = make_service(None)

    try:
        service.suggest_reply(
            ticket_id=999,
            current_user=make_user(
                user_id=1,
                role=UserRole.admin,
            ),
        )

    except TicketNotFoundError:
        pass

    else:
        raise AssertionError("Expected TicketNotFoundError")
