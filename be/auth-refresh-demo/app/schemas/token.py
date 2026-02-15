# Token schemas for Refresh Token Demo

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Response containing both access and refresh tokens"""
    access_token: str = Field(..., description="JWT access token pro API requesty (platnost 30 minut)")
    refresh_token: str = Field(..., description="Refresh token pro získání nového access tokenu (platnost 30 dní)")
    token_type: str = Field(default="bearer", description="Typ tokenu (vždy 'bearer')")
    expires_in: int = Field(..., description="Access token expirace v sekundách (1800 = 30 minut)", examples=[1800])


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token"""
    refresh_token: str = Field(..., description="Platný refresh token získaný při loginu", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])


class TokenRefreshResponse(BaseModel):
    """Response after successful token refresh"""
    access_token: str = Field(..., description="Nový JWT access token")
    refresh_token: str = Field(..., description="Nový refresh token (starý byl zneplatněn)")
    token_type: str = Field(default="bearer", description="Typ tokenu (vždy 'bearer')")
    expires_in: int = Field(..., description="Access token expirace v sekundách", examples=[1800])


class UserResponse(BaseModel):
    """User information response"""
    id: int = Field(..., description="Unikátní ID uživatele")
    username: str = Field(..., description="Uživatelské jméno", examples=["testuser"])
    email: str = Field(..., description="Emailová adresa", examples=["user@example.com"])
    is_active: bool = Field(..., description="Je účet aktivní?", examples=[True])

    class Config:
        from_attributes = True
