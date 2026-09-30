from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.courses import router as courses_router
from app.api.materials import (
    router as materials_router,
    status_router as material_status_router,
)
from app.api.users import router as users_router

from app.config import settings
from app.observability import setup_observability, setup_metrics
from app.services.auth.user_service import (
    DuplicateEmailError,
    KeycloakIdentityError,
)


app = FastAPI(
    title=settings.app_name,
)

setup_observability()
setup_metrics(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(materials_router)
app.include_router(material_status_router)


# A validated Keycloak token that cannot be resolved to a user is a caller
# problem, not a server fault: report it as 4xx instead of an opaque 500.
# Handlers are per exception type (never a global ValueError catch); the more
# specific DuplicateEmailError wins over the base handler via the MRO.
@app.exception_handler(KeycloakIdentityError)
async def keycloak_identity_error_handler(
    request: Request,
    exc: KeycloakIdentityError,
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(DuplicateEmailError)
async def duplicate_email_error_handler(
    request: Request,
    exc: DuplicateEmailError,
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/health")
async def health_check():
    return {"status": "ok"}
