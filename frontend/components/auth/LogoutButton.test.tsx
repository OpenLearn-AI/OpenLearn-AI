import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LogoutButton } from "@/components/auth/LogoutButton";
import { getKeycloak } from "@/lib/keycloak";

vi.mock("@/lib/keycloak", () => ({
    getKeycloak: vi.fn(),
}));

function renderWithClient(queryClient: QueryClient) {
    return render(
        <QueryClientProvider client={queryClient}>
            <LogoutButton />
        </QueryClientProvider>,
    );
}

describe("LogoutButton", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it("clears the query cache and calls keycloak.logout with the /login redirect", async () => {
        const mockKeycloak = { logout: vi.fn().mockResolvedValue(undefined) };
        vi.mocked(getKeycloak).mockResolvedValue(mockKeycloak as never);

        const queryClient = new QueryClient();
        const clearSpy = vi.spyOn(queryClient, "clear");

        renderWithClient(queryClient);

        await userEvent.click(screen.getByRole("button", { name: /logout/i }));

        expect(clearSpy).toHaveBeenCalledTimes(1);
        expect(mockKeycloak.logout).toHaveBeenCalledWith({
            redirectUri: `${window.location.origin}/login`,
        });
    });

    it("does nothing if keycloak is unavailable", async () => {
        vi.mocked(getKeycloak).mockResolvedValue(null as never);

        const queryClient = new QueryClient();
        const clearSpy = vi.spyOn(queryClient, "clear");

        renderWithClient(queryClient);

        await userEvent.click(screen.getByRole("button", { name: /logout/i }));

        expect(clearSpy).not.toHaveBeenCalled();
    });
});