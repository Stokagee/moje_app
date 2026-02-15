# PKCE Helper Functions

"""
PKCE (Proof Key for Code Exchange) helper functions.

These functions implement the PKCE verification logic:
- generate_code_verifier: Create random verifier
- create_code_challenge: Hash verifier to create challenge
- verify_code_verifier: Verify verifier matches challenge
"""

import hashlib
import base64
import secrets


def generate_code_verifier(length: int = 64) -> str:
    """
    Generuje code_verifier pro PKCE.

    Code verifier musí mít délku 43-128 znaků.
    Používá base64url encoding pro bezpečné URL znaky.

    Args:
        length: Délka verifieru (v bajtech před encoding)

    Returns:
        URL-safe base64 encoded string
    """
    random_bytes = secrets.token_bytes(length)
    code_verifier = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')

    # Ujisti se, že délka je v rozsahu 43-128
    if len(code_verifier) < 43:
        return generate_code_verifier(length * 2)
    if len(code_verifier) > 128:
        return generate_code_verifier(length // 2)

    return code_verifier


def create_code_challenge(code_verifier: str, method: str = "S256") -> str:
    """
    Vytvoří code_challenge z code_verifieru.

    Args:
        code_verifier: Předem vygenerovaný verifier
        method: Metoda hashování ("S256" pro SHA256)

    Returns:
        Code challenge string
    """
    if method == "S256":
        challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
        return code_challenge
    else:
        raise ValueError(f"Unsupported code_challenge_method: {method}")


def verify_code_verifier(code_verifier: str, code_challenge: str) -> bool:
    """
    Ověří, zda code_verifier odpovídá code_challenge.

    Tato funkce se používá v token endpointu pro ověření,
    že klient poslal správný verifier.

    Args:
        code_verifier: Verifier od klienta (z /token requestu)
        code_challenge: Uložená challenge (z /authorize requestu)

    Returns:
        True pokud verifier odpovídá challenge
    """
    expected_challenge = create_code_challenge(code_verifier, "S256")
    return expected_challenge == code_challenge


def generate_pkce_pair() -> tuple[str, str]:
    """
    Vygeneruje PKCE pair (verifier a challenge).

    Returns:
        (code_verifier, code_challenge) tuple
    """
    verifier = generate_code_verifier()
    challenge = create_code_challenge(verifier)
    return verifier, challenge
