"""Response schema for GET /auth/me.

The endpoint already returned this payload as a plain dict; this module makes
the existing contract explicit for OpenAPI without changing what is served.
"""

from typing import Any

from pydantic import BaseModel


class KeycloakIdentity(BaseModel):
    """The Keycloak identity pair that owns the local user row (ADR-0006)."""

    issuer: str
    subject: str


class CurrentUserResponse(BaseModel):
    """Body of GET /auth/me: the local user plus its realm roles.

    Field types mirror what the endpoint has always returned: ``id`` is the
    stringified UUID and ``settings`` is the free-form JSONB blob, so
    declaring this model changes nothing about the response.
    """

    id: str
    email: str
    settings: dict[str, Any]
    roles: list[str]
    keycloak: KeycloakIdentity
