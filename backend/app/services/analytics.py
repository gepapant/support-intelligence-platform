from datetime import (
    datetime,
    time,
    timedelta,
    timezone,
)

from app.domain.ticket import (
    TicketPriority,
    TicketStatus,
)
from app.domain.triage import (
    TicketCategory,
    TicketSentiment,
)
from app.models.ticket import Ticket
from app.repositories.analytics import (
    AnalyticsRepository,
)
from app.schemas.analytics import (
    AnalyticsSummary,
    AnalyticsTrendPoint,
    AnalyticsTrends,
)


class AnalyticsService:
    def __init__(
        self,
        repository: AnalyticsRepository,
    ):
        self.repository = repository

    def get_summary(
        self,
    ) -> AnalyticsSummary:
        status_counts = {status.value: 0 for status in TicketStatus}

        status_counts.update(self.repository.count_by(Ticket.status))

        priority_counts = {priority.value: 0 for priority in TicketPriority}

        priority_counts.update(self.repository.count_by(Ticket.priority))

        category_counts = {category.value: 0 for category in TicketCategory}

        category_counts.update(
            self.repository.count_by(
                Ticket.ai_category,
                exclude_null=True,
            )
        )

        sentiment_counts = {sentiment.value: 0 for sentiment in TicketSentiment}

        sentiment_counts.update(
            self.repository.count_by(
                Ticket.ai_sentiment,
                exclude_null=True,
            )
        )

        active_statuses = [
            TicketStatus.open,
            TicketStatus.in_progress,
        ]

        return AnalyticsSummary(
            total_tickets=(self.repository.count_tickets()),
            unassigned_tickets=(
                self.repository.count_tickets(Ticket.assignee_id.is_(None))
            ),
            ai_analyzed_tickets=(
                self.repository.count_tickets(Ticket.ai_analyzed_at.is_not(None))
            ),
            high_priority_active_tickets=(
                self.repository.count_tickets(
                    Ticket.priority == TicketPriority.high,
                    Ticket.status.in_(active_statuses),
                )
            ),
            negative_active_tickets=(
                self.repository.count_tickets(
                    Ticket.ai_sentiment == TicketSentiment.negative.value,
                    Ticket.status.in_(active_statuses),
                )
            ),
            status_counts=status_counts,
            priority_counts=priority_counts,
            category_counts=category_counts,
            sentiment_counts=sentiment_counts,
        )

    def get_trends(
        self,
        days: int,
    ) -> AnalyticsTrends:
        today = datetime.now(timezone.utc).date()

        start_day = today - timedelta(days=days - 1)

        since = datetime.combine(
            start_day,
            time.min,
            tzinfo=timezone.utc,
        )

        counts = self.repository.created_per_day(since)

        points: list[AnalyticsTrendPoint] = []

        for offset in range(days):
            current_day = start_day + timedelta(days=offset)

            points.append(
                AnalyticsTrendPoint(
                    date=current_day,
                    tickets_created=counts.get(
                        current_day,
                        0,
                    ),
                )
            )

        return AnalyticsTrends(
            days=days,
            created_per_day=points,
        )
