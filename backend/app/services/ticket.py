from app.domain.ticket import TicketStatus
from app.models.ticket import Ticket
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def create_ticket(self, ticket_data: TicketCreate) -> Ticket:
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            priority=ticket_data.priority,
            status=TicketStatus.open,
        )

        return self.repository.add(ticket)

    def list_tickets(self) -> list[Ticket]:
        return self.repository.get_all()

    def get_ticket(self, ticket_id: int) -> Ticket | None:
        return self.repository.get_by_id(ticket_id)

    def update_ticket(
        self,
        ticket_id: int,
        ticket_data: TicketUpdate,
    ) -> Ticket | None:
        ticket = self.repository.get_by_id(ticket_id)

        if ticket is None:
            return None

        updates = ticket_data.model_dump(exclude_unset=True)

        for field_name, value in updates.items():
            setattr(ticket, field_name, value)

        return self.repository.save(ticket)