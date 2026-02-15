"""Testy pro kompletní autentizační flow."""
import pytest


class TestRefreshTokenFlow:
    """Testy pro kompletní refresh token cyklus."""

    def test_complete_flow(self, client, test_user_data):
        """Register → Login → Use Token → Refresh → Logout."""
        # 1. Register
        register = client.post("/api/v1/auth/register", json=test_user_data)
        assert register.status_code == 201

        # 2. Login
        login = client.post("/api/v1/auth/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert login.status_code == 200
        tokens = login.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] == 1800

        # 3. Use access token
        me = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {tokens['access_token']}"
        })
        assert me.status_code == 200
        assert me.json()["username"] == test_user_data["username"]

        # 4. Refresh token
        refresh = client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        assert refresh.status_code == 200
        new_tokens = refresh.json()
        assert new_tokens["access_token"] != tokens["access_token"]
        assert new_tokens["refresh_token"] != tokens["refresh_token"]

        # 5. Starý refresh token by měl být neplatný (rotace)
        old_refresh = client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        assert old_refresh.status_code == 401

        # 6. Logout
        logout = client.post("/api/v1/auth/logout", headers={
            "Authorization": f"Bearer {new_tokens['access_token']}"
        })
        assert logout.status_code == 200

    def test_login_then_refresh_without_login(self, client):
        """Refresh bez předchozího loginu by měl selhat."""
        refresh = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        assert refresh.status_code == 401


class TestAuthentication:
    """Testy pro autentizační endpointy."""

    def test_register_new_user(self, client, test_user_data):
        """Registrace nového uživatele."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        user = response.json()
        assert user["username"] == test_user_data["username"]
        assert user["email"] == test_user_data["email"]
        assert "id" in user

    def test_register_duplicate_username(self, client, registered_user):
        """Registrace s duplicitním username."""
        response = client.post("/api/v1/auth/register", json=registered_user)
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_login_success(self, client, registered_user):
        """Úspěšný login."""
        response = client.post("/api/v1/auth/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    def test_login_invalid_password(self, client, registered_user):
        """Login s neplatným heslem."""
        response = client.post("/api/v1/auth/login", json={
            "username": registered_user["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Login neexistujícího uživatele."""
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        assert response.status_code == 401

    def test_get_me_with_token(self, client, registered_user):
        """Získání uživatelských dat s platným tokenem."""
        login = client.post("/api/v1/auth/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        token = login.json()["access_token"]

        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        assert response.json()["username"] == registered_user["username"]

    def test_get_me_without_token(self, client):
        """Získání uživatelských dat bez tokenu."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # No authorization header

    def test_get_me_with_invalid_token(self, client):
        """Získání uživatelských dat s neplatným tokenem."""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401
