from app.domain.retrieval import (
    RetrievedKnowledgeChunk,
)
from app.repositories.knowledge_chunk import (
    KnowledgeChunkRepository,
)
from app.services.embedding import (
    EmbeddingProvider,
    EmbeddingProviderError,
)


class KnowledgeSearchService:
    def __init__(
        self,
        repository: KnowledgeChunkRepository,
        embedding_provider: EmbeddingProvider,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider

    def search(
        self,
        query: str,
        limit: int = 3,
        min_similarity: float = 0.20,
    ) -> list[RetrievedKnowledgeChunk]:
        query = query.strip()

        if not query:
            raise ValueError("Search query cannot be empty")

        if limit < 1 or limit > 10:
            raise ValueError("Search limit must be between 1 and 10")

        embeddings = self.embedding_provider.embed([query])

        if len(embeddings) != 1:
            raise EmbeddingProviderError(
                "Embedding provider returned an unexpected number of vectors"
            )

        query_embedding = embeddings[0]

        if len(query_embedding) != (self.embedding_provider.dimensions):
            raise EmbeddingProviderError(
                "Embedding provider returned an invalid vector dimension"
            )

        results = self.repository.search_similar(
            query_embedding=query_embedding,
            limit=limit,
        )

        return [result for result in results if result.similarity >= min_similarity]
