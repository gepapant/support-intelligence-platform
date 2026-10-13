from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate
from app.services.ticket import TicketService

from app.api.dependencies.auth import get_current_user

from app.api.dependencies.auth import (
    get_current_user,
    require_admin,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.ticket import (
    TicketAssignment,
    TicketCreate,
    TicketRead,
    TicketUpdate,
)
from app.services.ticket import (
    AssigneeNotFoundError,
    InactiveAssigneeError,
    TicketNotFoundError,
    TicketService,
)

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
    dependencies=[
        Depends(get_current_user),
    ],
)


def get_ticket_service(
    db: Session = Depends(get_db),
) -> TicketService:
    ticket_repository = TicketRepository(db)
    user_repository = UserRepository(db)

    return TicketService(
        repository=ticket_repository,
        user_repository=user_repository,
    )


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket: TicketCreate,
    service: TicketService = Depends(get_ticket_service),
):
    return service.create_ticket(ticket)

@router.get(
    "/mine",
    response_model=list[TicketRead],
)
def get_my_tickets(
    current_user: User = Depends(
        get_current_user
    ),
    service: TicketService = Depends(
        get_ticket_service
    ),
):
    return service.list_assigned_tickets(
        user_id=current_user.id
    )

@router.get(
    "",
    response_model=list[TicketRead],
)
def get_tickets(
    service: TicketService = Depends(get_ticket_service),
):
    return service.list_tickets()


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
)
def get_ticket(
    ticket_id: int,
    service: TicketService = Depends(get_ticket_service),
):
    ticket = service.get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket

@router.patch(
    "/{ticket_id}",
    response_model=TicketRead,
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    service: TicketService = Depends(get_ticket_service),
):
    ticket = service.update_ticket(
        ticket_id=ticket_id,
        ticket_data=ticket_data,
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket

@router.patch(
    "/{ticket_id}/assignment",
    response_model=TicketRead,
)
def assign_ticket(
    ticket_id: int,
    assignment: TicketAssignment,
    current_admin: User = Depends(
        require_admin
    ),
    service: TicketService = Depends(
        get_ticket_service
    ),
):
    try:
        return service.assign_ticket(
            ticket_id=ticket_id,
            assignee_id=assignment.assignee_id,
        )

    except TicketNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    except AssigneeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignee not found",
        )

    except InactiveAssigneeError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assignee is inactive",
        )