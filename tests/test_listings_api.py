class TestListingsAPI:
    def test_list_listings_empty(self, client):
        response = client.get("/api/v1/listings")
        assert response.status_code == 200
        data = response.json()
        assert data["listings"] == []
        assert data["total"] == 0

    def test_list_listings(self, client, sample_listings):
        response = client.get("/api/v1/listings")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3

    def test_filter_by_platform(self, client, sample_listings):
        response = client.get("/api/v1/listings?platform=wallapop")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for listing in data["listings"]:
            assert listing["platform"] == "wallapop"

    def test_filter_by_sold_status(self, client, sample_listings):
        response = client.get("/api/v1/listings?is_sold=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["listings"][0]["is_sold"] is True

    def test_filter_by_reserved(self, client, sample_listings):
        response = client.get("/api/v1/listings?is_reserved=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["listings"][0]["lpn"] == "LST003"

    def test_listings_pagination(self, client, sample_listings):
        response = client.get("/api/v1/listings?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["listings"]) == 2
        assert data["total"] == 3

    def test_performance_empty(self, client):
        response = client.get("/api/v1/listings/performance")
        assert response.status_code == 200
        data = response.json()
        assert data["total_listings"] == 0
        assert data["total_views"] == 0
        assert data["conversion_rate"] == 0.0

    def test_performance_with_data(self, client, sample_listings):
        response = client.get("/api/v1/listings/performance")
        assert response.status_code == 200
        data = response.json()
        assert data["total_listings"] == 3
        assert data["total_views"] == 430
        assert data["total_favorites"] == 37
        assert data["total_conversations"] == 9
        assert data["avg_views"] == round(430 / 3, 2)
        assert data["conversion_rate"] == round(1 / 3 * 100, 2)
        assert "wallapop" in data["platforms"]
        assert "vinted" in data["platforms"]
