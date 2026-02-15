# Authentication routes for Refresh Token Demo

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared"))

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.config import settings
from app.models.user import User, RefreshToken
from app.schemas.token import TokenResponse, RefreshTokenRequest, TokenRefreshResponse, UserResponse
from app.schemas.auth import LoginRequest, RegisterRequest
from shared.logging.logger import get_logger
from shared.logging.formatters import log_auth_event, log_token_issued

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
logger = get_logger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrace nového uživatele",
    description="""Vytvoří nový uživatelský účet.

## Požadavky
- **username**: 3-50 znaků, musí být unikátní
- **email**: Platná emailová adresa, musí být unikátní
- **password**: Minimálně 6 znaků

## Chyby
- **400**: Username nebo email již existuje
- **422**: Neplatná vstupní data (např. příliš krátké heslo)
""",
    responses={
        201: {
            "description": "Účet úspěšně vytvořen",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "newuser",
                        "email": "user@example.com",
                        "is_active": True
                    }
                }
            }
        },
        400: {
            "description": "Username nebo email již existuje",
            "content": {
                "application/json": {
                    "examples": {
                        "username_exists": {
                            "summary": "Username existuje",
                            "value": {"detail": "Username already registered"}
                        },
                        "email_exists": {
                            "summary": "Email existuje",
                            "value": {"detail": "Email already registered"}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validační chyba",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "password"],
                                "msg": "ensure this value has at least 6 characters",
                                "type": "value_error.any_str.min_length"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""

    # Check if username exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        logger.warning("Registration failed: username already exists", extra=log_auth_event(
            event_type="register_failed",
            success=False,
            auth_flow="refresh_token",
            reason="username_exists",
            username=request.username
        ))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        logger.warning("Registration failed: email already exists", extra=log_auth_event(
            event_type="register_failed",
            success=False,
            auth_flow="refresh_token",
            reason="email_exists",
            email=request.email
        ))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("User registered successfully", extra=log_auth_event(
        event_type="register_success",
        success=True,
        auth_flow="refresh_token",
        user_id=user.id,
        username=user.username
    ))

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    tags=["authentication"],
    summary="Přihlásit uživatele",
    description="""Přihlásí uživatele pomocí username a password.

Vrací jak **access token** (platnost 30 minut) tak **refresh token** (platnost 30 dní).

## Token Rotation
Při přihlášení se zneplatní všechny předchozí refresh tokeny tohoto uživatele.
Tím se zabraňuje použití starých tokenů z jiných zařízení.

## Další kroky
1. Použijte access token v `Authorization: Bearer {token}` header
2. Po expiraci access tokenu zavolejte `/refresh` s refresh tokenem
3. Při odhlášení zavolejte `/logout` pro zneplatnění refresh tokenů

## Chyby
- **401 Unauthorized**: Nesprávné username nebo heslo
- **403 Forbidden**: Účet je deaktivován (`is_active=False`)
""",
    responses={
        200: {
            "description": "Úspěšné přihlášení",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y...",
                        "token_type": "bearer",
                        "expires_in": 1800
                    }
                }
            }
        },
        401: {
            "description": "Neplatné credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            }
        },
        403: {
            "description": "Účet deaktivován",
            "content": {
                "application/json": {
                    "example": {"detail": "User account is disabled"}
                }
            }
        }
    }
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username and password.

    Returns both access token (short-lived) and refresh token (long-lived).
    The access token expires in 30 minutes.
    The refresh token expires in 30 days.
    """

    # Find user
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning("Login failed: invalid credentials", extra=log_auth_event(
            event_type="login_failed",
            success=False,
            auth_flow="refresh_token",
            username=request.username,
            reason="invalid_credentials"
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("Login failed: account disabled", extra=log_auth_event(
            event_type="login_failed",
            success=False,
            auth_flow="refresh_token",
            user_id=user.id,
            username=user.username,
            reason="account_disabled"
        ))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Create and store refresh token
    refresh_token_string = create_refresh_token()
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = RefreshToken(
        token=refresh_token_string,
        user_id=user.id,
        expires_at=refresh_token_expires
    )

    db.add(refresh_token)

    # Revoke all old refresh tokens for this user (optional security measure)
    old_tokens_count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False
    ).count()

    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False
    ).update({
        "revoked": True,
        "revoked_at": datetime.utcnow()
    })

    db.commit()

    logger.info("User logged in successfully", extra=log_auth_event(
        event_type="login_success",
        success=True,
        auth_flow="refresh_token",
        user_id=user.id,
        username=user.username
    ))

    logger.info("Access token issued", extra=log_token_issued(
        token_type="access",
        auth_flow="refresh_token",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id
    ))

    logger.info("Refresh token issued", extra=log_token_issued(
        token_type="refresh",
        auth_flow="refresh_token",
        expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        user_id=user.id
    ))

    if old_tokens_count > 0:
        logger.info(f"Revoked {old_tokens_count} old refresh tokens during login", extra=log_auth_event(
            event_type="token_rotation",
            success=True,
            auth_flow="refresh_token",
            user_id=user.id,
            tokens_revoked=old_tokens_count
        ))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_string,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    summary="Obnovit access token",
    description="""Získá nový access token pomocí refresh tokenu.

## Token Rotation
- Starý refresh token je zneplatněn (revoked)
- Vytvoří se nový access token i nový refresh token
- Starý refresh token nelze znovu použít (vrátí 401)

