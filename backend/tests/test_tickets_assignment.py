def test_admin_can_assign_ticket_to_agent(
    admin_client,
):
    register_response = admin_client.post(
        "/auth/register",
        json={
            "email": "assigned-agent@example.com",
            "password": "Password123!",
        },
    )

    assert register_response.status_code == 201

    agent_id = register_response.json()["id"]

    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Assignment test",
            "description": "Ticket needs an agent.",
            "priority": "medium",
        },
    )

    assert ticket_response.status_code == 201

    ticket_id = ticket_response.json()["id"]

    response = admin_client.patch(
        f"/tickets/{ticket_id}/assignment",
        json={
            "assignee_id": agent_id,
        },
    )

    assert response.status_code == 200
    assert response.json()["assignee_id"] == agent_id


def test_agent_cannot_assign_ticket(
    authenticated_client,
):
    ticket_response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Protected assignment",
            "description": "Agent must not assign.",
            "priority": "medium",
        },
    )

    ticket_id = ticket_response.json()["id"]

    response = authenticated_client.patch(
        f"/tickets/{ticket_id}/assignment",
        json={
            "assignee_id": 999,
        },
    )

    assert response.status_code == 403


def test_assignment_rejects_unknown_user(
    admin_client,
):
    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Unknown assignee",
            "description": "Testing missing user.",
            "priority": "low",
        },
    )

    ticket_id = ticket_response.json()["id"]

    response = admin_client.patch(
        f"/tickets/{ticket_id}/assignment",
        json={
            "assignee_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Assignee not found"}


def test_agent_can_list_own_tickets(
    admin_client,
):
    register_response = admin_client.post(
        "/auth/register",
        json={
            "email": "my-tickets@example.com",
            "password": "Password123!",
        },
    )

    agent_id = register_response.json()["id"]

    login_response = admin_client.post(
        "/auth/login",
        json={
            "email": "my-tickets@example.com",
            "password": "Password123!",
        },
    )

    token = login_response.json()["access_token"]

    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "My assigned ticket",
            "description": "Should appear in mine.",
            "priority": "high",
        },
    )

    ticket_id = ticket_response.json()["id"]

    assign_response = admin_client.patch(
        f"/tickets/{ticket_id}/assignment",
        json={
            "assignee_id": agent_id,
        },
    )

    assert assign_response.status_code == 200

    response = admin_client.get(
        "/tickets/mine",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == ticket_id
    assert data[0]["assignee_id"] == agent_id


def test_admin_can_unassign_ticket(
    admin_client,
):
    register_response = admin_client.post(
        "/auth/register",
        json={
            "email": "unassign-agent@example.com",
            "password": "Password123!",
        },
    )

    agent_id = register_response.json()["id"]

    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Unassign test",
            "description": "Ticket will be unassigned.",
            "priority": "medium",
        },
    )

    ticket_id = ticket_response.json()["id"]

    assign_response = admin_client.patch(
        f"/tickets/{ticket_id}/assignment",
        json={
            "assignee_id": agent_id,
        },
    )

    assert assign_response.status_code == 200
    assert assign_response.json()["assignee_id"] == agent_id

    unassign_response = admin_client.patch(
        f"/tickets/{ticket_id}/assignment",
        json={
            "assignee_id": None,
        },
    )

    assert unassign_response.status_code == 200
    assert unassign_response.json()["assignee_id"] is None


def test_assignment_rejects_unknown_ticket(
    admin_client,
):
    response = admin_client.patch(
        "/tickets/999999/assignment",
        json={
            "assignee_id": None,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}
