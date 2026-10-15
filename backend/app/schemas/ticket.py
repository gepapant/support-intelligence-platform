from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.domain.ticket import TicketPriority, TicketStatus
from app.domain.triage import TicketCategory, TicketSentiment


class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.medium


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: TicketPriority | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")

        return self


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    assignee_id: int | None

    ai_category: TicketCategory | None
    ai_sentiment: TicketSentiment | None
    ai_suggested_priority: TicketPriority | None
    ai_summary: str | None
    ai_model: str | None
    ai_analyzed_at: datetime | None

    created_at: datetime
    updated_at: datetime


class TicketAssignment(BaseModel):
    assignee_id: int | None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus
