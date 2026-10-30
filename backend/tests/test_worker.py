import pytest

from app.core.config import queue_settings
from app.models.knowledge import (
    KnowledgeArticle,
)
from app.repositories.knowledge_chunk import (
    KnowledgeChunkRepository,
)
from app.services.knowledge_queue import (
    KnowledgeIndexDispatcher,
    KnowledgeIndexDispatchError,
)
from app.worker.celery_app import celery_app
from app.worker.tasks import (
    index_knowledge_article,
    index_knowledge_article_now,
    mark_knowledge_index_failed,
    mark_knowledge_index_queued,
    ping,
)
from tests.conftest import TestingSessionLocal


def test_queue_defaults_use_redis():
    assert queue_settings.broker_url == "redis://localhost:6379/0"

    assert queue_settings.result_backend == "redis://localhost:6379/1"


def test_celery_uses_json_serialization():
    assert celery_app.conf.task_serializer == "json"

    assert "json" in celery_app.conf.accept_content

    assert celery_app.conf.result_serializer == "json"


def test_ping_task_runs_without_broker():
    assert ping.run() == "pong"


def test_index_task_is_registered():
    assert index_knowledge_article.name == "knowledge.index_article"


def test_index_article_now(
    client,
    monkeypatch,
):
    db = TestingSessionLocal()

    article = KnowledgeArticle(
        title="Background indexing",
        content=("Refund duplicate payments after verification."),
        is_active=True,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    article_id = article.id

    db.close()

    monkeypatch.setattr(
        "app.worker.tasks.SessionLocal",
        TestingSessionLocal,
    )

    result = index_knowledge_article_now(article_id)

    assert result["article_id"] == article_id

    assert result["chunks_indexed"] == 1

    assert result["embedding_model"] == "hash-embedding-dev-v2"

    verification_db = TestingSessionLocal()

    repository = KnowledgeChunkRepository(verification_db)

    chunks = repository.get_by_article(article_id)

    assert len(chunks) == 1
    assert chunks[0].embedding is not None

    article = verification_db.get(
        KnowledgeArticle,
        article_id,
    )

    assert article is not None
    assert article.indexing_status == "ready"
    assert article.indexing_error is None
    assert article.indexed_at is not None

    verification_db.close()


def test_dispatcher_enqueues_index_task(
    monkeypatch,
):
    captured: list[int] = []

    class FakeResult:
        id = "job-123"

    def fake_delay(
        article_id: int,
    ):
        captured.append(article_id)

        return FakeResult()

    monkeypatch.setattr(
        index_knowledge_article,
        "delay",
        fake_delay,
    )

    dispatcher = KnowledgeIndexDispatcher()

    task_id = dispatcher.enqueue(42)

    assert captured == [42]
    assert task_id == "job-123"


def test_dispatcher_wraps_broker_failure(
    monkeypatch,
):
    def fail_delay(
        article_id: int,
    ):
        raise ConnectionError("Redis unavailable")

    monkeypatch.setattr(
        index_knowledge_article,
        "delay",
        fail_delay,
    )

    dispatcher = KnowledgeIndexDispatcher()

    with pytest.raises(
        KnowledgeIndexDispatchError,
        match=("Unable to dispatch knowledge indexing task"),
    ):
        dispatcher.enqueue(42)


def test_mark_index_queued(
    client,
    monkeypatch,
):
    db = TestingSessionLocal()

    article = KnowledgeArticle(
        title="Queue status",
        content="Queue test content.",
        is_active=True,
        indexing_status="failed",
        indexing_error="Previous error",
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    article_id = article.id

    db.close()

    monkeypatch.setattr(
        "app.worker.tasks.SessionLocal",
        TestingSessionLocal,
    )

    mark_knowledge_index_queued(article_id)

    verification_db = TestingSessionLocal()

    stored = verification_db.get(
        KnowledgeArticle,
        article_id,
    )

    assert stored is not None
    assert stored.indexing_status == "queued"
    assert stored.indexing_error is None
    assert stored.indexed_at is None

    verification_db.close()


def test_mark_index_failed(
    client,
    monkeypatch,
):
    db = TestingSessionLocal()

    article = KnowledgeArticle(
        title="Failed indexing",
        content="Failure test content.",
        is_active=True,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    article_id = article.id

    db.close()

    monkeypatch.setattr(
        "app.worker.tasks.SessionLocal",
        TestingSessionLocal,
    )

    mark_knowledge_index_failed(
        article_id,
        RuntimeError("Embedding provider unavailable"),
    )

    verification_db = TestingSessionLocal()

    stored = verification_db.get(
        KnowledgeArticle,
        article_id,
    )

    assert stored is not None
    assert stored.indexing_status == "failed"

    assert stored.indexing_error == "Embedding provider unavailable"

    assert stored.indexed_at is None

    verification_db.close()


def test_index_task_retries_on_temporary_failure(
    monkeypatch,
):
    calls: dict[str, object] = {}

    def fail_index(
        article_id: int,
    ) -> dict[str, int | str]:
        raise RuntimeError("Temporary embedding failure")

    def fake_mark_queued(
        article_id: int,
    ) -> None:
        calls["queued_article_id"] = article_id

    def fake_retry(
        *,
        exc: Exception,
        countdown: int,
    ):
        calls["retry_error"] = str(exc)
        calls["countdown"] = countdown

        raise RuntimeError("Retry scheduled")

    monkeypatch.setattr(
        "app.worker.tasks.index_knowledge_article_now",
        fail_index,
    )

    monkeypatch.setattr(
        "app.worker.tasks.mark_knowledge_index_queued",
        fake_mark_queued,
    )

    monkeypatch.setattr(
        index_knowledge_article,
        "retry",
        fake_retry,
    )

    index_knowledge_article.push_request(retries=0)

    try:
        with pytest.raises(
            RuntimeError,
            match="Retry scheduled",
        ):
            index_knowledge_article.run(42)
    finally:
        index_knowledge_article.pop_request()

    assert calls["queued_article_id"] == 42

    assert calls["retry_error"] == "Temporary embedding failure"

    assert calls["countdown"] == 5


def test_index_task_marks_failed_after_max_retries(
    monkeypatch,
):
    calls: dict[str, object] = {}

    def fail_index(
        article_id: int,
    ) -> dict[str, int | str]:
        raise RuntimeError("Permanent embedding failure")

    def fake_mark_failed(
        article_id: int,
        error: Exception,
    ) -> None:
        calls["failed_article_id"] = article_id

        calls["error"] = str(error)

    monkeypatch.setattr(
        "app.worker.tasks.index_knowledge_article_now",
        fail_index,
    )

    monkeypatch.setattr(
        "app.worker.tasks.mark_knowledge_index_failed",
        fake_mark_failed,
    )

    index_knowledge_article.push_request(retries=3)

    try:
        with pytest.raises(
            RuntimeError,
            match=("Permanent embedding failure"),
        ):
            index_knowledge_article.run(42)
    finally:
        index_knowledge_article.pop_request()

    assert calls["failed_article_id"] == 42

    assert calls["error"] == "Permanent embedding failure"


def test_dispatcher_can_index_synchronously(
    monkeypatch,
):
    captured: list[int] = []

    def fake_index(
        article_id: int,
    ) -> dict[str, int | str]:
        captured.append(article_id)

        return {
            "article_id": article_id,
            "chunks_indexed": 1,
            "embedding_model": ("hash-embedding-dev-v2"),
        }

    monkeypatch.setenv(
        "KNOWLEDGE_INDEX_MODE",
        "sync",
    )

    monkeypatch.setattr(
        "app.services.knowledge_queue.index_knowledge_article_now",
        fake_index,
    )

    dispatcher = KnowledgeIndexDispatcher()

    result = dispatcher.enqueue(42)

    assert captured == [42]

    assert result == "sync-42"
