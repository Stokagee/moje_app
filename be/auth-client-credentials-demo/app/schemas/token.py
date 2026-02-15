# Token schemas for Client Credentials Demo

from pydantic import BaseModel, Field


class M2MTokenResponse(BaseModel):
    """Response for successful M2M token request"""
    access_token: str = Field(..., description="JWT access token pro M2M requesty")
    token_type: str = Field(default="bearer", description="Typ tokenu (vždy 'bearer')")
    expires_in: int = Field(..., description="Token expirace v sekundách (3600 = 1 hodina)", examples=[3600])
    scope: str = Field(..., description="Udělené scopes (např. 'read write')")


class ClientCredentialsRequest(BaseModel):
    """Request for client credentials token"""
    grant_type: str = Field(default="client_credentials", description="Musí být 'client_credentials'")
    client_id: str = Field(..., description="ID klientské aplikace", examples=["demo-service"])
    client_secret: str = Field(..., description="Secret klientské aplikace", examples=["demo-secret123"])
    scope: str = Field(default="read", description="Požadované scopes (např. 'read write')")


class TokenIntrospectResponse(BaseModel):
    """Response for token introspection"""
    active: bool = Field(..., description="Je token platný?")
    client_id: str | None = Field(None, description="Client ID z tokenu")
    scopes: str | None = Field(None, description="Scopes udělené tokenu")
    type: str | None = Field(None, description="Typ tokenu (např. 'm2m')")
