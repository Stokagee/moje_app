# Protected API routes for Client Credentials Demo

from fastapi import APIRouter, Depends
from app.models.oauth2_client import OAuth2Client
from app.routes.oauth2 import get_m2m_client, require_scopes

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get(
    "/data",
    summary="Veřejná data (bez autentizace)",
    description="""Vrátí veřejná data, která nevyžadují autentizaci.

Tento endpoint může být volán bez tokenu.
""",
    responses={
        200: {
            "description": "Veřejná data",
            "content": {
                "application/json": {
                    "example": {
                        "message": "This is public data",
                        "data": ["item1", "item2", "item3"]
                    }
                }
            }
        }
    }
)
def get_public_data():
    """Public endpoint - no authentication required"""
    return {
        "message": "This is public data",
        "data": ["item1", "item2", "item3"]
    }


@router.get(
    "/secure/data",
    summary="Chráněná data (vyžaduje 'read' scope)",
    description="""Vrátí chráněná data, která vyžadují `read` scope.

## Autentizace
- Vyžaduje platný M2M token v `Authorization: Bearer {token}` header
- Token musí mít `read` scope

## Chyby
- **403**: Chybějící nebo neplatný token
- **403**: Token nemá požadovaný `read` scope
""",
    responses={
        200: {
            "description": "Chráněná data",
            "content": {
                "application/json": {
                    "example": {
                        "message": "This is secure data (read access)",
                        "client": "Demo Service",
                        "data": {
                            "id": 1,
                            "name": "Secure Resource",
                            "value": "Sensitive information"
                        }
                    }
                }
            }
        },
        403: {
            "description": "Chybějící autentizace nebo insufficient scope",
            "content": {
                "application/json": {
                    "examples": {
                        "no_token": {
                            "summary": "Chybějící token",
                            "value": {"detail": "Not authenticated"}
                        },
                        "no_scope": {
                            "summary": "Insufficient scope",
                            "value": {"detail": "Insufficient scope. Required: read"}
                        }
                    }
                }
            }
        }
    }
)
def get_secure_data(client: OAuth2Client = Depends(require_scopes(["read"]))):
    """
    Protected endpoint - requires 'read' scope

    This demonstrates how to protect an endpoint that requires
    specific scopes.
    """
    return {
        "message": "This is secure data (read access)",
        "client": client.name,
        "data": {
            "id": 1,
            "name": "Secure Resource",
            "value": "Sensitive information"
        }
    }


@router.post(
    "/secure/data",
    summary="Vytvořit chráněná data (vyžaduje 'write' scope)",
    description="""Vytvoří nová chráněná data.

## Autentizace
- Vyžaduje platný M2M token
- Token musí mít `write` scope

## Chyby
- **403**: Chybějící autentizace nebo insufficient scope
""",
    responses={
        200: {
            "description": "Data úspěšně vytvořena",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Data created successfully",
                        "client": "Demo Service",
                        "created_data": {"key": "value"}
                    }
                }
            }
        },
        403: {
            "description": "Chybějící autentizace nebo insufficient scope",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient scope. Required: write"}
                }
            }
        }
    }
)
def create_secure_data(
    data: dict,
    client: OAuth2Client = Depends(require_scopes(["write"]))
):
    """
    Protected endpoint - requires 'write' scope

    This demonstrates how to protect an endpoint that creates data.
    """
    return {
        "message": "Data created successfully",
        "client": client.name,
        "created_data": data
    }


@router.delete(
    "/secure/data/{data_id}",
    summary="Smazat chráněná data (vyžaduje 'delete' scope)",
    description="""Smaže chráněná data podle ID.

## Autentizace
- Vyžaduje platný M2M token
- Token musí mít `delete` scope

## Parametry
- `data_id`: ID dat k smazání
""",
    responses={
        200: {
            "description": "Data úspěšně smazána",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Data 123 deleted successfully",
                        "client": "Demo Service"
                    }
                }
            }
        },
        403: {
            "description": "Chybějící autentizace nebo insufficient scope",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient scope. Required: delete"}
                }
            }
        }
    }
)
def delete_secure_data(
    data_id: int,
    client: OAuth2Client = Depends(require_scopes(["delete"]))
):
    """
    Protected endpoint - requires 'delete' scope

    This demonstrates how to protect an endpoint that deletes data.
    """
    return {
        "message": f"Data {data_id} deleted successfully",
        "client": client.name
    }


@router.get(
    "/secure/admin",
    summary="Admin data (vyžaduje 'admin' scope)",
    description="""Vrátí admin data, která vyžadují `admin` scope.

## Autentizace
- Vyžaduje platný M2M token
- Token musí mít `admin` scope

## Demo Poznámka
Demo client nemá `admin` scope. Pro testování tohoto endpointu
musíte vytvořit nového clienta s `admin` scope.
""",
    responses={
        200: {
            "description": "Admin data",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Admin data accessed",
                        "client": "Admin Service",
                        "admin_info": {
                            "total_clients": 5,
                            "active_tokens": 12,
                            "server_status": "running"
                        }
                    }
                }
            }
        },
        403: {
            "description": "Chybějící autentizace nebo insufficient scope",
            "content": {
                "application/json": {
                    "example": {"detail": "Insufficient scope. Required: admin"}
                }
            }
        }
    }
)
def admin_data(client: OAuth2Client = Depends(require_scopes(["admin"]))):
    """
    Protected endpoint - requires 'admin' scope

    This demonstrates how to protect an admin endpoint.
    """
    return {
        "message": "Admin data accessed",
        "client": client.name,
        "admin_info": {
            "total_clients": 5,
            "active_tokens": 12,
            "server_status": "running"
        }
    }


@router.get(
    "/whoami",
    summary="Informace o autentizovaném clientovi",
    description="""Vrátí informace o autentizovaném M2M clientovi.

## Autentizace
- Vyžaduje platný M2M token

## Použití
Užitečné pro debugging a testování autentizace.
""",
    responses={
        200: {
            "description": "Informace o clientovi",
            "content": {
                "application/json": {
                    "example": {
                        "client_id": "demo-service",
                        "name": "Demo Service",
                        "description": "Demo service account for testing Client Credentials flow",
                        "scopes": "read write",
                        "is_active": True
                    }
                }
            }
        },
        401: {
            "description": "Neplatný token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid authentication credentials"}
                }
            }
        }
    }
)
def whoami(client: OAuth2Client = Depends(get_m2m_client)):
    """
    Returns information about the authenticated client.

    Useful for debugging and testing.
    """
    return {
        "client_id": client.client_id,
        "name": client.name,
        "description": client.description,
        "scopes": client.scopes,
        "is_active": client.is_active
    }
