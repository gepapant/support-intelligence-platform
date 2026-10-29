from datetime import (
    datetime,
    timedelta,
    timezone,
)

from app.models.ticket import Ticket
from tests.conftest import (
    TestingSessionLocal,
)


def test_admin_can_get_analytics_summary(
    admin_client,
):
    first = admin_client.post(
        "/tickets",
        json={
            "title": "Billing issue",
            "description": ("Customer has a billing problem."),
            "priority": "low",
        },
    )

    second = admin_client.post(
        "/tickets",
        json={
            "title": "Technical outage",
            "description": ("Customer cannot access the service."),
            "priority": "high",
        },
    )

    third = admin_client.post(
        "/tickets",
        json={
            "title": "General question",
            "description": ("Customer has a question."),
            "priority": "medium",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 201

    second_id = second.json()["id"]
    third_id = third.json()["id"]

    response = admin_client.patch(
        f"/tickets/{second_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    response = admin_client.patch(
        f"/tickets/{third_id}/status",
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    response = admin_client.patch(
        f"/tickets/{third_id}/status",
        json={
            "status": "closed",
        },
    )

    assert response.status_code == 200

    db = TestingSessionLocal()

    first_ticket = db.get(
        Ticket,
        first.json()["id"],
    )

    second_ticket = db.get(
        Ticket,
        second_id,
    )

    assert first_ticket is not None
    assert second_ticket is not None

    first_ticket.ai_category = "billing"
    first_ticket.ai_sentiment = "positive"
    first_ticket.ai_analyzed_at = datetime.now(timezone.utc)

    second_ticket.ai_category = "technical"
    second_ticket.ai_sentiment = "negative"
    second_ticket.ai_analyzed_at = datetime.now(timezone.utc)

    db.commit()
    db.close()

    response = admin_client.get("/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_tickets"] == 3
    assert data["unassigned_tickets"] == 3
    assert data["ai_analyzed_tickets"] == 2

    assert data["high_priority_active_tickets"] == 1

    assert data["negative_active_tickets"] == 1

    assert data["status_counts"] == {
        "open": 1,
        "in_progress": 1,
        "closed": 1,
    }

    assert data["priority_counts"] == {
        "low": 1,
        "medium": 1,
        "high": 1,
    }

    assert data["category_counts"]["billing"] == 1

    assert data["category_counts"]["technical"] == 1

    assert data["category_counts"]["refund"] == 0

    assert data["sentiment_counts"]["positive"] == 1

    assert data["sentiment_counts"]["negative"] == 1

    assert data["sentiment_counts"]["neutral"] == 0


def test_admin_can_get_seven_day_ticket_trends(
    admin_client,
):
    first = admin_client.post(
        "/tickets",
        json={
            "title": "Today ticket",
            "description": "Created today.",
            "priority": "medium",
        },
    )

    second = admin_client.post(
        "/tickets",
        json={
            "title": "Recent ticket",
            "description": ("Created two days ago."),
            "priority": "medium",
        },
    )

    third = admin_client.post(
        "/tickets",
        json={
            "title": "Old ticket",
            "description": ("Created outside the window."),
            "priority": "medium",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 201

    now = datetime.now(timezone.utc)

    db = TestingSessionLocal()

    first_ticket = db.get(
        Ticket,
        first.json()["id"],
    )

    second_ticket = db.get(
        Ticket,
        second.json()["id"],
    )

    third_ticket = db.get(
        Ticket,
        third.json()["id"],
    )

    assert first_ticket is not None
    assert second_ticket is not None
    assert third_ticket is not None

    first_ticket.created_at = now

    second_ticket.created_at = now - timedelta(days=2)

    third_ticket.created_at = now - timedelta(days=10)

    db.commit()
    db.close()

    response = admin_client.get("/analytics/trends?days=7")

    assert response.status_code == 200

    data = response.json()

    assert data["days"] == 7

    points = data["created_per_day"]

    assert len(points) == 7

    counts_by_date = {point["date"]: point["tickets_created"] for point in points}

    today = now.date()

    two_days_ago = today - timedelta(days=2)

    assert counts_by_date[today.isoformat()] == 1

    assert counts_by_date[two_days_ago.isoformat()] == 1

    assert sum(counts_by_date.values()) == 2


def test_admin_can_get_thirty_day_ticket_trends(
    admin_client,
):
    response = admin_client.get("/analytics/trends?days=30")

    assert response.status_code == 200

    data = response.json()

    assert data["days"] == 30

    assert len(data["created_per_day"]) == 30


def test_analytics_rejects_invalid_trend_window(
    admin_client,
):
    response = admin_client.get("/analytics/trends?days=14")

    assert response.status_code == 422


def test_agent_cannot_access_analytics(
    authenticated_client,
):
    response = authenticated_client.get("/analytics/summary")

    assert response.status_code == 403


def test_analytics_requires_authentication(
    client,
):
    response = client.get("/analytics/summary")

    assert response.status_code == 401
