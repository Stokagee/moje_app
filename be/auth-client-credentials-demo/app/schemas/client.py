# Client schemas for Client Credentials Demo

from pydantic import BaseModel, Field


class ClientCreate(BaseModel):
    """Schema for creating a new OAuth2 client"""
    client_id: str = Field(..., min_length=3, max_length=50, description="Unikátní ID klientské aplikace")
    client_secret: str = Field(..., min_length=8, description="Secret klientské aplikace (min 8 znaků)")
    name: str = Field(..., min_length=3, max_length=100, description="Jméno klientské aplikace")
    description: str | None = Field(None, description="Popis klientské aplikace")
    scopes: str = Field(default="read", description="Scopes přiřazené klientovi (např. 'read write')")


class ClientResponse(BaseModel):
    """OAuth2 client response"""
    id: int = Field(..., description="Unikátní ID klienta")
    client_id: str = Field(..., description="Client ID")
    name: str = Field(..., description="Jméno klienta")
    description: str | None = Field(None, description="Popis klienta")
    scopes: str = Field(..., description="Scopes přiřazené klientovi")
    is_active: bool = Field(..., description="Je klient aktivní?")

    class Config:
        from_attributes = True
