# Integration tests for PKCE Flow

import pytest
from fastapi.testclient import TestClient
from app.utils.pkce_helpers import generate_code_verifier, create_code_challenge, verify_code_verifier


class TestPKCEFlow:
    """Test complete PKCE flow"""

    def test_pkce_helpers(self):
        """Test PKCE helper functions"""
        # Generate verifier
        verifier = generate_code_verifier()
        assert len(verifier) >= 43
        assert len(verifier) <= 128

        # Create challenge
        challenge = create_code_challenge(verifier)
        assert len(challenge) > 0

        # Verify
        assert verify_code_verifier(verifier, challenge) is True
        assert verify_code_verifier("wrong", challenge) is False

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "pkce_info" in data
        assert data["message"] == "OAuth2 PKCE Flow Demo API"

    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_pkce_demo_endpoint(self, client: TestClient):
        """Test PKCE demo endpoint"""
        response = client.get("/oauth2/pkce/demo")
        assert response.status_code == 200
        data = response.json()
        assert "code_verifier" in data
        assert "code_challenge" in data
        assert "example_authorize_url" in data
        assert "example_token_request" in data

    def test_authorize_endpoint_missing_challenge(self, client: TestClient):
        """Test that authorize endpoint requires code_challenge"""
        response = client.get("/oauth2/authorize", params={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code"
        })
        # Should fail without code_challenge
        assert response.status_code in [400, 422]

    def test_authorize_endpoint_with_challenge(self, client: TestClient):
        """Test authorize endpoint with code_challenge"""
        verifier = generate_code_verifier()
        challenge = create_code_challenge(verifier)

        response = client.get("/oauth2/authorize", params={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code",
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        })
        # Should return HTML consent page
        assert response.status_code == 200

    def test_authorize_endpoint_rejects_plain_method(self, client: TestClient):
        """Test that authorize endpoint rejects 'plain' challenge method"""
        verifier = generate_code_verifier()

        response = client.get("/oauth2/authorize", params={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code",
            "code_challenge": verifier,
            "code_challenge_method": "plain"  # Should be rejected
        })
        # Should reject 'plain' method
        assert response.status_code == 400

    def test_complete_pkce_flow(self, client: TestClient):
        """Test complete PKCE flow from authorize to token"""

        # Step 1: Generate PKCE pair
        verifier = generate_code_verifier()
        challenge = create_code_challenge(verifier)

        # Step 2: Authorize request
        auth_response = client.get("/oauth2/authorize", params={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "response_type": "code",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": "read"
        })
        assert auth_response.status_code == 200

        # Step 3: Approve consent
        approve_response = client.post("/oauth2/approve", data={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "code_challenge": challenge,
            "username": "demo",
            "password": "demo123",
            "scopes": "read"
        })
        assert approve_response.status_code == 302
        redirect_url = approve_response.headers.get("location")
        assert "code=" in redirect_url

        # Extract authorization code from redirect
        auth_code = redirect_url.split("code=")[1].split("&")[0]

        # Step 4: Exchange code for token with code_verifier
        token_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": "pkce-test-client",
            "code_verifier": verifier,
            "redirect_uri": "http://localhost:3000/callback"
        })
        assert token_response.status_code == 200
        token_data = token_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        # Step 5: Use token to get userinfo
        userinfo_response = client.get("/oauth2/userinfo", headers={
            "Authorization": f"Bearer {token_data['access_token']}"
        })
        assert userinfo_response.status_code == 200
        userinfo = userinfo_response.json()
        assert userinfo["username"] == "demo"

    def test_token_endpoint_rejects_wrong_verifier(self, client: TestClient):
        """Test that token endpoint rejects wrong code_verifier"""
        verifier = generate_code_verifier()
        challenge = create_code_challenge(verifier)

        # Get authorization code
        client.get("/oauth2/authorize", params={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        })

        approve_response = client.post("/oauth2/approve", data={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "code_challenge": challenge,
            "username": "demo",
            "password": "demo123",
            "scopes": "read"
        })
        redirect_url = approve_response.headers.get("location")
        auth_code = redirect_url.split("code=")[1].split("&")[0]

        # Try to exchange with wrong verifier
        wrong_verifier = generate_code_verifier()
        token_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": "pkce-test-client",
            "code_verifier": wrong_verifier,
            "redirect_uri": "http://localhost:3000/callback"
        })
        assert token_response.status_code == 400

    def test_token_is_single_use(self, client: TestClient):
        """Test that authorization code can only be used once"""
        verifier = generate_code_verifier()
        challenge = create_code_challenge(verifier)

        # Get authorization code
        client.get("/oauth2/authorize", params={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "code_challenge": challenge,
            "code_challenge_method": "S256"
        })

        approve_response = client.post("/oauth2/approve", data={
            "client_id": "pkce-test-client",
            "redirect_uri": "http://localhost:3000/callback",
            "code_challenge": challenge,
            "username": "demo",
            "password": "demo123",
            "scopes": "read"
        })
        redirect_url = approve_response.headers.get("location")
        auth_code = redirect_url.split("code=")[1].split("&")[0]

        # First use should succeed
        first_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": "pkce-test-client",
            "code_verifier": verifier,
            "redirect_uri": "http://localhost:3000/callback"
        })
        assert first_response.status_code == 200

        # Second use should fail
        second_response = client.post("/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": "pkce-test-client",
            "code_verifier": verifier,
            "redirect_uri": "http://localhost:3000/callback"
        })
        assert second_response.status_code == 400
