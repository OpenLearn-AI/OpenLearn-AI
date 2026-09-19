from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.auth.oidc import decode_access_token, extract_roles
from app.services.auth.user_service import get_user_by_keycloak_identity

_bearer = HTTPBearer(auto_error=False)


def get_current_oidc_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        return decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise unauthorized from exc


async def get_current_user(
    claims: dict[str, Any] = Depends(get_current_oidc_claims),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the local user from the validated token identity.

    Lookup-only by (keycloak_issuer, keycloak_subject): a valid token for an
    unknown local user is a 404, never a silent creation.
    """
    user = await get_user_by_keycloak_identity(db, claims)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


def require_role(required_role: str):
    def dependency(
        claims: dict[str, Any] = Depends(get_current_oidc_claims),
    ) -> dict[str, Any]:
        roles = extract_roles(claims)

        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return claims

    return dependency


require_student = require_role("student")
require_instructor = require_role("instructor")
require_admin = require_role("admin")