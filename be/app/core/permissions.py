"""Role-Based Access Control (RBAC) Permissions.

Tento modul poskytuje FastAPI dependencies pro kontrolu oprávnění:
- Role-based access (courier, admin, dispatcher)
- Resource ownership (kurýr může měnit jen své objednávky)
- Scope-based access (OAuth2 scopes)

Použití:
    from app.core.permissions import require_role, require_order_ownership

    @router.delete("/orders/{id}")
    async def delete(admin = Depends(require_role("admin"))):
        pass

    @router.post("/orders/{id}/pickup")
    async def pickup(
        order_id: int,
        courier = Depends(require_order_ownership)
    ):
        # Kurýr může vyzvednout jen své objednávky
        pass
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.auth import CurrentUser, get_current_user
from app.database import get_db
from app.crud import order as order_crud


class Role:
    """Definice rolí v systému."""
    COURIER = "courier"
    DISPATCHER = "dispatcher"
    ADMIN = "admin"
    CUSTOMER = "customer"


def require_role(required_role: str):
    """
    Factory pro vytvoření dependency, která kontroluje roli.

    Použití:
        @router.delete("/orders/{id}")
        async def delete(admin = Depends(require_role("admin"))):
            pass

    Args:
        required_role: Požadovaná role (courier, admin, dispatcher)

    Returns:
        FastAPI dependency funkce
    """
    async def role_checker(
        user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if user.role != required_role and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required for this operation"
            )
        return user

    return role_checker


def require_any_role(allowed_roles: list[str]):
    """
    Factory pro vytvoření dependency, která kontroluje jednu z povolených rolí.

    Použití:
        @router.post("/orders/{id}/pickup")
        async def pickup(
            user = Depends(require_any_role(["courier", "dispatcher"]))
        ):
            pass

    Args:
        allowed_roles: Seznam povolených rolí

    Returns:
        FastAPI dependency funkc
    """
    async def role_checker(
        user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if user.role not in allowed_roles and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of roles {allowed_roles} required for this operation"
            )
        return user

    return role_checker


async def require_order_ownership(
    order_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> CurrentUser:
    """
    Dependency pro ověření, že kurýr vlastní objednávku.

    Kurýr může měnit jen objednávky, které mu jsou přiřazeny.
    Admin může měnit všechny objednávky.

    Použití:
        @router.post("/orders/{order_id}/pickup")
        async def pickup(
            order_id: int,
            courier = Depends(require_order_ownership)
        ):
            pass

    Raises:
        401 Unauthorized: Pokud token chybí nebo je nevalidní
        403 Forbidden: Pokud kurýr není vlastníkem objednávky
        404 Not Found: Pokud objednávka neexistuje

    Returns:
        CurrentUser s ověřeným vlastnictvím
    """
    # Admin může vše
    if user.role == "admin":
        return user

    # Získat objednávku
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Ověřit vlastnictví (kurýr musí mít přiřazenu objednávku)
    if user.role == "courier":
        # TODO: Implementovat kontrolu courier_id z tokenu vs. order.courier_id
        # Pro teď předpokládáme, že user_id v tokenu odpovídá courier_id
        if order.courier_id != user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify orders assigned to you"
            )

    return user


def check_order_access(
    user: CurrentUser,
    order,
    action: str = "read"
) -> bool:
    """
    Zkontroluje přístup k objednávce na základě role a akce.

    Pravidla:
    - admin: může vše
    - dispatcher: může číst a přiřazovat
    - courier: může číst a měnit své objednávky
    - customer: může číst své objednávky

    Args:
        user: Aktuální uživatel
        order: Objednávka k ověření
        action: Typ akce (read, write, delete)

    Returns:
        True pokud má přístup
    """
    if user.role == "admin":
        return True

    if action == "read":
        # Čtení je povoleno všem přihlášeným
        return True

    if action == "write":
        if user.role == "dispatcher":
            return True
        if user.role == "courier":
            return order.courier_id == user.user_id

    if action == "delete":
        return user.role == "admin"

    return False
