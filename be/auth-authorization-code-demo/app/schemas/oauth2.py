# OAuth2 schemas for Authorization Code Demo

from pydantic import BaseModel, Field


class AuthorizeRequest(BaseModel):
    """Schema for authorization request"""
    client_id: str = Field(..., description="ID klientské aplikace")
    redirect_uri: str = Field(..., description="Redirect URI po schválení")
    response_type: str = Field(default="code", description="Musí být 'code'")
    scope: str = Field(default="read", description="Požadované scopes")
    state: str = Field(default="", description="Náhodný řetězec pro CSRF ochranu")


class ApproveRequest(BaseModel):
    """Schema for consent approval"""
    client_id: str = Field(..., description="ID klientské aplikace")
    redirect_uri: str = Field(..., description="Redirect URI po schválení")
    state: str = Field(default="", description="State parameter z requestu")
    scopes: str = Field(..., description="Požadované scopes (mezerou oddělené)")
    username: str = Field(..., description="Uživatelské jméno")
    password: str = Field(..., description="Heslo uživatele")


class TokenRequest(BaseModel):
    """Schema for token request"""
    grant_type: str = Field(default="authorization_code", description="Musí být 'authorization_code'")
    code: str = Field(..., description="Authorization code z redirectu")
    client_id: str = Field(..., description="ID klientské aplikace")
    client_secret: str = Field(..., description="Secret klientské aplikace")
    redirect_uri: str = Field(..., description="Stejná redirect URI jako v authorize requestu")


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Typ tokenu (vždy 'bearer')")
    expires_in: int = Field(..., description="Expirace v sekundách")
    scope: str = Field(..., description="Udělené scopes")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Chybový kód")
    error_description: str | None = Field(None, description="Popis chyby")
