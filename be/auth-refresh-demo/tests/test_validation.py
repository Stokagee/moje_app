"""Testy pro validaci a chybové scénáře."""
import pytest


class TestTokenValidation:
    """Testy pro validaci tokenů."""

    def test_refresh_with_invalid_token(self, client):
        """Refresh s neplatným tokenem."""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "completely_invalid_token"
        })
        assert response.status_code == 401

    def test_refresh_with_empty_token(self, client):
        """Refresh s prázdným tokenem."""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": ""
        })
        assert response.status_code == 422  # Validation error

    def test_logout_revokes_refresh_tokens(self, client, test_user_data):
        """Ověří, že logout zneplatní refresh tokeny."""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        refresh_token = login.json()["refresh_token"]
        access_token = login.json()["access_token"]

        # Logout
        client.post("/api/v1/auth/logout", headers={
            "Authorization": f"Bearer {access_token}"
        })

        # Try to refresh after logout
        refresh = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh.status_code == 401


class TestInputValidation:
    """Testy pro validaci vstupních dat."""

    def test_register_missing_username(self, client):
        """Registrace bez username."""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@test.com",
            "password": "testpass123"
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Registrace s příliš krátkým heslem."""
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "12345"  # Min 6 chars
        })
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """Registrace s neplatným emailem."""
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "not-an-email",
            "password": "testpass123"
        })
        assert response.status_code == 422

    def test_register_short_username(self, client):
        """Registrace s příliš krátkým username."""
        response = client.post("/api/v1/auth/register", json={
            "username": "ab",  # Min 3 chars
            "email": "test@test.com",
            "password": "testpass123"
        })
        assert response.status_code == 422

    def test_register_duplicate_email(self, client, test_user_data):
        """Registrace s duplicitním emailem."""
        # First registration
        client.post("/api/v1/auth/register", json=test_user_data)

        # Second registration with same email, different username
        response = client.post("/api/v1/auth/register", json={
            "username": "different_user",
            "email": test_user_data["email"],
            "password": "testpass123"
        })
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()
