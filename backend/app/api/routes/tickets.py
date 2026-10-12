from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.ticket import TicketRepository
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate
from app.services.ticket import TicketService


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


def get_ticket_service(
    db: Session = Depends(get_db),
) -> TicketService:
    repository = TicketRepository(db)

    return TicketService(repository)


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