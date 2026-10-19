from app.domain.retrieval import (
    RetrievedKnowledgeChunk,
)
from app.integrations.hash_embedding import (
    HashEmbeddingProvider,
)
from app.services.knowledge_search import (
    KnowledgeSearchService,
)


class FakeKnowledgeSearchRepository:
    def __init__(self):
        self.query_embedding = None
        self.limit = None

    def search_similar(
        self,
        query_embedding: list[float],
        limit: int = 3,
    ) -> list[RetrievedKnowledgeChunk]:
        self.query_embedding = query_embedding
        self.limit = limit

        return [
            RetrievedKnowledgeChunk(
                chunk_id=1,
                article_id=10,
                chunk_index=0,
                content=("Refunds are processed within five business days."),
                article_title="Refund policy",
                source_url=("https://example.com/refunds"),
                similarity=0.9,
            )
        ]


def test_search_embeds_query_and_calls_repository():
    repository = FakeKnowledgeSearchRepository()
    provider = HashEmbeddingProvider()

    service = KnowledgeSearchService(
        repository=repository,
        embedding_provider=provider,
    )

    results = service.search(
        "How long does a refund take?",
        limit=3,
    )

    assert len(results) == 1
    assert results[0].article_title == "Refund policy"

    assert repository.limit == 3

    assert repository.query_embedding is not None
    assert len(repository.query_embedding) == 384


def test_search_rejects_empty_query():
    repository = FakeKnowledgeSearchRepository()

    service = KnowledgeSearchService(
        repository=repository,
        embedding_provider=(HashEmbeddingProvider()),
    )

    try:
        service.search("   ")

    except ValueError:
        pass

    else:
        raise AssertionError("Expected ValueError")


def test_search_rejects_invalid_limit():
    repository = FakeKnowledgeSearchRepository()

    service = KnowledgeSearchService(
        repository=repository,
        embedding_provider=(HashEmbeddingProvider()),
    )

    try:
        service.search(
            "refund policy",
            limit=0,
        )

    except ValueError:
        pass

    else:
        raise AssertionError("Expected ValueError")
