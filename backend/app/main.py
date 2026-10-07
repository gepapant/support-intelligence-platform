from fastapi import FastAPI, status

from app.schemas.ticket import (
    TicketCreate,
    TicketRead,
    TicketStatus,
)

app = FastAPI(
    title="Support Intelligence API",
    version = "0.1.0",
)

tickets: list[TicketRead] = []


@app.get("/")
def root():
    return {"message": "Support Intelligence API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post(
    "/tickets",
    response_model = TicketRead,
    status_code = status.HTTP_201_CREATED,
)
def create_ticket(ticket: TicketCreate):
    new_ticket = TicketRead(
        id=len(tickets) + 1,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=TicketStatus.open,
    )
    tickets.append(new_ticket)

    return new_ticket


@app.get("/tickets", response_model = list[TicketRead])
def get_tickets():
    return tickets


