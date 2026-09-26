import { create } from "zustand";
import { getKeycloak } from "@/lib/keycloak";

interface AuthState {
    isAuthenticated: boolean;
    isLoading: boolean;
    roles: string[];
    initialize: () => Promise<void>;
    logout: () => Promise<void>;
}

let refreshIntervalId: ReturnType<typeof setInterval> | null = null;

export const useAuthStore = create<AuthState>((set) => ({
    isAuthenticated: false,
    isLoading: true,
    roles: [],

    initialize: async () => {
        const keycloak = await getKeycloak();

        if (!keycloak) {
            set({ isAuthenticated: false, isLoading: false });
            return;
        }

        set({
            isAuthenticated: !!keycloak.authenticated,
            isLoading: false,
            roles: keycloak.realmAccess?.roles ?? [],
        });

        // Bug fix: nothing was refreshing the access token before this.
        // accessTokenLifespan is 300s in the realm config, so without this
        // every API call started failing with 401 shortly after login.
        if (refreshIntervalId) {
            clearInterval(refreshIntervalId);
        }

        refreshIntervalId = setInterval(async () => {
            try {
                await keycloak.updateToken(70);
            } catch {
                set({ isAuthenticated: false, roles: [] });

                if (refreshIntervalId) {
                    clearInterval(refreshIntervalId);
                    refreshIntervalId = null;
                }

                await keycloak.login({ redirectUri: window.location.origin });
            }
        }, 30000);

        keycloak.onAuthLogout = () => {
            set({ isAuthenticated: false, roles: [] });

            if (refreshIntervalId) {
                clearInterval(refreshIntervalId);
                refreshIntervalId = null;
            }
        };
    },

    logout: async () => {
        const keycloak = await getKeycloak();

        if (!keycloak) return;

        if (refreshIntervalId) {
            clearInterval(refreshIntervalId);
            refreshIntervalId = null;
        }

        set({ isAuthenticated: false, roles: [] });

        await keycloak.logout({
            redirectUri: `${window.location.origin}/login`,
        });
    },
}));