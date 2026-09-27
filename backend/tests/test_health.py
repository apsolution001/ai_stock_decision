from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok_and_version() -> None:
    response = TestClient(create_app()).get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"


def test_health_reports_paper_mode_by_default() -> None:
    response = TestClient(create_app()).get("/health")
    assert response.json()["trading_mode"] == "paper"
