from app.worker.tasks import index_knowledge_article


class KnowledgeIndexDispatcher:
    def enqueue(
        self,
        article_id: int,
    ) -> str:
        result = index_knowledge_article.delay(article_id)

        return result.id
