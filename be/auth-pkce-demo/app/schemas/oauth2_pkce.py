# OAuth2 PKCE schemas

from pydantic import BaseModel, Field


class PKCEAuthorizeRequest(BaseModel):
    """Schema for PKCE authorization request"""
    client_id: str = Field(..., description="ID klientské aplikace")
    redirect_uri: str = Field(..., description="Redirect URI po schválení")
    response_type: str = Field(default="code", description="Musí být 'code'")
    scope: str = Field(default="read", description="Požadované scopes")
    state: str = Field(default="", description="Náhodný řetězec pro CSRF ochranu")
    code_challenge: str = Field(..., description="SHA256 hash z code_verifieru")
    code_challenge_method: str = Field(default="S256", description="Hash metoda (vždy S256)")


class PKCEApproveRequest(BaseModel):
    """Schema for PKCE consent approval"""
    client_id: str = Field(..., description="ID klientské aplikace")
    redirect_uri: str = Field(..., description="Redirect URI po schválení")
    state: str = Field(default="", description="State parameter z requestu")
    scopes: str = Field(..., description="Požadované scopes (mezerou oddělené)")
    code_challenge: str = Field(..., description="Code challenge z authorize requestu")
    username: str = Field(..., description="Uživatelské jméno")
    password: str = Field(..., description="Heslo uživatele")


class PKCETokenRequest(BaseModel):
    """
    Schema for PKCE token request.

    KEY DIFFERENCE: No client_secret required!
    Uses code_verifier instead.
    """
    grant_type: str = Field(default="authorization_code", description="Musí být 'authorization_code'")
    code: str = Field(..., description="Authorization code z redirectu")
    client_id: str = Field(..., description="ID klientské aplikace")
    code_verifier: str = Field(..., description="Code verifier (původní náhodná hodnota)")
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


class UserInfoResponse(BaseModel):
    """User info response"""
    sub: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    full_name: str | None = Field(None, description="Full name")


class PKCEDemoResponse(BaseModel):
    """PKCE demo response"""
    code_verifier: str = Field(..., description="Vygenerovaný code verifier")
    code_challenge: str = Field(..., description="Vygenerovaný code challenge")
    code_challenge_method: str = Field(default="S256", description="Hash metoda")
    example_authorize_url: str = Field(..., description="Příklad autorizační URL")
    example_token_request: dict = Field(..., description="Příklad token requestu")
