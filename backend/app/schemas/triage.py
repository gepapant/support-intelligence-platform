from pydantic import BaseModel, Field

from app.domain.ticket import TicketPriority
from app.domain.triage import TicketCategory, TicketSentiment


class TicketTriageResult(BaseModel):
    category: TicketCategory
    sentiment: TicketSentiment
    suggested_priority: TicketPriority

    summary: str = Field(
        min_length=1,
        max_length=500,
    )
