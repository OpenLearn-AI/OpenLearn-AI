from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_oidc_claims
from app.db.session import get_db
from app.services.auth.oidc import extract_roles
from app.services.auth.user_service import get_or_create_user_from_keycloak

router = APIRouter(prefix="/auth", tags=["auth"])


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