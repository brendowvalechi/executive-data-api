class TestListCompanies:
    """Testes para GET /companies/"""

    def test_list_empty(self, client):
        """Retorna lista vazia quando não há empresas."""
        response = client.get("/companies/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []

    def test_list_all(self, client, sample_companies):
        """Retorna todas as empresas."""
        response = client.get("/companies/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["data"]) == 5

    def test_filter_by_sector(self, client, sample_companies):
        """Filtra empresas por setor."""
        response = client.get("/companies/?sector=Tecnologia")
        data = response.json()
        assert data["total"] == 2
        for company in data["data"]:
            assert "Tecnologia" in company["sector"]

    def test_filter_by_name(self, client, sample_companies):
        """Busca empresa por nome."""
        response = client.get("/companies/?name=Tech")
        data = response.json()
        assert data["total"] == 2  # Tech Corp e Tech Start

    def test_filter_by_state(self, client, sample_companies):
        """Filtra empresas por estado."""
        response = client.get("/companies/?state=SP")
        data = response.json()
        assert data["total"] == 2  # Tech Corp e Big Energy

    def test_filter_min_revenue(self, client, sample_companies):
        """Filtra por receita mínima."""
        response = client.get("/companies/?min_revenue=100000000")
        data = response.json()
        assert data["total"] == 2  # Energy SA (200M) e Big Energy (500M)

    def test_filter_max_employees(self, client, sample_companies):
        """Filtra por máximo de funcionários."""
        response = client.get("/companies/?max_employees=500")
        data = response.json()
        assert data["total"] == 3  # Tech Corp, Food Ltda, Tech Start

    def test_search(self, client, sample_companies):
        """Busca geral em múltiplos campos."""
        response = client.get("/companies/?search=Paulo")
        data = response.json()
        # Deve encontrar empresas em São Paulo
        assert data["total"] >= 1

    def test_sort_by_revenue_desc(self, client, sample_companies):
        """Ordena por receita decrescente."""
        response = client.get("/companies/?sort_by=revenue&order=desc")
        data = response.json()
        revenues = [c["revenue"] for c in data["data"]]
        assert revenues == sorted(revenues, reverse=True)

    def test_sort_by_name_asc(self, client, sample_companies):
        """Ordena por nome crescente."""
        response = client.get("/companies/?sort_by=name&order=asc")
        data = response.json()
        names = [c["name"] for c in data["data"]]
        assert names == sorted(names)

    def test_pagination(self, client, sample_companies):
        """Testa paginação."""
        response = client.get("/companies/?page=1&limit=2")
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["limit"] == 2

    def test_pagination_page_2(self, client, sample_companies):
        """Testa segunda página."""
        response = client.get("/companies/?page=2&limit=2")
        data = response.json()
        assert len(data["data"]) == 2
        assert data["page"] == 2

    def test_pagination_last_page(self, client, sample_companies):
        """Testa última página (parcial)."""
        response = client.get("/companies/?page=3&limit=2")
        data = response.json()
        assert len(data["data"]) == 1  # 5 total, page 3 com limit 2 = 1 item

    def test_invalid_sort_field(self, client):
        """Retorna 422 para campo de ordenação inválido."""
        response = client.get("/companies/?sort_by=invalido")
        assert response.status_code == 422

    def test_invalid_limit(self, client):
        """Retorna 422 para limit acima de 100."""
        response = client.get("/companies/?limit=500")
        assert response.status_code == 422

    def test_combined_filters(self, client, sample_companies):
        """Combina múltiplos filtros."""
        response = client.get(
            "/companies/?sector=Energia&sort_by=revenue&order=desc&limit=10"
        )
        data = response.json()
        assert data["total"] == 2
        revenues = [c["revenue"] for c in data["data"]]
        assert revenues == sorted(revenues, reverse=True)


class TestGetCompany:
    """Testes para GET /companies/{id}"""

    def test_get_existing(self, client, sample_companies):
        """Retorna empresa existente."""
        response = client.get("/companies/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "name" in data

    def test_get_nonexistent(self, client):
        """Retorna 404 para empresa inexistente."""
        response = client.get("/companies/9999")
        assert response.status_code == 404


class TestCompanyStats:
    """Testes para GET /companies/stats"""

    def test_stats_with_data(self, client, sample_companies):
        """Retorna estatísticas corretas."""
        response = client.get("/companies/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_companies"] == 5
        assert len(data["sectors"]) == 3  # Tecnologia, Energia, Alimentação

    def test_stats_empty(self, client):
        """Retorna stats vazias sem dados."""
        response = client.get("/companies/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_companies"] == 0
