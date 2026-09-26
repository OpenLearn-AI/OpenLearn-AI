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
        updateToken: vi.fn().mockResolvedValue(true),
        login: vi.fn().mockResolvedValue(undefined),
        logout: vi.fn().mockResolvedValue(undefined),
        onAuthLogout: undefined,
        ...overrides,
    };
}

describe("useAuthStore", () => {
    beforeEach(() => {
        vi.useFakeTimers();
        useAuthStore.setState({ isAuthenticated: false, isLoading: true, roles: [] });
    });

    afterEach(() => {
        vi.clearAllTimers();
        vi.useRealTimers();
        vi.restoreAllMocks();
    });

    it("sets isAuthenticated=false when keycloak is unavailable", async () => {
        vi.mocked(getKeycloak).mockResolvedValue(null as never);

        await useAuthStore.getState().initialize();

        const state = useAuthStore.getState();
        expect(state.isAuthenticated).toBe(false);
        expect(state.isLoading).toBe(false);
    });

    it("sets isAuthenticated and roles from an authenticated keycloak instance", async () => {
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

    it("refreshes the token every 30s via updateToken(70)", async () => {
        const mockKeycloak = createMockKeycloak();
        vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

        await useAuthStore.getState().initialize();
        expect(mockKeycloak.updateToken).not.toHaveBeenCalled();

        await vi.advanceTimersByTimeAsync(30000);
        expect(mockKeycloak.updateToken).toHaveBeenCalledWith(70);

        await vi.advanceTimersByTimeAsync(30000);
        expect(mockKeycloak.updateToken).toHaveBeenCalledTimes(2);
    });

    it("logs out and redirects to Keycloak login when token refresh fails", async () => {
        const mockKeycloak = createMockKeycloak({
            updateToken: vi.fn().mockRejectedValue(new Error("refresh failed")),
        });
        vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

        await useAuthStore.getState().initialize();
        await vi.advanceTimersByTimeAsync(30000);

        await vi.waitFor(() => {
            expect(mockKeycloak.login).toHaveBeenCalledWith({
                redirectUri: window.location.origin,
            });
        });

        const state = useAuthStore.getState();
        expect(state.isAuthenticated).toBe(false);
        expect(state.roles).toEqual([]);
    });

    it("does not stack a second interval when initialize() runs twice", async () => {
        const mockKeycloak = createMockKeycloak();
        vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

        await useAuthStore.getState().initialize();
        await useAuthStore.getState().initialize();

        await vi.advanceTimersByTimeAsync(30000);
        expect(mockKeycloak.updateToken).toHaveBeenCalledTimes(1);
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