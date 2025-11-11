"""
Integration tests for FastAPI endpoints
"""

import pytest


@pytest.mark.integration
class TestRootEndpoints:
    """Test root endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "ADA.MARINA" in data["name"]
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


@pytest.mark.integration
class TestBerthEndpoints:
    """Test berth management endpoints"""

    def test_list_berths_empty(self, client):
        """Test listing berths when empty"""
        response = client.get("/api/v1/berths")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_berth(self, client, sample_berth_data):
        """Test creating a berth"""
        response = client.post("/api/v1/berths", json=sample_berth_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["berth_number"] == sample_berth_data["berth_number"]
        assert data["section"] == sample_berth_data["section"]

    def test_get_berth_by_id(self, client, sample_berth_data):
        """Test getting berth by ID"""
        # Create a berth first
        create_response = client.post("/api/v1/berths", json=sample_berth_data)
        berth_id = create_response.json()["id"]

        # Get the berth
        response = client.get(f"/api/v1/berths/{berth_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == berth_id
        assert data["berth_number"] == sample_berth_data["berth_number"]

    def test_get_nonexistent_berth(self, client):
        """Test getting non-existent berth"""
        response = client.get("/api/v1/berths/99999")
        assert response.status_code == 404


@pytest.mark.integration
class TestCustomerEndpoints:
    """Test customer management endpoints"""

    def test_list_customers_empty(self, client):
        """Test listing customers when empty"""
        response = client.get("/api/v1/customers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_customer(self, client, sample_customer_data):
        """Test creating a customer"""
        response = client.post("/api/v1/customers", json=sample_customer_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["name"] == sample_customer_data["name"]
        assert data["email"] == sample_customer_data["email"]

    def test_create_duplicate_email(self, client, sample_customer_data):
        """Test creating customer with duplicate email"""
        # Create first customer
        client.post("/api/v1/customers", json=sample_customer_data)

        # Try to create duplicate
        response = client.post("/api/v1/customers", json=sample_customer_data)
        assert response.status_code in [400, 409]  # Bad request or Conflict


@pytest.mark.integration
class TestDashboardEndpoints:
    """Test dashboard endpoints"""

    def test_dashboard_overview(self, client):
        """Test dashboard overview endpoint"""
        response = client.get("/api/v1/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert "berth_stats" in data or "total_berths" in data

    def test_dashboard_occupancy(self, client):
        """Test dashboard occupancy endpoint"""
        response = client.get("/api/v1/dashboard/occupancy")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (dict, list))
