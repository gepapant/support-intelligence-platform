from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.ticket import TicketPriority, TicketStatus
from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_all(
        self,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        assignee_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Ticket]:
        statement = select(Ticket)

        if status is not None:
            statement = statement.where(Ticket.status == status)

        if priority is not None:
            statement = statement.where(Ticket.priority == priority)

        if assignee_id is not None:
            statement = statement.where(Ticket.assignee_id == assignee_id)

        statement = statement.order_by(Ticket.id).offset(offset).limit(limit)

        return list(self.db.scalars(statement).all())

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)

    def save(self, ticket: Ticket) -> Ticket:
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_by_assignee_id(
        self,
        user_id: int,
    ) -> list[Ticket]:
        statement = (
            select(Ticket).where(Ticket.assignee_id == user_id).order_by(Ticket.id)
        )

        return list(self.db.scalars(statement).all())
