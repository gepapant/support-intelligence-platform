from enum import Enum


class ReplyDecision(str, Enum):
    pending = "pending"
    accepted = "accepted"
    edited = "edited"
    rejected = "rejected"
