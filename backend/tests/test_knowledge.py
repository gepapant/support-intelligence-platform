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
