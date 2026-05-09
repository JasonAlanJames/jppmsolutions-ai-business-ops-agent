from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_triage_requires_auth():
    response = client.get("/emails/triage")

    assert response.status_code == 401


def test_approve_requires_auth():
    response = client.post(
        "/emails/approve",
        json={
            "message_id": "test-message",
            "approved": False,
            "reviewer": "Jason James",
            "notes": "Testing auth protection.",
        },
    )

    assert response.status_code == 401


def test_approvals_requires_auth():
    response = client.get("/emails/approvals")

    assert response.status_code == 401


def test_root_redirects_to_dashboard():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/dashboard"


def test_health_remains_public():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "running"