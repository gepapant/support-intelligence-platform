from app.domain.ticket import TicketStatus
from app.models.ticket import Ticket
from app.repositories.ticket import TicketRepository
from app.repositories.user import UserRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketNotFoundError(Exception):
    pass


class AssigneeNotFoundError(Exception):
    pass


class InactiveAssigneeError(Exception):
    pass


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        user_repository: UserRepository,
    ):
        self.repository = repository
        self.user_repository = user_repository

    def create_ticket(
        self,
        ticket_data: TicketCreate,
    ) -> Ticket:
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            priority=ticket_data.priority,
            status=TicketStatus.open,
        )

        return self.repository.add(ticket)

    def list_tickets(self) -> list[Ticket]:
        return self.repository.get_all()

    def get_ticket(
        self,
        ticket_id: int,
    ) -> Ticket | None:
        return self.repository.get_by_id(
            ticket_id
        )

    def update_ticket(
        self,
        ticket_id: int,
        ticket_data: TicketUpdate,
    ) -> Ticket | None:
        ticket = self.repository.get_by_id(
            ticket_id
        )

        if ticket is None:
            return None

        updates = ticket_data.model_dump(
            exclude_unset=True
        )

        for field_name, value in updates.items():
            setattr(
                ticket,
                field_name,
                value,
            )

        return self.repository.save(ticket)

    def list_assigned_tickets(
        self,
        user_id: int,
    ) -> list[Ticket]:
        return self.repository.get_by_assignee_id(
            user_id
        )

    def assign_ticket(
        self,
        ticket_id: int,
        assignee_id: int | None,
    ) -> Ticket:
        ticket = self.repository.get_by_id(
            ticket_id
        )

        if ticket is None:
            raise TicketNotFoundError

        if assignee_id is None:
            ticket.assignee_id = None

            return self.repository.save(
                ticket
            )

        user = self.user_repository.get_by_id(
            assignee_id
        )

        if user is None:
            raise AssigneeNotFoundError

        if not user.is_active:
            raise InactiveAssigneeError

        ticket.assignee_id = user.id

        return self.repository.save(ticket)