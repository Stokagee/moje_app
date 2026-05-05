"""Testy pro OAuth2 PKCE autentizaci.

Tento modul testuje:
- JWT token validaci
- Role-based access control
- Scope validation
"""
import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.core.auth import (
    decode_token,
    get_current_user,
    get_current_courier,
    get_current_admin,
    CurrentUser,
    require_scopes
)
from app.core.config import settings


class TestTokenValidation:
    """Test JWT token validace."""

    def test_decode_valid_token(self):
        """Platný token by měl být dekódován."""
        from jose import jwt

        # Vytvořit test token
        payload = {
            "sub": "testuser",
            "user_id": 1,
            "role": "courier",
            "scopes": "orders:read orders:write",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        # Dekódovat
        result = decode_token(token)
        assert result is not None
        assert result["sub"] == "testuser"
        assert result["role"] == "courier"

    def test_decode_expired_token(self):
        """Expirovaný token by měl být odmítnut."""
        from jose import jwt

        payload = {
            "sub": "testuser",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expirovaný
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        result = decode_token(token)
        assert result is None

    def test_decode_invalid_token(self):
        """Nevalidní token by měl být odmítnut."""
        result = decode_token("invalid.token.here")
        assert result is None

    def test_decode_wrong_secret(self):
        """Token podepsaný špatným klíčem by měl být odmítnut."""
        from jose import jwt

        payload = {"sub": "testuser", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, "wrong-secret-key", algorithm=settings.ALGORITHM)

        result = decode_token(token)
        assert result is None


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_valid(self):
        """Platný token by měl vrátit CurrentUser."""
        from jose import jwt

        payload = {
            "sub": "courier1",
            "user_id": 42,
            "role": "courier",
            "scopes": "orders:read orders:write"
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        user = await get_current_user(credentials)

        assert isinstance(user, CurrentUser)
        assert user.username == "courier1"
        assert user.user_id == 42
        assert user.role == "courier"
        assert "orders:read" in user.scopes

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Nevalidní token by měl vyhodit 401."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self):
        """Token bez 'sub' by měl být odmítnut."""
        from jose import jwt

        payload = {"user_id": 1}  # Chybí 'sub'
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        with pytest.raises(HTTPException) as exc:
            await get_current_user(credentials)

        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestRoleBasedAccess:
    """Test role-based access control."""

    @pytest.mark.asyncio
    async def test_get_current_courier_success(self):
        """Courier role by měl projít."""
        user = CurrentUser(username="courier1", user_id=1, role="courier")

        result = await get_current_courier(user)

        assert result.role == "courier"

    @pytest.mark.asyncio
    async def test_get_current_courier_admin_bypass(self):
        """Admin by měl mít přístup ke courier endpointům."""
        user = CurrentUser(username="admin1", user_id=1, role="admin")

        result = await get_current_courier(user)

        assert result.role == "admin"

    @pytest.mark.asyncio
    async def test_get_current_courier_forbidden(self):
        """Customer role by neměl mít přístup k courier endpointům."""
        user = CurrentUser(username="customer1", user_id=1, role="customer")

        with pytest.raises(HTTPException) as exc:
            await get_current_courier(user)

        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Courier role required" in exc.value.detail

    @pytest.mark.asyncio
    async def test_get_current_admin_success(self):
        """Admin role by měl projít."""
        user = CurrentUser(username="admin1", user_id=1, role="admin")

        result = await get_current_admin(user)

        assert result.role == "admin"

    @pytest.mark.asyncio
    async def test_get_current_admin_forbidden(self):
        """Courier role by neměl mít přístup k admin endpointům."""
        user = CurrentUser(username="courier1", user_id=1, role="courier")

        with pytest.raises(HTTPException) as exc:
            await get_current_admin(user)

        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin role required" in exc.value.detail


class TestScopeValidation:
    """Test OAuth2 scope validace."""

    @pytest.mark.asyncio
    async def test_require_scopes_success(self):
        """Token se správnými scopes by měl projít."""
        user = CurrentUser(
            username="user1",
            user_id=1,
            scopes=["orders:read", "orders:write"],
            role="courier"
        )

        checker = require_scopes(["orders:read"])
        result = await checker(user)

        assert result == user

    @pytest.mark.asyncio
    async def test_require_scopes_missing(self):
        """Token bez požadovaného scope by měl být odmítnut."""
        user = CurrentUser(
            username="user1",
            user_id=1,
            scopes=["orders:read"],  # Chybí orders:write
            role="courier"
        )

        checker = require_scopes(["orders:write"])

        with pytest.raises(HTTPException) as exc:
            await checker(user)

        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Missing required scope" in exc.value.detail

    @pytest.mark.asyncio
    async def test_require_multiple_scopes(self):
        """Token s více scopes by měl projít."""
        user = CurrentUser(
            username="user1",
            user_id=1,
            scopes=["orders:read", "orders:write", "orders:admin"],
            role="admin"
        )

        checker = require_scopes(["orders:read", "orders:write"])
        result = await checker(user)

        assert result == user
