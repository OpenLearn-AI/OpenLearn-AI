from app.config import settings


def test_keycloak_configuration() -> None:
    assert settings.keycloak_issuer == "http://localhost:8080/realms/openlearn"
    assert (
        settings.keycloak_jwks_url
        == "http://localhost:8080/realms/openlearn/protocol/openid-connect/certs"
    )
    assert settings.keycloak_audience == "openlearn-api"
    assert settings.keycloak_client_id == "openlearn-frontend"


def test_cors_origin_list() -> None:
    assert settings.cors_origin_list == ["http://localhost:3000"]