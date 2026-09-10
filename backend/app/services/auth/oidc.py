"""Validation of OIDC access tokens issued by Keycloak.

The backend does not render login pages; users authenticate against
Keycloak in the browser. A Keycloak-issued access token is presented as a
bearer token on API requests and validated here using the realm's JWKS.
"""

from typing import Any

import jwt
from jwt import InvalidTokenError, PyJWKClient, PyJWKClientError

from app.config import settings

_KEYCLOAK_ALGORITHMS = ["RS256"]

_JWK_CLIENT = PyJWKClient(
    settings.keycloak_jwks_url,
    cache_keys=True,
)


def _signing_key(token: str):
    try:
        return _JWK_CLIENT.get_signing_key_from_jwt(token).key
    except (PyJWKClientError, jwt.DecodeError) as exc:
        raise ValueError("Could not resolve the token signing key.") from exc


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a Keycloak access token.

    Verifies the RS256 signature against the realm JWKS, the issuer, and
    the ``openlearn-api`` audience. Returns the decoded claims.

    Raises ``ValueError`` for any validation failure.
    """
    try:
        payload = jwt.decode(
            token,
            key=_signing_key(token),
            algorithms=_KEYCLOAK_ALGORITHMS,
            audience=settings.keycloak_audience,
            issuer=settings.keycloak_issuer,
            options={
                "require": ["exp", "iat", "iss", "aud", "sub"],
            },
        )
    except InvalidTokenError as exc:
        raise ValueError("Invalid access token.") from exc

    if not payload.get("sub"):
        raise ValueError("Access token subject is missing.")

    return payload


def extract_roles(payload: dict[str, Any]) -> list[str]:
    """Extract realm roles from decoded access token claims.

    Returns only well-formed string roles. Malformed ``realm_access`` or
    ``roles`` values yield an empty list.
    """
    realm_access = payload.get("realm_access")
    if not isinstance(realm_access, dict):
        return []

    roles = realm_access.get("roles", [])
    if not isinstance(roles, list):
        return []

    return [role for role in roles if isinstance(role, str) and role]