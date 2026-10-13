def test_login_returns_access_token(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "Password123!",
        },
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_me_returns_authenticated_user(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "Password123!",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "Password123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "me@example.com"
    assert data["role"] == "agent"
    assert data["is_active"] is True