from enum import Enum

from pydantic import BaseModel


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.medium


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus