from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealth:

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data

    def test_cache_status(self):
        response = client.get("/cache/status")
        assert response.status_code == 200
        data = response.json()
        assert "redis_available" in data


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "version" in data
    assert "uptime_seconds" in data
    assert "database" in data
    assert "cache" in data


def test_health_has_database_status():
    response = client.get("/health")
    data = response.json()
    assert data["database"]["status"] in ["healthy", "unhealthy"]


def test_health_has_cache_status():
    response = client.get("/health")
    data = response.json()
    assert data["cache"]["status"] in ["healthy", "unhealthy"]
