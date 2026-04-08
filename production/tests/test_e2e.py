import pytest
import asyncio
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

@pytest.fixture
async def client():
    async with AsyncClient(base_url=BASE_URL) as ac:
        yield ac

class TestHealthAndBasics:
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "channels" in data

class TestWebFormChannel:
    @pytest.mark.asyncio
    async def test_form_submission_success(self, client):
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Help with API authentication",
            "category": "technical",
            "message": "I need help with the API authentication flow"
        })
        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert len(data["ticket_id"]) > 0
        assert "message" in data

    @pytest.mark.asyncio
    async def test_form_validation_name_too_short(self, client):
        response = await client.post("/support/submit", json={
            "name": "A",
            "email": "test@example.com",
            "subject": "Valid subject here",
            "category": "general",
            "message": "This is a valid message with enough content"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_form_validation_invalid_email(self, client):
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "not-an-email",
            "subject": "Valid subject here",
            "category": "general",
            "message": "This is a valid message with enough content"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_form_validation_message_too_short(self, client):
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Valid subject",
            "category": "general",
            "message": "Short"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_form_invalid_category(self, client):
        response = await client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Valid subject here",
            "category": "invalid_category",
            "message": "This is a valid message with enough content"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_ticket_status_retrieval(self, client):
        submit_response = await client.post("/support/submit", json={
            "name": "Status Test User",
            "email": "statustest@example.com",
            "subject": "Testing ticket status retrieval",
            "category": "general",
            "message": "Testing that I can retrieve ticket status after submission"
        })
        ticket_id = submit_response.json()["ticket_id"]
        status_response = await client.get(f"/support/ticket/{ticket_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert "ticket_id" in data
        assert "status" in data

class TestWebhookEndpoints:
    @pytest.mark.asyncio
    async def test_gmail_webhook_accepts_request(self, client):
        response = await client.post("/webhooks/gmail", json={
            "message": {"data": "dGVzdA==", "messageId": "test-123"},
            "subscription": "projects/test/subscriptions/gmail-push"
        })
        assert response.status_code == 200
        assert "status" in response.json()

    @pytest.mark.asyncio
    async def test_whatsapp_webhook_accepts_request(self, client):
        response = await client.post("/webhooks/whatsapp", data={
            "MessageSid": "SM123",
            "From": "whatsapp:+1234567890",
            "Body": "Hello I need help",
            "ProfileName": "Test User"
        })
        assert response.status_code in [200, 403]

class TestMetrics:
    @pytest.mark.asyncio
    async def test_metrics_endpoint_responds(self, client):
        response = await client.get("/metrics/channels")
        assert response.status_code == 200

class TestMultipleSubmissions:
    @pytest.mark.asyncio
    async def test_concurrent_submissions(self, client):
        import asyncio
        tasks = []
        for i in range(5):
            tasks.append(client.post("/support/submit", json={
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "subject": f"Concurrent test {i}",
                "category": "general",
                "message": f"Testing concurrent submission number {i} to verify system stability"
            }))
        responses = await asyncio.gather(*tasks)
        ticket_ids = [r.json()["ticket_id"] for r in responses if r.status_code == 200]
        assert len(ticket_ids) == 5
        assert len(set(ticket_ids)) == 5  # All unique
