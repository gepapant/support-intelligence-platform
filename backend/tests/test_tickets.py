def test_create_ticket(client):
    response = client.post(
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
    assert data["description"] == (
        "Customer did not receive the reset email."
    )
    assert data["priority"] == "high"
    assert data["status"] == "open"

def test_create_ticket_rejects_invalid_priority(client):
    response = client.post(
        "/tickets",
        json={
            "title": "Broken login",
            "description": "Customer cannot log in.",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422

def test_get_ticket(client):
    create_response = client.post(
        "/tickets",
        json={
            "title": "Missing refund",
            "description": "Refund has not arrived.",
            "priority": "medium",
        },
    )

    ticket_id = create_response.json()["id"]

    response = client.get(f"/tickets/{ticket_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == ticket_id
    assert data["title"] == "Missing refund"

def test_get_missing_ticket_returns_404(client):
    response = client.get("/tickets/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found"
    }


def test_list_tickets(client):
    client.post(
        "/tickets",
        json={
            "title": "First ticket",
            "description": "First description",
            "priority": "low",
        },
    )

    client.post(
        "/tickets",
        json={
            "title": "Second ticket",
            "description": "Second description",
            "priority": "high",
        },
    )

    response = client.get("/tickets")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "First ticket"
    assert data[1]["title"] == "Second ticket"