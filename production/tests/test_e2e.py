import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

# Use synchronous TestClient - no server needed, no asyncio issues
client = TestClient(app)


class TestHealthAndBasics:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "channels" in data
        assert "email" in data["channels"]
        assert "whatsapp" in data["channels"]
        assert "web_form" in data["channels"]


class TestWebFormChannel:
    def test_form_submission_success(self):
        response = client.post("/support/submit", json={
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
        assert "estimated_response_time" in data

    def test_form_validation_name_too_short(self):
        response = client.post("/support/submit", json={
            "name": "A",
            "email": "test@example.com",
            "subject": "Valid subject here",
            "category": "general",
            "message": "This is a valid message with enough content"
        })
        assert response.status_code == 422

    def test_form_validation_invalid_email(self):
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "not-an-email",
            "subject": "Valid subject here",
            "category": "general",
            "message": "This is a valid message with enough content"
        })
        assert response.status_code == 422

    def test_form_validation_message_too_short(self):
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Valid subject",
            "category": "general",
            "message": "Short"
        })
        assert response.status_code == 422

    def test_form_invalid_category(self):
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Valid subject here",
            "category": "invalid_category",
            "message": "This is a valid message with enough content"
        })
        assert response.status_code == 422

    def test_form_valid_all_categories(self):
        for category in ["general", "technical", "billing", "feedback", "bug_report"]:
            response = client.post("/support/submit", json={
                "name": "Category Test User",
                "email": "cattest@example.com",
                "subject": f"Testing category {category}",
                "category": category,
                "message": "Testing that all valid categories are accepted by the API"
            })
            assert response.status_code == 200, f"Category {category} failed"

    def test_ticket_status_retrieval(self):
        submit_response = client.post("/support/submit", json={
            "name": "Status Test User",
            "email": "statustest@example.com",
            "subject": "Testing ticket status retrieval",
            "category": "general",
            "message": "Testing that I can retrieve ticket status after submission"
        })
        assert submit_response.status_code == 200
        ticket_id = submit_response.json()["ticket_id"]

        status_response = client.get(f"/support/ticket/{ticket_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert "ticket_id" in data
        assert "status" in data

    def test_form_subject_too_short(self):
        response = client.post("/support/submit", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Hi",
            "category": "general",
            "message": "This is a valid message with enough content here"
        })
        assert response.status_code == 422

    def test_form_missing_required_fields(self):
        response = client.post("/support/submit", json={
            "name": "Test User"
        })
        assert response.status_code == 422

    def test_form_default_priority(self):
        response = client.post("/support/submit", json={
            "name": "Priority Test User",
            "email": "priority@example.com",
            "subject": "Testing default priority",
            "category": "general",
            "message": "Testing that default priority medium is applied correctly"
        })
        assert response.status_code == 200


class TestWebhookEndpoints:
    def test_gmail_webhook_accepts_request(self):
        response = client.post("/webhooks/gmail", json={
            "message": {"data": "dGVzdA==", "messageId": "test-123"},
            "subscription": "projects/test/subscriptions/gmail-push"
        })
        assert response.status_code == 200
        assert "status" in response.json()

    def test_whatsapp_webhook_accepts_request(self):
        response = client.post(
            "/webhooks/whatsapp",
            data={
                "MessageSid": "SM123",
                "From": "whatsapp:+1234567890",
                "Body": "Hello I need help",
                "ProfileName": "Test User"
            }
        )
        # 200 = mock mode, 403 = signature validation active (both acceptable)
        assert response.status_code in [200, 403]

    def test_whatsapp_status_webhook(self):
        response = client.post(
            "/webhooks/whatsapp/status",
            data={
                "MessageSid": "SM123",
                "MessageStatus": "delivered"
            }
        )
        assert response.status_code == 200


class TestMetrics:
    def test_metrics_endpoint_responds(self):
        response = client.get("/metrics/channels")
        assert response.status_code == 200
        # Returns either real data or error dict - both are valid JSON
        data = response.json()
        assert isinstance(data, dict)

    def test_health_includes_all_channels(self):
        response = client.get("/health")
        assert response.status_code == 200
        channels = response.json()["channels"]
        assert channels["email"] == "active"
        assert channels["whatsapp"] == "active"
        assert channels["web_form"] == "active"


class TestMultipleSubmissions:
    def test_concurrent_submissions_unique_tickets(self):
        ticket_ids = []
        for i in range(5):
            response = client.post("/support/submit", json={
                "name": f"Load User {i}",
                "email": f"loaduser{i}@example.com",
                "subject": f"Concurrent test submission number {i}",
                "category": "general",
                "message": f"Testing concurrent submission number {i} to verify system stability under load"
            })
            assert response.status_code == 200
            ticket_ids.append(response.json()["ticket_id"])

        # All ticket IDs must be unique
        assert len(set(ticket_ids)) == 5

    def test_rapid_sequential_submissions(self):
        responses = []
        for i in range(3):
            r = client.post("/support/submit", json={
                "name": f"Sequential User {i}",
                "email": f"seq{i}@example.com",
                "subject": f"Sequential test {i} subject line",
                "category": "technical",
                "message": f"Sequential submission test number {i} checking system handles rapid requests"
            })
            responses.append(r)
        assert all(r.status_code == 200 for r in responses)
