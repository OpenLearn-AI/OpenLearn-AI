import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { useAuthStore } from "@/stores/auth-store";
import { getKeycloak } from "@/lib/keycloak";

vi.mock("@/lib/keycloak", () => ({
    getKeycloak: vi.fn(),
}));

function createMockKeycloak(overrides: Record<string, unknown> = {}) {
    return {
        authenticated: true,
        realmAccess: { roles: ["student"] },
        logout: vi.fn().mockResolvedValue(undefined),
        onAuthLogout: undefined,
        ...overrides,
    };
}

describe("useAuthStore", () => {
    beforeEach(() => {
        useAuthStore.setState({ isAuthenticated: false, isLoading: true, roles: [] });
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it("sets isAuthenticated=false when keycloak is unavailable", async () => {
        vi.mocked(getKeycloak).mockResolvedValue(null as never);

        await useAuthStore.getState().initialize();

        const state = useAuthStore.getState();
        expect(state.isAuthenticated).toBe(false);
        expect(state.isLoading).toBe(false);
    });

    it("sets isAuthenticated and roles from an authenticated keycloak instance (successful auth state / session restoration)", async () => {
        const mockKeycloak = createMockKeycloak({
            authenticated: true,
            realmAccess: { roles: ["admin", "student"] },
        });
        vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

        await useAuthStore.getState().initialize();

        const state = useAuthStore.getState();
        expect(state.isAuthenticated).toBe(true);
        expect(state.isLoading).toBe(false);
        expect(state.roles).toEqual(["admin", "student"]);
    });

    it("sets isAuthenticated=false when Keycloak reports no active session (failed authentication state)", async () => {
        const mockKeycloak = createMockKeycloak({ authenticated: false, realmAccess: undefined });
        vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

        await useAuthStore.getState().initialize();

        const state = useAuthStore.getState();
        expect(state.isAuthenticated).toBe(false);
        expect(state.isLoading).toBe(false);
        expect(state.roles).toEqual([]);
    });

    it("clears auth state when Keycloak triggers onAuthLogout (e.g. expired refresh token)", async () => {
        const mockKeycloak = createMockKeycloak();
        vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

        await useAuthStore.getState().initialize();
        expect(useAuthStore.getState().isAuthenticated).toBe(true);

        mockKeycloak.onAuthLogout?.();

        const state = useAuthStore.getState();
        expect(state.isAuthenticated).toBe(false);
        expect(state.roles).toEqual([]);
    });

    describe("logout", () => {
        it("clears auth state and calls keycloak.logout with the /login redirect", async () => {
            const mockKeycloak = createMockKeycloak();
            vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

            await useAuthStore.getState().initialize();
            await useAuthStore.getState().logout();

            expect(mockKeycloak.logout).toHaveBeenCalledWith({
                redirectUri: `${window.location.origin}/login`,
            });

            const state = useAuthStore.getState();
            expect(state.isAuthenticated).toBe(false);
            expect(state.roles).toEqual([]);
        });

        it("does nothing if keycloak is unavailable", async () => {
            vi.mocked(getKeycloak).mockResolvedValue(null as never);

            await expect(useAuthStore.getState().logout()).resolves.toBeUndefined();
        });
    });
});