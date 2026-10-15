from app.api.routes.triage import get_triage_provider
from app.domain.ticket import TicketPriority
from app.domain.triage import (
    TicketCategory,
    TicketSentiment,
)
from app.integrations.openai_triage import TriageProviderError
from app.main import app
from app.schemas.triage import TicketTriageResult


class FakeTriageProvider:
    model_name = "fake-triage-v1"

    def analyze(
        self,
        title: str,
        description: str,
    ) -> TicketTriageResult:
        return TicketTriageResult(
            category=TicketCategory.billing,
            sentiment=TicketSentiment.negative,
            suggested_priority=TicketPriority.high,
            summary=("Customer reports being charged twice."),
        )


class FailingTriageProvider:
    model_name = "failing-provider"

    def analyze(
        self,
        title: str,
        description: str,
    ) -> TicketTriageResult:
        raise TriageProviderError("Provider failed")


def test_admin_can_run_ticket_triage(
    admin_client,
):
    app.dependency_overrides[get_triage_provider] = lambda: FakeTriageProvider()

    create_response = admin_client.post(
        "/tickets",
        json={
            "title": "Charged twice",
            "description": ("I was charged twice for my order."),
            "priority": "medium",
        },
    )

    ticket_id = create_response.json()["id"]

    response = admin_client.post(f"/tickets/{ticket_id}/triage")

    assert response.status_code == 200

    data = response.json()

    assert data["ai_category"] == "billing"
    assert data["ai_sentiment"] == "negative"
    assert data["ai_suggested_priority"] == "high"
    assert data["ai_summary"] == ("Customer reports being charged twice.")
    assert data["ai_model"] == "fake-triage-v1"
    assert data["ai_analyzed_at"] is not None

    get_response = admin_client.get(f"/tickets/{ticket_id}")

    persisted = get_response.json()

    assert persisted["ai_category"] == "billing"
    assert persisted["ai_model"] == "fake-triage-v1"


def test_unassigned_agent_cannot_run_triage(
    authenticated_client,
):
    app.dependency_overrides[get_triage_provider] = lambda: FakeTriageProvider()

    create_response = authenticated_client.post(
        "/tickets",
        json={
            "title": "Protected ticket",
            "description": "AI analysis should be blocked.",
            "priority": "medium",
        },
    )

    ticket_id = create_response.json()["id"]

    response = authenticated_client.post(f"/tickets/{ticket_id}/triage")

    assert response.status_code == 403
    assert response.json() == {"detail": "You cannot analyze this ticket"}


def test_triage_missing_ticket_returns_404(
    admin_client,
):
    app.dependency_overrides[get_triage_provider] = lambda: FakeTriageProvider()

    response = admin_client.post("/tickets/999999/triage")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found"}


def test_triage_provider_failure_returns_502(
    admin_client,
):
    app.dependency_overrides[get_triage_provider] = lambda: FailingTriageProvider()

    create_response = admin_client.post(
        "/tickets",
        json={
            "title": "AI failure test",
            "description": "Provider should fail.",
            "priority": "medium",
        },
    )

    ticket_id = create_response.json()["id"]

    response = admin_client.post(f"/tickets/{ticket_id}/triage")

    assert response.status_code == 502
    assert response.json() == {"detail": "AI triage provider failed"}