## Kdy použít
- Access token expiroval (obdrželi jste 401)
- Před expirací access tokenu pro proaktivní obnovení

## Chyby
- **401 Unauthorized**: Neplatný nebo expirovaný refresh token
- **401 Unauthorized**: Refresh token byl již použit (rotace)
""",
    responses={
        200: {
            "description": "Token úspěšně obnoven",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y...",
                        "token_type": "bearer",
                        "expires_in": 1800
                    }
                }
            }
        },
        401: {
            "description": "Neplatný refresh token",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid": {
                            "summary": "Neplatný token",
                            "value": {"detail": "Invalid refresh token"}
                        },
                        "expired": {
                            "summary": "Expirovaný token",
                            "value": {"detail": "Refresh token has expired"}
                        },
                        "revoked": {
                            "summary": "Již použitý token (rotace)",
                            "value": {"detail": "Refresh token has been revoked"}
                        }
                    }
                }
            }
        }
    }
)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh an access token using a refresh token.

    This endpoint implements token rotation:
    - The old refresh token is revoked
    - A new refresh token is issued
    - A new access token is issued

    This prevents refresh token reuse and improves security.
    """

    # Find the refresh token in database
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == request.refresh_token
    ).first()

    if not refresh_token:
        logger.warning("Token refresh failed: invalid token", extra=log_auth_event(
            event_type="refresh_failed",
            success=False,
            auth_flow="refresh_token",
            reason="invalid_token"
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Check if token is valid
    if not refresh_token.is_valid:
        if refresh_token.revoked:
            logger.warning("Token refresh failed: token already revoked", extra=log_auth_event(
                event_type="refresh_failed",
                success=False,
                auth_flow="refresh_token",
                user_id=refresh_token.user_id,
                reason="token_revoked"
            ))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )
        else:
            logger.warning("Token refresh failed: token expired", extra=log_auth_event(
                event_type="refresh_failed",
                success=False,
                auth_flow="refresh_token",
                user_id=refresh_token.user_id,
                reason="token_expired"
            ))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )

    # Revoke the old refresh token (rotation)
    refresh_token.revoke()

    # Get user
    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    if not user or not user.is_active:
        logger.warning("Token refresh failed: user not found or inactive", extra=log_auth_event(
            event_type="refresh_failed",
            success=False,
            auth_flow="refresh_token",
            user_id=refresh_token.user_id,
            reason="user_inactive"
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new access token
    new_access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Create new refresh token
    new_refresh_token_string = create_refresh_token()
    new_refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    new_refresh_token = RefreshToken(
        token=new_refresh_token_string,
        user_id=user.id,
        expires_at=new_refresh_token_expires
    )

    db.add(new_refresh_token)
    db.commit()

    logger.info("Token refreshed successfully with rotation", extra=log_auth_event(
        event_type="refresh_success",
        success=True,
        auth_flow="refresh_token",
        user_id=user.id,
        username=user.username
    ))

    logger.info("New access token issued", extra=log_token_issued(
        token_type="access",
        auth_flow="refresh_token",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id
    ))

    logger.info("New refresh token issued", extra=log_token_issued(
        token_type="refresh",
        auth_flow="refresh_token",
        expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        user_id=user.id
    ))

    return TokenRefreshResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token_string,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/logout",
    summary="Odhlásit uživatele",
    description="""Odhlásí uživatele zneplatněním všech refresh tokenů.

## Poznámka
- Access token nelze odvolat (JWT omezení)
- Access token vyexpiruje přirozeně po 30 minutách
- Refresh tokeny jsou zneplatněny okamžitě

## Chyby
- **401 Unauthorized**: Neplatný access token v requestu
""",
    responses={
        200: {
            "description": "Úspěšné odhlášení",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully logged out"}
                }
            }
        },
        401: {
            "description": "Neplatný token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid token"}
                }
            }
        }
    }
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking their refresh tokens.

    Note: The access token cannot be revoked (JWT limitation),
    but it will expire naturally.
    """

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        logger.warning("Logout failed: invalid token", extra=log_auth_event(
            event_type="logout_failed",
            success=False,
            auth_flow="refresh_token",
            reason="invalid_token"
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if user:
        # Revoke all refresh tokens for this user
        revoked_count = db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked == False
        ).count()

        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked == False
        ).update({
            "revoked": True,
            "revoked_at": datetime.utcnow()
        })
        db.commit()

        logger.info("User logged out successfully", extra=log_auth_event(
            event_type="logout_success",
            success=True,
            auth_flow="refresh_token",
            user_id=user.id,
            username=username,
            tokens_revoked=revoked_count
        ))

    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Získat aktuálního uživatele",
    description="""Vrátí informace o aktuálně přihlášeném uživateli.

## Autentizace
Vyžaduje platný access token v `Authorization: Bearer {token}` header.

## Chyby
- **401 Unauthorized**: Neplatný nebo chybějící token
- **403 Forbidden**: Účet je deaktivován
""",
    responses={
        200: {
            "description": "Informace o uživateli",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "testuser",
                        "email": "user@example.com",
                        "is_active": True
                    }
                }
            }
        },
        401: {
            "description": "Neplatný autentizační token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid authentication credentials"}
                }
            }
        },
        403: {
            "description": "Účet je deaktivován",
            "content": {
                "application/json": {
                    "example": {"detail": "User account is disabled"}
                }
            }
        }
    }
)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
