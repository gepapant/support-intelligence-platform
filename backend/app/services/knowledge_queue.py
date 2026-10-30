import os

from app.worker.tasks import (
    index_knowledge_article,
    index_knowledge_article_now,
)


class KnowledgeIndexDispatchError(Exception):
    pass


class KnowledgeIndexDispatcher:
    def enqueue(
        self,
        article_id: int,
    ) -> str:
        mode = (
            os.getenv(
                "KNOWLEDGE_INDEX_MODE",
                "async",
            )
            .strip()
            .lower()
        )

        if mode == "sync":
            try:
                index_knowledge_article_now(article_id)

            except Exception as exc:
                raise KnowledgeIndexDispatchError(
                    "Unable to index knowledge article"
                ) from exc

            return f"sync-{article_id}"

        try:
            result = index_knowledge_article.delay(article_id)

        except Exception as exc:
            raise KnowledgeIndexDispatchError(
                "Unable to dispatch knowledge indexing task"
            ) from exc

        return result.id
