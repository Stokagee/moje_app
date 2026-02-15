"""Testy pro M2M autentizaci."""
import pytest


class TestClientCredentialsFlow:
    """Testy pro Client Credentials flow."""

    def test_get_m2m_token_success(self, client):
        """Úspěšné získání M2M tokenu."""
        response = client.post("/oauth2/token", data={
            "grant_type": "client_credentials",
            "client_id": "demo-service",
            "client_secret": "demo-secret123",
            "scope": "read write"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600
        assert "read" in data["scope"]
        assert "write" in data["scope"]

    def test_get_m2m_token_invalid_credentials(self, client):
        """Neplatné client credentials."""
        response = client.post("/oauth2/token", data={
            "grant_type": "client_credentials",
            "client_id": "wrong-id",
            "client_secret": "wrong-secret",
            "scope": "read"
        })
        assert response.status_code == 401

    def test_get_m2m_token_invalid_grant_type(self, client):
        """Nepodporovaný grant_type."""
        response = client.post("/oauth2/token", data={
            "grant_type": "password",
            "client_id": "demo-service",
            "client_secret": "demo-secret123"
        })
        assert response.status_code == 400
        assert "Unsupported grant_type" in response.json()["detail"]

    def test_use_m2m_token_for_protected_endpoint(self, client, auth_headers):
        """Použití M2M tokenu pro chráněný endpoint."""
        response = client.get("/api/v1/secure/data", headers=auth_headers)
        assert response.status_code == 200
        assert "data" in response.json()

    def test_protected_endpoint_without_token(self, client):
        """Chráněný endpoint bez tokenu."""
        response = client.get("/api/v1/secure/data")
        assert response.status_code == 403

    def test_protected_endpoint_with_invalid_token(self, client):
        """Chráněný endpoint s neplatným tokenem."""
        response = client.get("/api/v1/secure/data", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401

    def test_public_endpoint_no_auth_required(self, client):
        """Public endpoint nevyžaduje autentizaci."""
        response = client.get("/api/v1/data")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_whoami_with_valid_token(self, client, m2m_token):
        """Whoami endpoint s platným tokenem."""
        response = client.get("/api/v1/whoami", headers={
            "Authorization": f"Bearer {m2m_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == "demo-service"
        assert data["name"] == "Demo Service"


class TestScopeValidation:
    """Testy pro scope validaci."""

    def test_access_with_valid_scope(self, client, m2m_token):
        """Přístup s platným scope."""
        response = client.get("/api/v1/secure/data", headers={
            "Authorization": f"Bearer {m2m_token}"
        })
        assert response.status_code == 200

    def test_access_without_required_scope(self, client):
        """Přístup bez požadovaného scope."""
        # Get token only with read scope
        token_response = client.post("/oauth2/token", data={
            "grant_type": "client_credentials",
            "client_id": "demo-service",
            "client_secret": "demo-secret123",
            "scope": "read"  # Only read, not write
        })
        token = token_response.json()["access_token"]

        # Try to access write endpoint
        response = client.post("/api/v1/secure/data",
            json={"test": "data"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "Insufficient scope" in response.json()["detail"]


class TestTokenIntrospection:
    """Testy pro introspekci tokenu."""

    def test_introspect_active_token(self, client, m2m_token):
        """Introspekce platného tokenu."""
        response = client.post("/oauth2/introspect", json={
            "token": m2m_token
        })
        assert response.status_code == 200
        data = response.json()
        assert data["active"] is True
        assert data["client_id"] == "demo-service"

    def test_introspect_invalid_token(self, client):
        """Introspekce neplatného tokenu."""
        response = client.post("/oauth2/introspect", json={
            "token": "invalid_token"
        })
        assert response.status_code == 200
        assert response.json()["active"] is False
