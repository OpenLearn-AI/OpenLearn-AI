import type Keycloak from "keycloak-js";

let keycloak: Keycloak | null = null;
let initPromise: Promise<Keycloak> | null = null;

export async function getKeycloak() {
    if (typeof window === "undefined") {
        return null;
    }

    if (initPromise) {
        return initPromise;
    }

    initPromise = (async () => {
        const module = await import("keycloak-js");
        const KeycloakConstructor = module.default;

        if (!keycloak) {
            keycloak = new KeycloakConstructor({
                url: "http://localhost:8080",
                realm: "openlearn",
                clientId: "openlearn-frontend",
            });
        }

        await keycloak.init({
            onLoad: "check-sso",
            pkceMethod: "S256",
        });

        return keycloak;
    })();

    return initPromise;
}