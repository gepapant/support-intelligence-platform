from enum import Enum


class TicketCategory(str, Enum):
    account = "account"
    billing = "billing"
    technical = "technical"
    refund = "refund"
    feature_request = "feature_request"
    other = "other"


class TicketSentiment(str, Enum):
    negative = "negative"
    neutral = "neutral"
    positive = "positive"
