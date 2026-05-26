class TestOrdersAPI:
    def test_list_orders_empty(self, client):
        response = client.get("/api/v1/orders")
        assert response.status_code == 200
        data = response.json()
        assert data["orders"] == []
        assert data["total"] == 0

    def test_list_orders(self, client, sample_orders):
        response = client.get("/api/v1/orders")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    def test_list_orders_filter_status(self, client, sample_orders):
        response = client.get("/api/v1/orders?status_id=1")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["orders"][0]["request_id"] == "ORD-001"

    def test_list_orders_filter_date_range(self, client, sample_orders):
        response = client.get(
            "/api/v1/orders?date_from=2024-02-01&date_to=2024-03-01"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["orders"][0]["request_id"] == "ORD-002"

    def test_list_orders_filter_account(self, client, sample_orders):
        response = client.get("/api/v1/orders?account_id=ACC-01")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_list_orders_pagination(self, client, sample_orders):
        response = client.get("/api/v1/orders?page=1&page_size=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["orders"]) == 1
        assert data["total"] == 2

    def test_get_order_detail(self, client, sample_orders):
        response = client.get("/api/v1/orders/ORD-001")
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == "ORD-001"
        assert data["buyer_name"] == "John Doe"
        assert len(data["items"]) == 1
        assert data["items"][0]["lpn"] == "LPN001"

    def test_get_order_not_found(self, client):
        response = client.get("/api/v1/orders/NONEXISTENT")
        assert response.status_code == 404

    def test_update_status_valid_transition(self, client, sample_orders):
        response = client.patch(
            "/api/v1/orders/ORD-001/status",
            json={"status_id": 2, "notes": "Processing started"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status_id"] == 2
        assert data["notes"] == "Processing started"

    def test_update_status_invalid_transition(self, client, sample_orders):
        response = client.patch(
            "/api/v1/orders/ORD-001/status",
            json={"status_id": 4},
        )
        assert response.status_code == 422

    def test_update_status_not_found(self, client):
        response = client.patch(
            "/api/v1/orders/NOPE/status",
            json={"status_id": 2},
        )
        assert response.status_code == 404

    def test_update_status_cancel(self, client, sample_orders):
        response = client.patch(
            "/api/v1/orders/ORD-001/status",
            json={"status_id": 5},
        )
        assert response.status_code == 200
        assert response.json()["status_id"] == 5
