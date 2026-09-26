import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { useAuthStore } from "@/stores/auth-store";

const mockRouter = { replace: vi.fn(), push: vi.fn() };
const mockInitialize = vi.fn();

vi.mock("next/navigation", () => ({
    useRouter: () => mockRouter,
}));

vi.mock("@/stores/auth-store", () => ({
    useAuthStore: vi.fn(),
}));

function mockStore(overrides: { isAuthenticated: boolean; isLoading: boolean }) {
    vi.mocked(useAuthStore).mockReturnValue({
        initialize: mockInitialize,
        roles: [],
        logout: vi.fn(),
        ...overrides,
    } as unknown as ReturnType<typeof useAuthStore>);
}

describe("RequireAuth", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it("calls initialize() on mount", () => {
        mockStore({ isLoading: true, isAuthenticated: false });

        render(
            <RequireAuth>
                <p>secret content</p>
            </RequireAuth>,
        );

        expect(mockInitialize).toHaveBeenCalledTimes(1);
    });

    it("shows a loading state while the session is being checked", () => {
        mockStore({ isLoading: true, isAuthenticated: false });

        render(
            <RequireAuth>
                <p>secret content</p>
            </RequireAuth>,
        );

        expect(screen.getByText(/checking your session/i)).toBeInTheDocument();
        expect(screen.queryByText("secret content")).not.toBeInTheDocument();
        expect(mockRouter.replace).not.toHaveBeenCalled();
    });

    it("redirects to /login once loading finishes and the user is not authenticated", () => {
        mockStore({ isLoading: false, isAuthenticated: false });

        render(
            <RequireAuth>
                <p>secret content</p>
            </RequireAuth>,
        );

        expect(mockRouter.replace).toHaveBeenCalledWith("/login");
        expect(screen.queryByText("secret content")).not.toBeInTheDocument();
    });

    it("renders the children when the user is authenticated", () => {
        mockStore({ isLoading: false, isAuthenticated: true });

        render(
            <RequireAuth>
                <p>secret content</p>
            </RequireAuth>,
        );

        expect(screen.getByText("secret content")).toBeInTheDocument();
        expect(mockRouter.replace).not.toHaveBeenCalled();
    });
});