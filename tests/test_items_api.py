class TestItemsAPI:
    def test_list_items_empty(self, client):
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_items_with_data(self, client, sample_items):
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_items_pagination(self, client, sample_items):
        response = client.get("/api/v1/items?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_list_items_page_2(self, client, sample_items):
        response = client.get("/api/v1/items?page=2&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    def test_filter_by_condition(self, client, sample_items):
        response = client.get("/api/v1/items?condition=new")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["condition"] == "new"

    def test_filter_by_availability(self, client, sample_items):
        response = client.get("/api/v1/items?available=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["available"] is True

    def test_filter_by_asin(self, client, sample_items):
        response = client.get("/api/v1/items?asin=B08N5WRWNW")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_filter_combined(self, client, sample_items):
        response = client.get("/api/v1/items?condition=new&available=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["lpn"] == "LPN001"

    def test_get_item(self, client, sample_items):
        response = client.get("/api/v1/items/LPN001")
        assert response.status_code == 200
        data = response.json()
        assert data["lpn"] == "LPN001"
        assert data["asin"] == "B08N5WRWNW"
        assert data["condition"] == "new"

    def test_get_item_not_found(self, client):
        response = client.get("/api/v1/items/NONEXISTENT")
        assert response.status_code == 404

    def test_create_item(self, client):
        payload = {
            "lpn": "LPN-NEW",
            "asin": "B0NEWITEM1",
            "amazon_description": "New Item",
            "sale_price": 35.00,
            "condition": "new",
            "available": True,
        }
        response = client.post("/api/v1/items", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["lpn"] == "LPN-NEW"
        assert data["sale_price"] == 35.00

    def test_create_item_duplicate(self, client, sample_items):
        payload = {"lpn": "LPN001", "condition": "new"}
        response = client.post("/api/v1/items", json=payload)
        assert response.status_code == 409

    def test_create_item_minimal(self, client):
        payload = {"lpn": "LPN-MIN"}
        response = client.post("/api/v1/items", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["available"] is True
        assert data["scraping_attempts"] == 0

    def test_update_item(self, client, sample_items):
        payload = {"sale_price": 30.00, "condition": "used_like_new"}
        response = client.patch("/api/v1/items/LPN001", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["sale_price"] == 30.00
        assert data["condition"] == "used_like_new"

    def test_update_item_not_found(self, client):
        payload = {"sale_price": 10.00}
        response = client.patch("/api/v1/items/NOPE", json=payload)
        assert response.status_code == 404

    def test_update_item_availability(self, client, sample_items):
        payload = {"available": False}
        response = client.patch("/api/v1/items/LPN001", json=payload)
        assert response.status_code == 200
        assert response.json()["available"] is False

    def test_get_stats(self, client, sample_items):
        response = client.get("/api/v1/items/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["available"] == 2
        assert data["sold"] == 1
        assert data["avg_price"] is not None

    def test_get_stats_empty(self, client):
        response = client.get("/api/v1/items/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["available"] == 0
        assert data["avg_price"] is None
