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