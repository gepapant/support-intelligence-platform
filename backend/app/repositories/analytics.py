from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket


class AnalyticsRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def count_tickets(
        self,
        *conditions,
    ) -> int:
        statement = select(func.count(Ticket.id)).select_from(Ticket)

        if conditions:
            statement = statement.where(*conditions)

        return int(self.db.scalar(statement) or 0)

    def count_by(
        self,
        column,
        *,
        exclude_null: bool = False,
    ) -> dict[str, int]:
        statement = (
            select(
                column,
                func.count(Ticket.id),
            )
            .select_from(Ticket)
            .group_by(column)
        )

        if exclude_null:
            statement = statement.where(column.is_not(None))

        rows = self.db.execute(statement).all()

        result: dict[str, int] = {}

        for value, count in rows:
            if value is None:
                continue

            key = value.value if hasattr(value, "value") else str(value)

            result[key] = int(count)

        return result

    def created_per_day(
        self,
        since: datetime,
    ) -> dict[date, int]:
        day_expression = func.date(Ticket.created_at)

        statement = (
            select(
                day_expression,
                func.count(Ticket.id),
            )
            .where(Ticket.created_at >= since)
            .group_by(day_expression)
            .order_by(day_expression)
        )

        rows = self.db.execute(statement).all()

        result: dict[date, int] = {}

        for day, count in rows:
            if isinstance(day, date):
                parsed_day = day
            else:
                parsed_day = date.fromisoformat(str(day))

            result[parsed_day] = int(count)

        return result
