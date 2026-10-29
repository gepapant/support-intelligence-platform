from datetime import date

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_tickets: int
    unassigned_tickets: int
    ai_analyzed_tickets: int
    high_priority_active_tickets: int
    negative_active_tickets: int

    status_counts: dict[str, int]
    priority_counts: dict[str, int]
    category_counts: dict[str, int]
    sentiment_counts: dict[str, int]


class AnalyticsTrendPoint(BaseModel):
    date: date
    tickets_created: int


class AnalyticsTrends(BaseModel):
    days: int
    created_per_day: list[AnalyticsTrendPoint]
