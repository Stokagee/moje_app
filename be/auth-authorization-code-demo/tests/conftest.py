"""Pytest fixtures pro Authorization Code Demo."""
import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from app.core.database import SessionLocal


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
def demo_client_credentials():
    """Demo OAuth2 client credentials."""
    return {
        "client_id": "demo-client",
        "client_secret": "demo-client-secret",
        "redirect_uri": "http://localhost:3000/callback"
    }


@pytest.fixture
def demo_user_credentials():
    """Demo user credentials."""
    return {
        "username": "demo",
        "password": "demo123"
    }
