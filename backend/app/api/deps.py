from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth.oidc import decode_access_token, extract_roles

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