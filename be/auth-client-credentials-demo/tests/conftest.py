"""Pytest fixtures pro Client Credentials Demo."""
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
def m2m_token(client):
    """Získá M2M token pro testy."""
    response = client.post("/oauth2/token", data={
        "grant_type": "client_credentials",
        "client_id": "demo-service",
        "client_secret": "demo-secret123",
        "scope": "read write"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(m2m_token):
    """Vrátí authorization headers s M2M tokenem."""
    return {"Authorization": f"Bearer {m2m_token}"}
