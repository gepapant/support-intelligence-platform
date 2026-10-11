from fastapi import Depends, FastAPI, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.ticket import TicketStatus
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketRead


app = FastAPI(
    title="Support Intelligence API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Support Intelligence API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/tickets",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
):
    new_ticket = Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=TicketStatus.open,
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket


@app.get("/tickets", response_model=list[TicketRead])
def get_tickets(
    db: Session = Depends(get_db),
):
    statement = select(Ticket)

    tickets = db.scalars(statement).all()

    return tickets