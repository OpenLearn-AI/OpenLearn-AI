import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useMe } from "@/features/auth/api/useMe";
import { getAccessToken } from "@/lib/keycloak";
import type { MeResponse } from "@/features/auth/types";

vi.mock("@/lib/keycloak", () => ({
    getAccessToken: vi.fn(),
}));

function createWrapper() {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: { retry: false },
        },
    });

    return function Wrapper({ children }: { children: ReactNode }) {
        return (
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        );
    };
}

const mockMeResponse: MeResponse = {
    id: "user-1",
    email: "student@example.com",
    settings: {},
    roles: ["student"],
    keycloak: { issuer: "http://localhost:8080/realms/openlearn", subject: "abc-123" },
};

describe("useMe", () => {
    beforeEach(() => {
        vi.stubGlobal("fetch", vi.fn());
    });

    afterEach(() => {
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
    });

    it("is in a loading state before the request resolves", () => {
        vi.mocked(getAccessToken).mockReturnValue(new Promise(() => { }));

        const { result } = renderHook(() => useMe(), { wrapper: createWrapper() });

        expect(result.current.isLoading).toBe(true);
        expect(result.current.data).toBeUndefined();
    });

    it("returns the current user on success", async () => {
        vi.mocked(getAccessToken).mockResolvedValue("valid-token");
        vi.mocked(fetch).mockResolvedValue({
            ok: true,
            status: 200,
            json: async () => mockMeResponse,
        } as Response);

        const { result } = renderHook(() => useMe(), { wrapper: createWrapper() });

        await waitFor(() => expect(result.current.isSuccess).toBe(true));

        expect(result.current.data).toEqual(mockMeResponse);
        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining("/auth/me"),
            expect.objectContaining({
                headers: { Authorization: "Bearer valid-token" },
            }),
        );
    });

    it("fails when there is no access token", async () => {
        vi.mocked(getAccessToken).mockResolvedValue(null);

        const { result } = renderHook(() => useMe(), { wrapper: createWrapper() });

        await waitFor(() => expect(result.current.isError).toBe(true));

        expect(result.current.error).toBeInstanceOf(Error);
        expect(fetch).not.toHaveBeenCalled();
    });

    it("fails when the backend responds with a non-ok status", async () => {
        vi.mocked(getAccessToken).mockResolvedValue("valid-token");
        vi.mocked(fetch).mockResolvedValue({
            ok: false,
            status: 401,
            json: async () => ({}),
        } as Response);

        const { result } = renderHook(() => useMe(), { wrapper: createWrapper() });

        await waitFor(() => expect(result.current.isError).toBe(true));

        expect(result.current.error).toBeInstanceOf(Error);
        expect((result.current.error as Error).message).toContain("401");
    });
});