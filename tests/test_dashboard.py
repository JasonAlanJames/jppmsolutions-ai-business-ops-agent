from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_requires_auth():
    response = client.get("/dashboard")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dashboard login required."


def test_dashboard_triage_action_requires_auth():
    response = client.post("/dashboard/triage")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dashboard login required."


def test_dashboard_approve_action_requires_auth():
    response = client.post("/dashboard/approve/test-message-id")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dashboard login required."


def test_dashboard_reject_action_requires_auth():
    response = client.post("/dashboard/reject/test-message-id")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dashboard login required."


def test_dashboard_search_requires_auth():
    response = client.get("/dashboard?q=AI")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dashboard login required."

def test_dashboard_search_requires_auth():
    response = client.get("/dashboard?q=AI+is+awesome")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dashboard login required."

def test_dashboard_live_gmail_search_requires_auth():
    response = client.get("/dashboard?q=AI&live_gmail=true")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dashboard login required."