def test_admin_can_list_users(admin_client):
    response = admin_client.get("/admin/users")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["email"] == "admin@example.com"
    assert data[0]["role"] == "admin"

    assert "hashed_password" not in data[0]


def test_agent_cannot_list_users(
    authenticated_client,
):
    response = authenticated_client.get("/admin/users")

    assert response.status_code == 403

    assert response.json() == {"detail": "Admin access required"}


def test_anonymous_user_cannot_list_users(client):
    response = client.get("/admin/users")

    assert response.status_code == 401
