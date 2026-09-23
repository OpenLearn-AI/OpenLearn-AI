import type Keycloak from "keycloak-js";

let keycloak: Keycloak | null = null;
let initPromise: Promise<Keycloak> | null = null;

export async function getKeycloak(): Promise<Keycloak | null> {
    if (typeof window === "undefined") {
        return null;
    }

    if (initPromise) {
        return initPromise;
    }

    initPromise = (async () => {
        const keycloakModule = await import("keycloak-js");
        const KeycloakConstructor = keycloakModule.default;

        if (!keycloak) {
            keycloak = new KeycloakConstructor({
                url: "http://localhost:8080",
                realm: "openlearn",
                clientId: "openlearn-frontend",
            });
        }

        if (!keycloak.authenticated) {
            await keycloak.init({
                onLoad: "check-sso",
                pkceMethod: "S256",
                checkLoginIframe: false,
            });
        }

        return keycloak;
    })();

    try {
        return await initPromise;
    } catch (error) {
        initPromise = null;
        console.error("Failed to initialize Keycloak:", error);
        return null;
    }
}

export async function getAccessToken(): Promise<string | null> {
    const instance = await getKeycloak();

    if (!instance || !instance.authenticated) {
        return null;
    }

    try {
        await instance.updateToken(30);
    } catch (error) {
        console.error("Failed to refresh Keycloak token:", error);
        return null;
    }

    return instance.token ?? null;
}