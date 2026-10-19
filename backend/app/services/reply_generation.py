from typing import Protocol

from app.domain.retrieval import (
    RetrievedKnowledgeChunk,
)


class ReplyProviderError(Exception):
    pass


class ReplyProvider(Protocol):
    provider_name: str

    def generate(
        self,
        ticket_title: str,
        ticket_description: str,
        context: list[RetrievedKnowledgeChunk],
    ) -> str: ...
