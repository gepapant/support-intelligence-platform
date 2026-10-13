def test_assigned_agent_can_start_ticket(
    admin_client,
):
    register_response = admin_client.post(
        "/auth/register",
        json={
            "email": "status-agent@example.com",
            "password": "Password123!",
        },
    )

    agent_id = register_response.json()["id"]

    login_response = admin_client.post(
        "/auth/login",
        json={
            "email": "status-agent@example.com",
            "password": "Password123!",
        },
    )

    token = login_response.json()["access_token"]

    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Workflow ticket",
            "description": "Test workflow.",
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

    response = admin_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_open_ticket_cannot_be_closed_directly(
    admin_client,
):
    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Invalid transition",
            "description": "Cannot close directly.",
            "priority": "medium",
        },
    )

    ticket_id = ticket_response.json()["id"]

    response = admin_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "closed",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Invalid ticket status transition"
    }


def test_unassigned_agent_cannot_change_status(
    authenticated_client,
):
    ticket_response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Unassigned ticket",
            "description": "Agent should be forbidden.",
            "priority": "low",
        },
    )

    ticket_id = ticket_response.json()["id"]

    response = authenticated_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 403


def test_admin_can_change_ticket_status(
    admin_client,
):
    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Admin workflow",
            "description": "Admin manages workflow.",
            "priority": "high",
        },
    )

    ticket_id = ticket_response.json()["id"]

    response = admin_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_closed_ticket_can_be_reopened(
    admin_client,
):
    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Reopen ticket",
            "description": "Testing reopen.",
            "priority": "medium",
        },
    )

    ticket_id = ticket_response.json()["id"]

    first_response = admin_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert first_response.status_code == 200

    second_response = admin_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "closed",
        },
    )

    assert second_response.status_code == 200

    reopen_response = admin_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "open",
        },
    )

    assert reopen_response.status_code == 200
    assert reopen_response.json()["status"] == "open"

def test_agent_cannot_change_another_agents_ticket(
    admin_client,
):
    first_register = admin_client.post(
        "/auth/register",
        json={
            "email": "owner@example.com",
            "password": "Password123!",
        },
    )

    owner_id = first_register.json()["id"]

    second_register = admin_client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "Password123!",
        },
    )

    assert second_register.status_code == 201

    login_response = admin_client.post(
        "/auth/login",
        json={
            "email": "other@example.com",
            "password": "Password123!",
        },
    )

    other_token = login_response.json()[
        "access_token"
    ]

    ticket_response = admin_client.post(
        "/tickets",
        json={
            "title": "Owned ticket",
            "description": "Assigned to someone else.",
            "priority": "medium",
        },
    )

    ticket_id = ticket_response.json()["id"]

    admin_client.patch(
        f"/tickets/{ticket_id}/assignment",
        json={
            "assignee_id": owner_id,
        },
    )

    response = admin_client.patch(
        f"/tickets/{ticket_id}/status",
        json={
            "status": "in_progress",
        },
        headers={
            "Authorization": f"Bearer {other_token}"
        },
    )

    assert response.status_code == 403