from sqlalchemy.orm import Session

from app.models.reply_suggestion import (
    TicketReplySuggestion,
)


class ReplySuggestionRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def add(
        self,
        suggestion: TicketReplySuggestion,
    ) -> TicketReplySuggestion:
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(suggestion)

        return suggestion

    def get_by_id(
        self,
        suggestion_id: int,
    ) -> TicketReplySuggestion | None:
        return self.db.get(
            TicketReplySuggestion,
            suggestion_id,
        )

    def save(
        self,
        suggestion: TicketReplySuggestion,
    ) -> TicketReplySuggestion:
        self.db.commit()
        self.db.refresh(suggestion)

        return suggestion