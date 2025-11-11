"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Test database URL (use in-memory SQLite for tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_berth_data():
    """Sample berth data for testing"""
    return {
        "berth_number": "A-01",
        "section": "A",
        "length_meters": 12.0,
        "width_meters": 4.0,
        "depth_meters": 3.0,
        "has_electricity": True,
        "has_water": True,
        "electricity_voltage": 220,
        "has_wifi": True,
        "status": "available",
        "daily_rate_eur": 45.0
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "name": "Test Customer",
        "email": "test@example.com",
        "phone": "+90 532 123 4567",
        "tc_kimlik": "12345678901",
        "city": "Istanbul",
        "country": "Turkey",
        "preferred_language": "tr"
    }


@pytest.fixture
def sample_vessel_data():
    """Sample vessel data for testing"""
    return {
        "customer_id": 1,
        "name": "Test Vessel",
        "registration_number": "TEST-001",
        "flag_country": "Turkey",
        "vessel_type": "sailboat",
        "length_meters": 12.0,
        "width_meters": 4.0,
        "draft_meters": 2.0
    }
