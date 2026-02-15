"""Testy pro Authorization Code flow."""
import pytest
from urllib.parse import parse_qs, urlparse


class TestAuthorizationCodeFlow:
    """Testy pro kompletní OAuth2 Authorization Code flow."""

    def test_authorize_shows_consent_page(self, client, demo_client_credentials):
        """Authorize endpoint zobrazí consent stránku."""
        state = "test-state-123"

        response = client.get("/oauth2/authorize", params={
            "client_id": demo_client_credentials["client_id"],
            "redirect_uri": demo_client_credentials["redirect_uri"],
            "response_type": "code",
            "scope": "read write",
            "state": state
        })
        assert response.status_code == 200
        # Should be HTML with consent form
        assert "text/html" in response.headers["content-type"]
        assert "consent" in response.text.lower() or "authorize" in response.text.lower()

    def test_authorize_invalid_client_id(self, client):
        """Authorize s neplatným client_id."""
        response = client.get("/oauth2/authorize", params={
            "client_id": "invalid-client",
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code"
        })
        assert response.status_code == 400
        assert "client_id" in response.json()["detail"].lower()

    def test_authorize_invalid_redirect_uri(self, client):
        """Authorize s neplatnou redirect URI."""
        response = client.get("/oauth2/authorize", params={
            "client_id": "demo-client",
            "redirect_uri": "http://evil.com/callback",
            "response_type": "code"
        })
        assert response.status_code == 400
        assert "redirect_uri" in response.json()["detail"].lower()

    def test_authorize_unsupported_response_type(self, client):
        """Authorize s nepodporovaným response_type."""
        response = client.get("/oauth2/authorize", params={
            "client_id": "demo-client",
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "token"  # Should be "code"
        })
        assert response.status_code == 400

    def test_approve_consent_returns_code(self, client, demo_client_credentials):
        """Schválení consentu vrátí authorization code."""
        state = "test-state-xyz"

        # Approve consent
        response = client.post("/oauth2/approve", data={
            "client_id": demo_client_credentials["client_id"],
            "redirect_uri": demo_client_credentials["redirect_uri"],
            "state": state,
            "scopes": "read write",
            "username": "demo",
            "password": "demo123"
        }, allow_redirects=False)

        # Should redirect with code
        assert response.status_code == 302
        location = response.headers["location"]
        assert "code=" in location
        assert f"state={state}" in location

        # Extract code from location
        parsed = urlparse(location)
        params = parse_qs(parsed.query)
        assert "code" in params
        auth_code = params["code"][0]

        return auth_code

    def test_token_exchange_with_code(self, client, demo_client_credentials):
        """Výměna authorization code za access token."""
        # First get a code
        state = "test-state"
        approve_response = client.post("/oauth2/approve", data={
            "client_id": demo_client_credentials["client_id"],
            "redirect_uri": demo_client_credentials["redirect_uri"],
            "state": state,
            "scopes": "read",
            "username": "demo",
            "password": "demo123"
        }, allow_redirects=False)

        location = approve_response.headers["location"]
        parsed = urlparse(location)
        code = parse_qs(parsed.query)["code"][0]

        # Exchange code for token
        token_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": demo_client_credentials["client_id"],
            "client_secret": demo_client_credentials["client_secret"],
            "redirect_uri": demo_client_credentials["redirect_uri"]
        })

        assert token_response.status_code == 200
        data = token_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "read" in data["scope"]

    def test_code_is_single_use(self, client, demo_client_credentials):
        """Authorization code lze použít jen jednou."""
        # Get a code
        approve_response = client.post("/oauth2/approve", data={
            "client_id": demo_client_credentials["client_id"],
            "redirect_uri": demo_client_credentials["redirect_uri"],
            "state": "state",
            "scopes": "read",
            "username": "demo",
            "password": "demo123"
        }, allow_redirects=False)

        location = approve_response.headers["location"]
        parsed = urlparse(location)
        code = parse_qs(parsed.query)["code"][0]

        # First use - should succeed
        first_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": demo_client_credentials["client_id"],
            "client_secret": demo_client_credentials["client_secret"],
            "redirect_uri": demo_client_credentials["redirect_uri"]
        })
        assert first_response.status_code == 200

        # Second use - should fail
        second_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": demo_client_credentials["client_id"],
            "client_secret": demo_client_credentials["client_secret"],
            "redirect_uri": demo_client_credentials["redirect_uri"]
        })
        assert second_response.status_code == 400
        assert "code" in second_response.json()["detail"].lower()

    def test_token_exchange_with_invalid_code(self, client, demo_client_credentials):
        """Výměna s neplatným code."""
        response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": "invalid_code_12345",
            "client_id": demo_client_credentials["client_id"],
            "client_secret": demo_client_credentials["client_secret"],
            "redirect_uri": demo_client_credentials["redirect_uri"]
        })
        assert response.status_code == 400

    def test_token_exchange_with_wrong_secret(self, client, demo_client_credentials):
        """Výměna se špatným client_secret."""
        # Get a valid code first
        approve_response = client.post("/oauth2/approve", data={
            "client_id": demo_client_credentials["client_id"],
            "redirect_uri": demo_client_credentials["redirect_uri"],
            "state": "state",
            "scopes": "read",
            "username": "demo",
            "password": "demo123"
        }, allow_redirects=False)

        location = approve_response.headers["location"]
        parsed = urlparse(location)
        code = parse_qs(parsed.query)["code"][0]

        # Try to exchange with wrong secret
        response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": demo_client_credentials["client_id"],
            "client_secret": "wrong_secret",
            "redirect_uri": demo_client_credentials["redirect_uri"]
        })
        assert response.status_code == 401

    def test_userinfo_with_valid_token(self, client, demo_client_credentials):
        """Získání user info s platným tokenem."""
        # Get token through full flow
        approve_response = client.post("/oauth2/approve", data={
            "client_id": demo_client_credentials["client_id"],
            "redirect_uri": demo_client_credentials["redirect_uri"],
            "state": "state",
            "scopes": "read",
            "username": "demo",
            "password": "demo123"
        }, allow_redirects=False)

        location = approve_response.headers["location"]
        parsed = urlparse(location)
        code = parse_qs(parsed.query)["code"][0]

        token_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": demo_client_credentials["client_id"],
            "client_secret": demo_client_credentials["client_secret"],
            "redirect_uri": demo_client_credentials["redirect_uri"]
        })

        token = token_response.json()["access_token"]

        # Get userinfo
        userinfo_response = client.get("/oauth2/userinfo", params={
            "token": token
        })
        assert userinfo_response.status_code == 200
        userinfo = userinfo_response.json()
        assert userinfo["username"] == "demo"
        assert "email" in userinfo

    def test_userinfo_with_invalid_token(self, client):
        """Získání user info s neplatným tokenem."""
        response = client.get("/oauth2/userinfo", params={
            "token": "invalid_token"
        })
        assert response.status_code == 401
