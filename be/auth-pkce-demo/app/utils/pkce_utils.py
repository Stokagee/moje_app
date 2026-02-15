# PKCE Utils - Client Side Functions

"""
PKCE utilities for generating verifier and challenge on client side.

NOTE: These functions should run on the CLIENT side (SPA, mobile app).
The server only needs to verify the challenge matches the verifier.
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
    elif method == "plain":
        # Plain text (nedoporučeno, ale specifikace to umožňuje)
        return code_verifier
    else:
        raise ValueError(f"Unsupported code_challenge_method: {method}")


def verify_pkce(code_verifier: str, code_challenge: str, method: str = "S256") -> bool:
    """
    Ověří, zda code_verifier odpovídá code_challenge.

    Args:
        code_verifier: Verifier od klienta
        code_challenge: Uložená challenge
        method: Metoda hashování

    Returns:
        True pokud verifier odpovídá challenge
    """
    expected_challenge = create_code_challenge(code_verifier, method)
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


# Example client-side usage
if __name__ == "__main__":
    print("=== PKCE Client Demo ===\n")

    # 1. Generovat PKCE pair
    verifier, challenge = generate_pkce_pair()

    print(f"Code Verifier: {verifier}")
    print(f"Code Challenge: {challenge}")
    print(f"Verifier Length: {len(verifier)}")
    print(f"Challenge Length: {len(challenge)}")

    # 2. Ukázka autorizační URL
    client_id = "pkce-spa-client"
    redirect_uri = "http://localhost:3000/callback"
    state = "random-state-123"

    auth_url = (
        f"/oauth2/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"code_challenge={challenge}&"
        f"code_challenge_method=S256&"
        f"state={state}"
    )

    print(f"\nAuthorization URL with PKCE:\n{auth_url}")

    # 3. Ukázka ověření
    is_valid = verify_pkce(verifier, challenge)
    print(f"\nPKCE Verification: {'✓ Valid' if is_valid else '✗ Invalid'}")
