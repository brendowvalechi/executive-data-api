class TestListCities:
    """Testes para GET /cities/"""

    def test_list_empty(self, client):
        """Retorna lista vazia sem cidades."""
        response = client.get("/cities/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_all(self, client, sample_cities):
        """Retorna todas as cidades."""
        response = client.get("/cities/")
        data = response.json()
        assert data["total"] == 5

    def test_filter_by_state(self, client, sample_cities):
        """Filtra cidades por estado."""
        response = client.get("/cities/?state=SP")
        data = response.json()
        assert data["total"] == 2  # São Paulo e Campinas
        for city in data["data"]:
            assert city["state"] == "SP"

    def test_filter_by_name(self, client, sample_cities):
        """Busca cidade por nome."""
        response = client.get("/cities/?name=Belo")
        data = response.json()
        assert data["total"] == 1
        assert data["data"][0]["name"] == "Belo Horizonte"

    def test_filter_min_population(self, client, sample_cities):
        """Filtra por população mínima."""
        response = client.get("/cities/?min_population=5000000")
        data = response.json()
        assert data["total"] == 2  # SP (12.3M) e RJ (6.7M)

    def test_sort_by_population_desc(self, client, sample_cities):
        """Ordena por população decrescente."""
        response = client.get("/cities/?sort_by=population&order=desc")
        data = response.json()
        populations = [c["population"] for c in data["data"]]
        assert populations == sorted(populations, reverse=True)

    def test_sort_by_gdp_asc(self, client, sample_cities):
        """Ordena por PIB crescente."""
        response = client.get("/cities/?sort_by=gdp&order=asc")
        data = response.json()
        gdps = [c["gdp"] for c in data["data"]]
        assert gdps == sorted(gdps)

    def test_pagination(self, client, sample_cities):
        """Testa paginação."""
        response = client.get("/cities/?page=1&limit=3")
        data = response.json()
        assert len(data["data"]) == 3
        assert data["total"] == 5

    def test_search(self, client, sample_cities):
        """Busca geral."""
        response = client.get("/cities/?search=SP")
        data = response.json()
        assert data["total"] >= 1

    def test_invalid_sort_field(self, client):
        """Retorna 422 para campo inválido."""
        response = client.get("/cities/?sort_by=invalido")
        assert response.status_code == 422


class TestGetCity:
    """Testes para GET /cities/{id}"""

    def test_get_existing(self, client, sample_cities):
        """Retorna cidade existente."""
        response = client.get("/cities/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_nonexistent(self, client):
        """Retorna 404 para cidade inexistente."""
        response = client.get("/cities/9999")
        assert response.status_code == 404


class TestCityStats:
    """Testes para GET /cities/stats"""

    def test_stats_with_data(self, client, sample_cities):
        """Retorna estatísticas corretas."""
        response = client.get("/cities/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_cities"] == 5
        # SP, RJ, MG, PR
        assert len(data["states"]) == 4

    def test_stats_empty(self, client):
        """Stats vazias sem dados."""
        response = client.get("/cities/stats")
        assert response.status_code == 200
        assert response.json()["total_cities"] == 0
