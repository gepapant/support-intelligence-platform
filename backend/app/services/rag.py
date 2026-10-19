from app.domain.reply import ReplyDecision
from app.domain.user import UserRole
from app.models.reply_suggestion import (
    TicketReplySuggestion,
)
from app.models.user import User
from app.repositories.reply_suggestion import (
    ReplySuggestionRepository,
)
from app.repositories.ticket import TicketRepository
from app.schemas.rag import (
    RAGSource,
    SuggestedReplyResponse,
)
from app.services.knowledge_search import (
    KnowledgeSearchService,
)
from app.services.reply_generation import (
    ReplyProvider,
)
from app.services.ticket import (
    TicketAccessDeniedError,
    TicketNotFoundError,
)


class RAGService:
    def __init__(
        self,
        ticket_repository: TicketRepository,
        search_service: KnowledgeSearchService,
        reply_provider: ReplyProvider,
        suggestion_repository: ReplySuggestionRepository,
    ):
        self.ticket_repository = ticket_repository
        self.search_service = search_service
        self.reply_provider = reply_provider
        self.suggestion_repository = suggestion_repository

    def suggest_reply(
        self,
        ticket_id: int,
        current_user: User,
    ) -> SuggestedReplyResponse:
        ticket = self.ticket_repository.get_by_id(ticket_id)

        if ticket is None:
            raise TicketNotFoundError

        is_admin = current_user.role == UserRole.admin

        is_assignee = ticket.assignee_id == current_user.id

        if not is_admin and not is_assignee:
            raise TicketAccessDeniedError

        query = f"{ticket.title}\n{ticket.description}"

        retrieved = self.search_service.search(
            query=query,
            limit=3,
        )

        reply = self.reply_provider.generate(
            ticket_title=ticket.title,
            ticket_description=ticket.description,
            context=retrieved,
        )

        sources = [
            RAGSource(
                article_id=item.article_id,
                article_title=item.article_title,
                source_url=item.source_url,
                similarity=item.similarity,
            )
            for item in retrieved
        ]

        suggestion = TicketReplySuggestion(
            ticket_id=ticket.id,
            created_by_id=current_user.id,
            generated_reply=reply,
            final_reply=None,
            decision=ReplyDecision.pending.value,
            provider=(self.reply_provider.provider_name),
            sources_snapshot=[
                source.model_dump(
                    mode="json",
                )
                for source in sources
            ],
        )

        stored_suggestion = self.suggestion_repository.add(suggestion)

        return SuggestedReplyResponse(
            suggestion_id=stored_suggestion.id,
            reply=reply,
            provider=(self.reply_provider.provider_name),
            sources=sources,
        )
