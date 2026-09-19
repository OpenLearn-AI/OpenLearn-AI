from typing import Any

import httpx

from app.config import settings


class KeycloakAdminError(Exception):
    """Base error for Keycloak Admin API failures."""


class KeycloakUserExistsError(KeycloakAdminError):
    """Raised when the Keycloak user already exists."""


class KeycloakAdminService:
    def __init__(self) -> None:
        self.server_url = settings.keycloak_admin_server_url.rstrip("/")
        self.admin_realm = settings.keycloak_admin_realm
        self.user_realm = settings.keycloak_user_realm

    async def _get_admin_token(self) -> str:
        token_url = (
            f"{self.server_url}/realms/{self.admin_realm}"
            "/protocol/openid-connect/token"
        )

        data = {
            "client_id": "admin-cli",
            "username": settings.keycloak_admin_username,
            "password": settings.keycloak_admin_password,
            "grant_type": "password",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(token_url, data=data)
        except httpx.HTTPError as exc:
            raise KeycloakAdminError(
                "Could not connect to Keycloak."
            ) from exc

        if response.status_code != 200:
            raise KeycloakAdminError(
                "Could not authenticate with Keycloak Admin API."
            )

        payload: dict[str, Any] = response.json()
        access_token = payload.get("access_token")

        if not isinstance(access_token, str) or not access_token:
            raise KeycloakAdminError(
                "Keycloak Admin API did not return an access token."
            )

        return access_token

    async def create_user(
        self,
        *,
        email: str,
        password: str,
    ) -> None:
        access_token = await self._get_admin_token()

        users_url = (
            f"{self.server_url}/admin/realms/"
            f"{self.user_realm}/users"
        )

        user_representation = {
            "username": email,
            "email": email,
            "enabled": True,
            "emailVerified": False,
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False,
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    users_url,
                    json=user_representation,
                    headers=headers,
                )
        except httpx.HTTPError as exc:
            raise KeycloakAdminError(
                "Could not connect to Keycloak."
            ) from exc

        if response.status_code == 409:
            raise KeycloakUserExistsError(
                "A user with this email already exists."
            )

        if response.status_code not in (201, 204):
            raise KeycloakAdminError(
                "Keycloak could not create the user."
            )


keycloak_admin = KeycloakAdminService()
