from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "OpenLearn AI"
    environment: str = "development"
    debug: bool = False
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql+asyncpg://postgres@localhost:5432/openlearn_ai"

    # Keycloak / OIDC
    keycloak_issuer: str = "http://localhost:8080/realms/openlearn"
    keycloak_jwks_url: str = (
        "http://localhost:8080/realms/openlearn/protocol/openid-connect/certs"
    )
    keycloak_audience: str = "openlearn-api"
    keycloak_client_id: str = "openlearn-frontend"

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


settings = Settings()
