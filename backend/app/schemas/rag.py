from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from app.domain.reply import ReplyDecision


class RAGSource(BaseModel):
    article_id: int
    article_title: str
    source_url: str | None
    similarity: float


class SuggestedReplyResponse(BaseModel):
    suggestion_id: int
    reply: str
    provider: str
    sources: list[RAGSource]


class ReplySuggestionReviewRequest(BaseModel):
    decision: ReplyDecision

    final_reply: str | None = Field(
        default=None,
        min_length=1,
    )

    @model_validator(mode="after")
    def validate_review(self):
        if self.decision == ReplyDecision.pending:
            raise ValueError(
                "pending is not a review decision"
            )

        if self.decision == ReplyDecision.edited:
            if (
                self.final_reply is None
                or not self.final_reply.strip()
            ):
                raise ValueError(
                    "Edited replies require final_reply"
                )

            self.final_reply = (
                self.final_reply.strip()
            )

        elif self.final_reply is not None:
            raise ValueError(
                "final_reply is only allowed "
                "for edited replies"
            )

        return self


class ReplySuggestionReviewResponse(BaseModel):
    suggestion_id: int
    decision: ReplyDecision
    final_reply: str | None
    reviewed_at: datetime