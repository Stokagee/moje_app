"""
CRUD operace pro uživatele.
Pracuje s PostgreSQL databází.
"""
import bcrypt
from typing import Optional
from sqlalchemy.orm import Session

from models import User


def hash_password(password: str) -> str:
    """Zahashuje heslo pomocí bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Ověří heslo proti hashi."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def get_user(db: Session, username: str) -> Optional[User]:
    """
    Získá uživatele podle username.

    Args:
        db: Database session
        username: Uživatelské jméno

    Returns:
        User objekt nebo None
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Získá uživatele podle emailu.

    Args:
        db: Database session
        email: Email uživatele

    Returns:
        User objekt nebo None
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, password: str, email: str) -> User:
    """
    Vytvoří nového uživatele.

    Args:
        db: Database session
        username: Uživatelské jméno
        password: Heslo v plaintextu (bude zahashováno)
        email: Email uživatele

    Returns:
        Vytvořený User objekt

    Raises:
        ValueError: Pokud username nebo email již existuje
    """
    # Kontrola existence
    if get_user(db, username):
        raise ValueError(f"Uživatel '{username}' již existuje")
    if get_user_by_email(db, email):
        raise ValueError(f"Email '{email}' je již registrován")

    # Vytvoření uživatele
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Ověří uživatele podle username a hesla.

    Args:
        db: Database session
        username: Uživatelské jméno
        password: Heslo v plaintextu

    Returns:
        User objekt pokud ověření úspěšné, jinak None
    """
    user = get_user(db, username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def get_all_users(db: Session) -> list[User]:
    """
    Vrátí seznam všech uživatelů.

    Args:
        db: Database session

    Returns:
        List User objektů
    """
    return db.query(User).all()


def user_exists(db: Session, username: str) -> bool:
    """
    Zkontroluje, zda uživatel existuje.

    Args:
        db: Database session
        username: Uživatelské jméno

    Returns:
        True pokud existuje, False jinak
    """
    return get_user(db, username) is not None
