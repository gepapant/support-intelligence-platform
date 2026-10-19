from app.models.knowledge_chunk import KnowledgeChunk
from app.repositories.knowledge import (
    KnowledgeRepository,
)
from app.repositories.knowledge_chunk import (
    KnowledgeChunkRepository,
)
from app.services.embedding import (
    EmbeddingProvider,
    EmbeddingProviderError,
)
from app.services.knowledge import (
    KnowledgeArticleNotFoundError,
)


def chunk_text(
    text: str,
    max_words: int = 180,
    overlap_words: int = 30,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    if overlap_words >= max_words:
        raise ValueError("overlap_words must be smaller than max_words")

    chunks: list[str] = []

    start = 0

    while start < len(words):
        end = min(
            start + max_words,
            len(words),
        )

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap_words

    return chunks


class KnowledgeIndexService:
    def __init__(
        self,
        article_repository: KnowledgeRepository,
        chunk_repository: KnowledgeChunkRepository,
        embedding_provider: EmbeddingProvider,
    ):
        self.article_repository = article_repository
        self.chunk_repository = chunk_repository
        self.embedding_provider = embedding_provider

    def rebuild_article_chunks(
        self,
        article_id: int,
    ) -> list[KnowledgeChunk]:
        article = self.article_repository.get_by_id(article_id)

        if article is None:
            raise KnowledgeArticleNotFoundError

        chunk_contents = chunk_text(article.content)

        embeddings = self.embedding_provider.embed(chunk_contents)

        if len(embeddings) != len(chunk_contents):
            raise EmbeddingProviderError(
                "Embedding provider returned an unexpected number of vectors"
            )

        for embedding in embeddings:
            if len(embedding) != (self.embedding_provider.dimensions):
                raise EmbeddingProviderError(
                    "Embedding provider returned an invalid vector dimension"
                )

        chunks = [
            KnowledgeChunk(
                article_id=article.id,
                chunk_index=index,
                content=content,
                embedding=embedding,
                embedding_model=(self.embedding_provider.model_name),
            )
            for index, (
                content,
                embedding,
            ) in enumerate(
                zip(
                    chunk_contents,
                    embeddings,
                    strict=True,
                )
            )
        ]

        return self.chunk_repository.replace_for_article(
            article_id=article.id,
            chunks=chunks,
        )
