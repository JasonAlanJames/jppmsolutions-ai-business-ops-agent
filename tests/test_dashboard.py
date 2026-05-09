from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_dashboard_loads():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "JPPM AI Business Ops Dashboard" in response.text
    assert "Workflow Records" in response.text
    assert "Approval Decisions" in response.text