from app.repositories.knowledge_chunk import (
    KnowledgeChunkRepository,
)
from tests.conftest import TestingSessionLocal


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


def test_agent_cannot_create_knowledge_article(
    authenticated_client,
):
    response = authenticated_client.post(
        "/knowledge",
        json={
            "title": "Protected article",
            "content": "Only admins may create this.",
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
    assert response.json() == {"detail": "Knowledge article not found"}


def test_admin_can_reindex_knowledge_article(
    admin_client,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Duplicate charges",
            "content": (
                "If a customer is charged twice, "
                "verify both payments and refund "
                "the duplicate charge."
            ),
            "source_url": ("https://example.com/help/duplicate-charges"),
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    response = admin_client.post(f"/knowledge/{article_id}/reindex")

    assert response.status_code == 200

    data = response.json()

    assert data["article_id"] == article_id
    assert data["chunks_indexed"] == 1
    assert data["embedding_model"] == "hash-embedding-dev-v2"


def test_reindex_missing_article_returns_404(
    admin_client,
):
    response = admin_client.post("/knowledge/999999/reindex")

    assert response.status_code == 404
    assert response.json() == {"detail": "Knowledge article not found"}


def test_create_article_indexes_chunks_automatically(
    admin_client,
):
    response = admin_client.post(
        "/knowledge",
        json={
            "title": "Automatic indexing",
            "content": ("Customers can reset their password from the login page."),
        },
    )

    assert response.status_code == 201

    article_id = response.json()["id"]

    db = TestingSessionLocal()

    repository = KnowledgeChunkRepository(db)

    chunks = repository.get_by_article(article_id)

    assert len(chunks) == 1
    assert chunks[0].embedding is not None
    assert chunks[0].embedding_model == "hash-embedding-dev-v2"

    db.close()


def test_content_update_rebuilds_chunks_automatically(
    admin_client,
):
    create_response = admin_client.post(
        "/knowledge",
        json={
            "title": "Long policy",
            "content": "Short original content.",
        },
    )

    assert create_response.status_code == 201

    article_id = create_response.json()["id"]

    updated_content = " ".join(f"word-{index}" for index in range(400))

    update_response = admin_client.patch(
        f"/knowledge/{article_id}",
        json={
            "content": updated_content,
        },
    )

    assert update_response.status_code == 200

    db = TestingSessionLocal()

    repository = KnowledgeChunkRepository(db)

    chunks = repository.get_by_article(article_id)

    assert len(chunks) == 3

    assert chunks[0].content != "Short original content."

    db.close()
