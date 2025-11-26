"""
In-memory uživatelská databáze.

Pro výukové účely - žádná skutečná databáze!
Uživatelé jsou uloženi v paměti (dict) a resetují se při restartu serveru.
"""
import bcrypt
from typing import Optional


def hash_password(password: str) -> str:
    """Zahashuje heslo pomocí bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Ověří heslo proti hashi."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# ============================================================
# IN-MEMORY DATABÁZE UŽIVATELŮ
# ============================================================
# Struktura: {username: {username, email, hashed_password}}
FAKE_USERS_DB: dict = {}

# Předvytvořené testovací účty (hesla: "admin123" a "user123")
FAKE_USERS_DB["admin"] = {
    "username": "admin",
    "email": "admin@example.com",
    "hashed_password": hash_password("admin123"),
}

FAKE_USERS_DB["user"] = {
    "username": "user",
    "email": "user@example.com",
    "hashed_password": hash_password("user123"),
}


# ============================================================
# FUNKCE PRO PRÁCI S UŽIVATELI
# ============================================================

def get_user(username: str) -> Optional[dict]:
    """
    Získá uživatele podle username.

    Args:
        username: Uživatelské jméno

    Returns:
        Dict s uživatelskými daty nebo None
    """
    return FAKE_USERS_DB.get(username)


def create_user(username: str, password: str, email: str) -> dict:
    """
    Vytvoří nového uživatele.

    Args:
        username: Uživatelské jméno
        password: Heslo v plaintextu (bude zahashováno)
        email: Email uživatele

    Returns:
        Dict s vytvořeným uživatelem

    Raises:
        ValueError: Pokud username již existuje
    """
    if username in FAKE_USERS_DB:
        raise ValueError(f"Uživatel '{username}' již existuje")

    user = {
        "username": username,
        "email": email,
        "hashed_password": hash_password(password),
    }
    FAKE_USERS_DB[username] = user
    return user


def verify_user(username: str, password: str) -> Optional[dict]:
    """
    Ověří uživatele podle username a hesla.

    Args:
        username: Uživatelské jméno
        password: Heslo v plaintextu

    Returns:
        Dict s uživatelskými daty pokud ověření úspěšné, jinak None
    """
    user = get_user(username)
    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return user


def get_all_users() -> list[dict]:
    """
    Vrátí seznam všech uživatelů (bez hesel).

    Returns:
        List uživatelů
    """
    return [
        {"username": u["username"], "email": u["email"]}
        for u in FAKE_USERS_DB.values()
    ]
