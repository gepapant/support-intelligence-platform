from app.domain.ticket import TicketPriority
from app.domain.triage import (
    TicketCategory,
    TicketSentiment,
)
from app.schemas.triage import TicketTriageResult


class RuleBasedTriageProvider:
    model_name = "rule-based-dev-v1"

    def analyze(
        self,
        title: str,
        description: str,
    ) -> TicketTriageResult:
        text = f"{title} {description}".lower()

        if any(
            word in text
            for word in (
                "charged",
                "charge",
                "payment",
                "billing",
                "invoice",
            )
        ):
            category = TicketCategory.billing

        elif any(
            word in text
            for word in (
                "refund",
                "refunded",
                "money back",
            )
        ):
            category = TicketCategory.refund

        elif any(
            word in text
            for word in (
                "login",
                "password",
                "account",
            )
        ):
            category = TicketCategory.account

        elif any(
            word in text
            for word in (
                "error",
                "bug",
                "broken",
                "crash",
                "not working",
            )
        ):
            category = TicketCategory.technical

        elif any(
            phrase in text
            for phrase in (
                "feature request",
                "please add",
                "would be useful",
            )
        ):
            category = TicketCategory.feature_request

        else:
            category = TicketCategory.other

        if any(
            word in text
            for word in (
                "angry",
                "terrible",
                "awful",
                "frustrated",
                "charged twice",
                "not working",
            )
        ):
            sentiment = TicketSentiment.negative

        elif any(
            word in text
            for word in (
                "thanks",
                "thank you",
                "great",
                "happy",
            )
        ):
            sentiment = TicketSentiment.positive

        else:
            sentiment = TicketSentiment.neutral

        if any(
            phrase in text
            for phrase in (
                "urgent",
                "charged twice",
                "cannot login",
                "can't login",
                "crash",
            )
        ):
            suggested_priority = TicketPriority.high

        elif category in {
            TicketCategory.billing,
            TicketCategory.refund,
            TicketCategory.technical,
        }:
            suggested_priority = TicketPriority.medium

        else:
            suggested_priority = TicketPriority.low

        summary = (
            f"{title}. "
            f"Ticket classified as {category.value} "
            f"with {sentiment.value} sentiment."
        )

        return TicketTriageResult(
            category=category,
            sentiment=sentiment,
            suggested_priority=suggested_priority,
            summary=summary,
        )
