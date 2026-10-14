import type Keycloak from "keycloak-js";

import { config } from "@/lib/config";

let keycloak: Keycloak | null = null;
let initPromise: Promise<Keycloak> | null = null;

/**
 * Subscribers invoked when the Keycloak token refresh fails (W1's
 * previously missing "token-expired event"). `lib/query-provider.tsx`
 * subscribes to trigger the global 401 session recovery;
 * `lib/auth-context.tsx` subscribes to reflect the expired session in
 * React state so the existing AuthGuard redirect also reacts.
 */
type RefreshErrorListener = () => void;
const refreshErrorListeners: RefreshErrorListener[] = [];

/**
 * Subscribe to the Keycloak token-refresh-failure event. Returns an
 * unsubscribe function for effect cleanup.
 */
export function onKeycloakRefreshError(
    listener: RefreshErrorListener,
): () => void {
    refreshErrorListeners.push(listener);

    return () => {
        const index = refreshErrorListeners.indexOf(listener);

        if (index >= 0) {
            refreshErrorListeners.splice(index, 1);
        }
    };
}

function emitRefreshError(): void {
    for (const listener of refreshErrorListeners) {
        listener();
    }
}

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
                url: config.keycloak.url,
                realm: config.keycloak.realm,
                clientId: config.keycloak.clientId,
            });
        }

        // W1: surface the previously missing token-expired event. The
        // adapter fires `onAuthRefreshError` when a forced token
        // refresh fails; fan the event out to subscribers. The init
        // options below are unchanged (protected: check-sso, PKCE,
        // iframe setting).
        keycloak.onAuthRefreshError = emitRefreshError;

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