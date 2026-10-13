from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.ticket import TicketRepository

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
    TicketStatusUpdate,
)
from app.services.ticket import (
    AssigneeNotFoundError,
    InactiveAssigneeError,
    TicketNotFoundError,
    TicketService,
    InvalidStatusTransitionError,
    TicketAccessDeniedError,
)
from app.domain.ticket import TicketPriority, TicketStatus

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
def list_tickets(
    ticket_status: TicketStatus | None = Query(
        default=None,
        alias="status",
    ),
    priority: TicketPriority | None = None,
    assignee_id: int | None = None,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    service: TicketService = Depends(
        get_ticket_service
    ),
):
    return service.list_tickets(
        status=ticket_status,
        priority=priority,
        assignee_id=assignee_id,
        limit=limit,
        offset=offset,
    )


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
@router.patch(
    "/{ticket_id}/status",
    response_model=TicketRead,
)
def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    service: TicketService = Depends(
        get_ticket_service
    ),
):
    try:
        return service.update_ticket_status(
            ticket_id=ticket_id,
            new_status=status_update.status,
            current_user=current_user,
        )

    except TicketNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    except TicketAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change this ticket's status",
        )

    except InvalidStatusTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid ticket status transition",
        )