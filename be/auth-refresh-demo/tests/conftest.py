"""Pytest fixtures pro Refresh Token Demo."""
import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from app.core.database import SessionLocal, Base, engine
import secrets


def get_test_db():
    """Vrátí testovací database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """FastAPI TestClient s override database."""
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def unique_username():
    """Generuje unikátní username pro každý test."""
    return f"user_{secrets.token_hex(4)}"


@pytest.fixture
def unique_email():
    """Generuje unikátní email pro každý test."""
    return f"user_{secrets.token_hex(4)}@test.com"


@pytest.fixture
def test_user_data(unique_username, unique_email):
    """Vzorová data pro vytvoření uživatele."""
    return {
        "username": unique_username,
        "email": unique_email,
        "password": "testpass123"
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Vytvoří registrovaného uživatele a vrátí jeho data."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return test_user_data
