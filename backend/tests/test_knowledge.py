import pytest

from app.models.knowledge import (
    KnowledgeArticle,
)
from app.services.knowledge_queue import (
    KnowledgeIndexDispatcher,
    KnowledgeIndexDispatchError,
)
from tests.conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def fake_knowledge_index_queue(
    monkeypatch,
):
    queued_article_ids: list[int] = []

    def fake_enqueue(
        self,
        article_id: int,
    ) -> str:
        queued_article_ids.append(article_id)

        return "test-task-id"

    monkeypatch.setattr(
        KnowledgeIndexDispatcher,
        "enqueue",
        fake_enqueue,
    )

    return queued_article_ids


def test_admin_can_create_knowledge_article(
    admin_client,
):
    response = admin_client.post(
        "/knowledge",
        json={
            "title": "Refund policy",
            "content": ("Refunds are processed within five business days."),
            "source_url": ("https://example.com/help/refunds"),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Refund policy"
    assert data["is_active"] is True

    assert data["source_url"] == ("https://example.com/help/refunds")

    assert data["indexing_status"] == "queued"

    assert data["indexing_error"] is None
    assert data["indexed_at"] is None


def test_agent_cannot_create_knowledge_article(
    authenticated_client,
):
    response = authenticated_client.post(
        "/knowledge",
        json={
            "title": "Protected article",
            "content": ("Only admins may create this."),
        },
    )

    assert response.status_code == 403


def test_admin_can_list_and_update_knowledge_article(
    admin_client,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Password resets",
            "content": ("Users can request a password reset email."),
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    list_response = admin_client.get("/knowledge")

    assert list_response.status_code == 200

    assert len(list_response.json()) == 1

    update_response = admin_client.patch(
        f"/knowledge/{article_id}",
        json={
            "is_active": False,
        },
    )

    assert update_response.status_code == 200

    assert update_response.json()["is_active"] is False


def test_missing_knowledge_article_returns_404(
    admin_client,
):
    response = admin_client.get("/knowledge/999999")

    assert response.status_code == 404

    assert response.json() == {"detail": ("Knowledge article not found")}


def test_admin_can_queue_reindex(
    admin_client,
    fake_knowledge_index_queue,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Duplicate charges",
            "content": ("Verify both payments and refund the duplicate charge."),
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    fake_knowledge_index_queue.clear()

    response = admin_client.post(f"/knowledge/{article_id}/reindex")

    assert response.status_code == 200

    data = response.json()

    assert data["indexing_status"] == "queued"

    assert data["indexing_error"] is None
    assert data["indexed_at"] is None

    assert fake_knowledge_index_queue == [article_id]


def test_reindex_missing_article_returns_404(
    admin_client,
):
    response = admin_client.post("/knowledge/999999/reindex")

    assert response.status_code == 404

    assert response.json() == {"detail": ("Knowledge article not found")}


def test_create_article_queues_indexing(
    admin_client,
    fake_knowledge_index_queue,
):
    response = admin_client.post(
        "/knowledge",
        json={
            "title": "Queued indexing",
            "content": ("This article should be sent to the indexing queue."),
        },
    )

    assert response.status_code == 201

    article_id = response.json()["id"]

    assert fake_knowledge_index_queue == [article_id]


def test_content_update_queues_reindexing(
    admin_client,
    fake_knowledge_index_queue,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Original article",
            "content": ("Original content."),
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    fake_knowledge_index_queue.clear()

    update_response = admin_client.patch(
        f"/knowledge/{article_id}",
        json={
            "content": ("Updated content that requires re-indexing."),
        },
    )

    assert update_response.status_code == 200

    assert update_response.json()["indexing_status"] == "queued"

    assert fake_knowledge_index_queue == [article_id]


def test_metadata_update_does_not_queue_reindexing(
    admin_client,
    fake_knowledge_index_queue,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Metadata article",
            "content": ("Content remains unchanged."),
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    fake_knowledge_index_queue.clear()

    update_response = admin_client.patch(
        f"/knowledge/{article_id}",
        json={
            "title": ("Updated metadata article"),
        },
    )

    assert update_response.status_code == 200

    assert fake_knowledge_index_queue == []


def test_create_survives_queue_dispatch_failure(
    admin_client,
    monkeypatch,
):
    def fail_enqueue(
        self,
        article_id: int,
    ) -> str:
        raise KnowledgeIndexDispatchError("Unable to dispatch knowledge indexing task")

    monkeypatch.setattr(
        KnowledgeIndexDispatcher,
        "enqueue",
        fail_enqueue,
    )

    response = admin_client.post(
        "/knowledge",
        json={
            "title": "Broker outage",
            "content": ("This article should still be created."),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["indexing_status"] == "failed"

    assert data["indexing_error"] == ("Unable to dispatch knowledge indexing task")


def test_content_update_survives_queue_dispatch_failure(
    admin_client,
    monkeypatch,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Existing article",
            "content": "Original content.",
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    def fail_enqueue(
        self,
        article_id: int,
    ) -> str:
        raise KnowledgeIndexDispatchError("Unable to dispatch knowledge indexing task")

    monkeypatch.setattr(
        KnowledgeIndexDispatcher,
        "enqueue",
        fail_enqueue,
    )

    response = admin_client.patch(
        f"/knowledge/{article_id}",
        json={
            "content": "Updated content.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "Updated content."

    assert data["indexing_status"] == "failed"

    assert data["indexing_error"] == ("Unable to dispatch knowledge indexing task")


def test_failed_article_can_queue_reindex(
    admin_client,
    fake_knowledge_index_queue,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Retry article",
            "content": ("Content requiring retry."),
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    db = TestingSessionLocal()

    article = db.get(
        KnowledgeArticle,
        article_id,
    )

    assert article is not None

    article.indexing_status = "failed"
    article.indexing_error = "Previous broker failure"

    db.commit()
    db.close()

    fake_knowledge_index_queue.clear()

    response = admin_client.post(f"/knowledge/{article_id}/reindex")

    assert response.status_code == 200

    data = response.json()

    assert data["indexing_status"] == "queued"

    assert data["indexing_error"] is None
    assert data["indexed_at"] is None

    assert fake_knowledge_index_queue == [article_id]


def test_reindex_survives_broker_failure(
    admin_client,
    monkeypatch,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Reindex failure",
            "content": "Existing article.",
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    def fail_enqueue(
        self,
        article_id: int,
    ) -> str:
        raise KnowledgeIndexDispatchError("Unable to dispatch knowledge indexing task")

    monkeypatch.setattr(
        KnowledgeIndexDispatcher,
        "enqueue",
        fail_enqueue,
    )

    response = admin_client.post(f"/knowledge/{article_id}/reindex")

    assert response.status_code == 503

    db = TestingSessionLocal()

    article = db.get(
        KnowledgeArticle,
        article_id,
    )

    assert article is not None

    assert article.indexing_status == "failed"

    assert article.indexing_error == ("Unable to dispatch knowledge indexing task")

    db.close()
