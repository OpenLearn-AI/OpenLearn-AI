from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_oidc_claims
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, RegisterResponse
from app.services.auth.keycloak_admin import (
    KeycloakAdminError,
    KeycloakUserExistsError,
    keycloak_admin,
)
from app.services.auth.oidc import extract_roles
from app.services.auth.user_service import get_or_create_user_from_keycloak


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(payload: RegisterRequest) -> RegisterResponse:
    try:
        await keycloak_admin.create_user(
            email=str(payload.email),
            password=payload.password,
        )
    except KeycloakUserExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc
    except KeycloakAdminError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Registration service is temporarily unavailable.",
        ) from exc

    return RegisterResponse(
        message="Registration successful.",
        email=payload.email,
    )


@router.get("/me")
async def read_current_user(
    claims: dict[str, Any] = Depends(get_current_oidc_claims),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user = await get_or_create_user_from_keycloak(db, claims)

    return {
        "id": str(user.id),
        "email": user.email,
        "preferred_lang": user.preferred_lang,
        "settings": user.settings,
        "roles": extract_roles(claims),
        "keycloak": {
            "issuer": user.keycloak_issuer,
            "subject": user.keycloak_subject,
        },
    }
