from app.domain.retrieval import (
    RetrievedKnowledgeChunk,
)


class TemplateReplyProvider:
    provider_name = "template-rag-dev-v1"

    def generate(
        self,
        ticket_title: str,
        ticket_description: str,
        context: list[RetrievedKnowledgeChunk],
    ) -> str:
        if not context:
            return (
                "Thank you for contacting support. "
                "We are reviewing your request and will "
                "get back to you as soon as possible."
            )

        best_match = context[0]

        return (
            "Thank you for contacting support. "
            f"Based on our support documentation: "
            f"{best_match.content} "
            "Please let us know if you need any further help."
        )
