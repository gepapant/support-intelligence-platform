from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def get_all(self) -> list[Ticket]:
        statement = select(Ticket).order_by(Ticket.id)

        return list(self.db.scalars(statement).all())

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.db.get(Ticket, ticket_id)