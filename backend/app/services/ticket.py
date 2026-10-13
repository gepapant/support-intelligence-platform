from app.domain.ticket import TicketPriority, TicketStatus
from app.domain.user import UserRole
from app.models.ticket import Ticket
from app.models.user import User
from app.repositories.ticket import TicketRepository
from app.repositories.user import UserRepository
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketNotFoundError(Exception):
    pass


class AssigneeNotFoundError(Exception):
    pass


class InactiveAssigneeError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


class TicketAccessDeniedError(Exception):
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

    def list_tickets(
        self,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        assignee_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Ticket]:
        return self.repository.get_all(
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            limit=limit,
            offset=offset,
        )

    def get_ticket(
        self,
        ticket_id: int,
    ) -> Ticket | None:
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
        return self.repository.get_by_assignee_id(user_id)

    def assign_ticket(
        self,
        ticket_id: int,
        assignee_id: int | None,
    ) -> Ticket:
        ticket = self.repository.get_by_id(ticket_id)

        if ticket is None:
            raise TicketNotFoundError

        if assignee_id is None:
            ticket.assignee_id = None

            return self.repository.save(ticket)

        user = self.user_repository.get_by_id(assignee_id)

        if user is None:
            raise AssigneeNotFoundError

        if not user.is_active:
            raise InactiveAssigneeError

        ticket.assignee_id = user.id

        return self.repository.save(ticket)

    def update_ticket_status(
        self,
        ticket_id: int,
        new_status: TicketStatus,
        current_user: User,
    ) -> Ticket:
        ticket = self.repository.get_by_id(ticket_id)

        if ticket is None:
            raise TicketNotFoundError

        is_admin = current_user.role == UserRole.admin

        is_assignee = ticket.assignee_id == current_user.id

        if not is_admin and not is_assignee:
            raise TicketAccessDeniedError

        allowed_transitions = {
            TicketStatus.open: {
                TicketStatus.in_progress,
            },
            TicketStatus.in_progress: {
                TicketStatus.closed,
            },
            TicketStatus.closed: {
                TicketStatus.open,
            },
        }

        allowed_next_statuses = allowed_transitions[ticket.status]

        if new_status not in allowed_next_statuses:
            raise InvalidStatusTransitionError

        ticket.status = new_status

        return self.repository.save(ticket)
