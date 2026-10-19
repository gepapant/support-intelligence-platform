from app.integrations.hash_embedding import (
    HashEmbeddingProvider,
)
from app.models.knowledge import KnowledgeArticle
from app.repositories.knowledge import (
    KnowledgeRepository,
)
from app.repositories.knowledge_chunk import (
    KnowledgeChunkRepository,
)
from app.services.knowledge_index import (
    KnowledgeIndexService,
    chunk_text,
)
from tests.conftest import TestingSessionLocal


def test_chunk_text_splits_with_overlap():
    text = " ".join(f"word-{index}" for index in range(20))

    chunks = chunk_text(
        text,
        max_words=10,
        overlap_words=2,
    )

    assert len(chunks) == 3

    first = chunks[0].split()
    second = chunks[1].split()

    assert first[-2:] == second[:2]


def test_chunk_text_returns_empty_for_empty_text():
    assert chunk_text("") == []


def test_chunk_text_rejects_invalid_overlap():
    try:
        chunk_text(
            "some content",
            max_words=10,
            overlap_words=10,
        )

    except ValueError:
        pass

    else:
        raise AssertionError("Expected ValueError")


def test_rebuild_article_chunks(client):
    db = TestingSessionLocal()

    article = KnowledgeArticle(
        title="Refund policy",
        content=" ".join(f"word-{index}" for index in range(400)),
        is_active=True,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    article_repository = KnowledgeRepository(db)
    chunk_repository = KnowledgeChunkRepository(db)
    embedding_provider = HashEmbeddingProvider()
    service = KnowledgeIndexService(
        article_repository=article_repository,
        chunk_repository=chunk_repository,
        embedding_provider=embedding_provider,
    )

    chunks = service.rebuild_article_chunks(article.id)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2

    stored_chunks = chunk_repository.get_by_article(article.id)

    assert len(stored_chunks) == 3
    assert chunks[0].embedding is not None
    assert len(chunks[0].embedding) == 384
    assert chunks[0].embedding_model == embedding_provider.model_name
    db.close()


def test_hash_embedding_is_deterministic():
    provider = HashEmbeddingProvider()

    first = provider.embed(["password reset instructions"])[0]

    second = provider.embed(["password reset instructions"])[0]

    assert first == second
    assert len(first) == 384


def test_hash_embedding_normalizes_vector():
    provider = HashEmbeddingProvider()

    embedding = provider.embed(["refund payment billing"])[0]

    magnitude = sum(value * value for value in embedding) ** 0.5

    assert abs(magnitude - 1.0) < 0.000001
