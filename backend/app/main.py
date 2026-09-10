from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router

from app.config import settings


#<_________________________________________________
import structlog
from app.observability import setup_observability, setup_metrics
#__________________________________________________>

app = FastAPI(
    title=settings.app_name,
)

#<_________________________________________________
setup_observability()
setup_metrics(app)
logger = structlog.get_logger()
#__________________________________________________>

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
#<_____________________________________________________
@app.get("/test/error")
async def test_error():
    logger.error("test_error_endpoint_triggered", path="/test/error")
    raise Exception("This is a staging test error for Sentry verification!")
#______________________________________________________>