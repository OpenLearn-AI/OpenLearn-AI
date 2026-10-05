from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "OpenLearn AI"
    environment: str = "development"
    debug: bool = False
    cors_origins: str = "http://localhost:3000"
    database_url: str = (
        "postgresql+asyncpg://openlearn:devpassword@localhost:5432/openlearn_dev"
    )

    # Keycloak / OIDC
    keycloak_issuer: str = "http://localhost:8080/realms/openlearn"
    keycloak_jwks_url: str = (
        "http://localhost:8080/realms/openlearn/protocol/openid-connect/certs"
    )
    keycloak_audience: str = "openlearn-api"

    # PAL / AI Settings
    ai_ocr_provider: str = "mock"
    ai_ocr_fallbacks: str = ""
    ai_ocr_model: str = "gemini-2.5-flash"
    gemini_api_key: str = ""
    ai_embedding_provider: str = "mock"
    ai_embedding_fallbacks: str = ""
    ai_embedding_model: str = "BAAI/bge-m3"
    ai_embedding_dimension: int = 1024
    # Device for local embedding inference: "auto" (CUDA if available, else
    # CPU), "cpu" (forced CPU), or "cuda" (requires an actual CUDA device).
    ai_embedding_device: str = "auto"
    ai_reasoning_provider: str = "mock"
    ai_reasoning_fallbacks: str = ""
    ai_reasoning_model: str = "gpt-4o-mini"

    # LiteLLM gateway (ADR-0005) — OpenAI-compatible reasoning surface.
    # The key is a LiteLLM virtual/master key; staging env wiring is a
    # DevOps task (H1), not an application concern.
    litellm_api_base: str = "http://litellm:4000"
    litellm_api_key: str = ""
    ai_vector_db_provider: str = "mock"

    # Chunking
    chunk_size: int = 1200
    chunk_overlap: int = 150

    # OCR text-length gate (targeted-OCR eligibility; services/ocr.py)
    ocr_min_text_chars: int = 50

    # S3-compatible object storage (MinIO) for course materials
    # Credentials are deployment configuration and must never be hardcoded.
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    s3_bucket_name: str = "openlearn-materials"
    s3_region_name: str = "us-east-1"
    s3_url_expiration_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def ocr_fallback_list(self) -> list[str]:
        return [f.strip() for f in self.ai_ocr_fallbacks.split(",") if f.strip()]

    @property
    def embedding_fallback_list(self) -> list[str]:
        return [f.strip() for f in self.ai_embedding_fallbacks.split(",") if f.strip()]

    @property
    def reasoning_fallback_list(self) -> list[str]:
        return [f.strip() for f in self.ai_reasoning_fallbacks.split(",") if f.strip()]



settings = Settings()
