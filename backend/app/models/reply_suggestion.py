from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.reply import ReplyDecision


class TicketReplySuggestion(Base):
    __tablename__ = "ticket_reply_suggestions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tickets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    generated_reply: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    final_reply: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decision: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ReplyDecision.pending.value,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    sources_snapshot: Mapped[list[dict[str, object]]] = mapped_column(
        JSON,
        nullable=False,
    )

    reviewed_by_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
