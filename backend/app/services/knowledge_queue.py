from app.worker.tasks import (
    index_knowledge_article,
)


class KnowledgeIndexDispatchError(Exception):
    pass


class KnowledgeIndexDispatcher:
    def enqueue(
        self,
        article_id: int,
    ) -> str:
        try:
            result = index_knowledge_article.delay(article_id)

        except Exception as exc:
            raise KnowledgeIndexDispatchError(
                "Unable to dispatch knowledge indexing task"
            ) from exc

        return result.id
