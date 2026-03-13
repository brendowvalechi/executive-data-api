class TestHealth:
    """Testes para a rota raiz e endpoints de sistema."""

    def test_root(self, client):
        """Rota raiz retorna status online."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data

    def test_cache_status(self, client):
        """Endpoint de cache status retorna info."""
        response = client.get("/cache/status")
        assert response.status_code == 200
        data = response.json()
        assert "redis_available" in data
