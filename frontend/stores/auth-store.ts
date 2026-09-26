import { create } from "zustand";
import { getKeycloak } from "@/lib/keycloak";

interface AuthState {
    isAuthenticated: boolean;
    isLoading: boolean;
    roles: string[];
    initialize: () => Promise<void>;
    logout: () => Promise<void>;
}

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

        // Token refresh is handled on-demand by getAccessToken() (lib/keycloak.ts)
        // right before each authenticated API request — no background interval
        // needed here. Previously this store ran its own setInterval doing the
        // same job in parallel; removed in favor of the single on-demand path
        // used across courses/profile (see fix(#3) on
        // fix/frontend-pre-week7-integration).
        keycloak.onAuthLogout = () => {
            set({ isAuthenticated: false, roles: [] });
        };
    },

    logout: async () => {
        const keycloak = await getKeycloak();

        if (!keycloak) return;

        set({ isAuthenticated: false, roles: [] });

        await keycloak.logout({
            redirectUri: `${window.location.origin}/login`,
        });
    },
}));