def test_create_ticket(authenticated_client):
    response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Password reset issue",
            "description": "Customer did not receive the reset email.",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Password reset issue"
    assert data["description"] == ("Customer did not receive the reset email.")
    assert data["priority"] == "high"
    assert data["status"] == "open"


def test_create_ticket_rejects_invalid_priority(authenticated_client):
    response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Broken login",
            "description": "Customer cannot log in.",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422


def test_get_ticket(authenticated_client):
    create_response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Missing refund",
            "description": "Refund has not arrived.",
            "priority": "medium",
        },
    )

    ticket_id = create_response.json()["id"]

    response = authenticated_client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == ticket_id
    assert data["title"] == "Missing refund"


def test_get_missing_ticket_returns_404(authenticated_client):
    response = authenticated_client.get("/tickets/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}


def test_list_tickets(authenticated_client):
    authenticated_client.post(
        "/tickets",
        json={
            "title": "First ticket",
            "description": "First description",
            "priority": "low",
        },
    )

    authenticated_client.post(
        "/tickets",
        json={
            "title": "Second ticket",
            "description": "Second description",
            "priority": "high",
        },
    )

    response = authenticated_client.get("/tickets")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "First ticket"
    assert data[1]["title"] == "Second ticket"


def test_update_ticket_priority(authenticated_client):
    create_response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Billing problem",
            "description": "Customer was charged twice.",
            "priority": "low",
        },
    )

    ticket_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/tickets/{ticket_id}",
        json={
            "priority": "high",
        },
    )

    assert response.status_code == 200
    assert response.json()["priority"] == "high"


def test_update_missing_ticket_returns_404(
    authenticated_client,
):
    response = authenticated_client.patch(
        "/tickets/999999",
        json={
            "priority": "high",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}


def test_update_ticket_rejects_empty_body(authenticated_client):
    create_response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Test ticket",
            "description": "Testing empty PATCH.",
            "priority": "medium",
        },
    )

    ticket_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/tickets/{ticket_id}",
        json={},
    )

    assert response.status_code == 422


def test_tickets_require_authentication(client):
    response = client.get("/tickets")

    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/tickets",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_ticket_response_contains_timestamps(
    authenticated_client,
):
    response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Timestamp test",
            "description": "Testing timestamps.",
            "priority": "medium",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_filter_tickets_by_status(
    admin_client,
):
    admin_client.post(
        "/tickets",
        json={
            "title": "Open ticket",
            "description": "Remains open.",
            "priority": "medium",
        },
    )

    second = admin_client.post(
        "/tickets",
        json={
            "title": "Closed ticket",
            "description": "Will be closed.",
            "priority": "medium",
        },
    )

    second_id = second.json()["id"]

    first_update = admin_client.patch(
        f"/tickets/{second_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert first_update.status_code == 200

    second_update = admin_client.patch(
        f"/tickets/{second_id}/status",
        json={
            "status": "closed",
        },
    )

    assert second_update.status_code == 200

    response = admin_client.get("/tickets?status=closed")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Closed ticket"
    assert data[0]["status"] == "closed"


def test_filter_tickets_by_priority(
    authenticated_client,
):
    authenticated_client.post(
        "/tickets",
        json={
            "title": "Low priority",
            "description": "Not urgent.",
            "priority": "low",
        },
    )

    authenticated_client.post(
        "/tickets",
        json={
            "title": "High priority",
            "description": "Urgent issue.",
            "priority": "high",
        },
    )

    response = authenticated_client.get("/tickets?priority=high")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["priority"] == "high"
    assert data[0]["title"] == "High priority"


def test_ticket_pagination(
    authenticated_client,
):
    for number in range(5):
        response = authenticated_client.post(
            "/tickets",
            json={
                "title": f"Ticket {number}",
                "description": "Pagination test.",
                "priority": "medium",
            },
        )

        assert response.status_code == 201

    response = authenticated_client.get("/tickets?limit=2&offset=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Ticket 2"
    assert data[1]["title"] == "Ticket 3"


def test_ticket_pagination_rejects_invalid_limit(
    authenticated_client,
):
    response = authenticated_client.get("/tickets?limit=500")

    assert response.status_code == 422
