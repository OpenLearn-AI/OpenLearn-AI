import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { UserInfo } from "@/components/auth/UserInfo";
import { useMe } from "@/features/auth/api/useMe";
import type { MeResponse } from "@/features/auth/types";

vi.mock("@/features/auth/api/useMe", () => ({
    useMe: vi.fn(),
}));

function mockUseMe(overrides: Partial<{
    data: MeResponse | undefined;
    isLoading: boolean;
    isError: boolean;
}>) {
    vi.mocked(useMe).mockReturnValue({
        data: undefined,
        isLoading: false,
        isError: false,
        ...overrides,
    } as unknown as ReturnType<typeof useMe>);
}

const baseUser: MeResponse = {
    id: "user-1",
    email: "student@example.com",
    settings: {},
    roles: ["student"],
    keycloak: { issuer: "http://localhost:8080/realms/openlearn", subject: "abc-123" },
};

describe("UserInfo", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it("shows a loading message while /auth/me is pending", () => {
        mockUseMe({ isLoading: true });

        render(<UserInfo />);

        expect(screen.getByText(/loading your profile/i)).toBeInTheDocument();
    });

    it("shows an error message when /auth/me fails", () => {
        mockUseMe({ isLoading: false, isError: true });

        render(<UserInfo />);

        expect(
            screen.getByText(/unable to load your account information/i),
        ).toBeInTheDocument();
    });

    it("shows an error message when data is missing even without isError", () => {
        mockUseMe({ isLoading: false, isError: false, data: undefined });

        render(<UserInfo />);

        expect(
            screen.getByText(/unable to load your account information/i),
        ).toBeInTheDocument();
    });

    it("renders a single role as plain text (role-aware: one role)", () => {
        mockUseMe({ data: { ...baseUser, roles: ["student"] } });

        render(<UserInfo />);

        // getByText only matches an element's own direct text node, not its
        // descendants' text, so the "Email:"/"Role:" <span> labels and their
        // values (siblings of the span, inside the same <p>) are checked separately.
        expect(screen.getByText("student@example.com")).toBeInTheDocument();
        expect(screen.getByText("Role:")).toBeInTheDocument();
        expect(screen.getByText("student")).toBeInTheDocument();
        expect(screen.queryByText("Roles:")).not.toBeInTheDocument();
    });

    it("renders a bulleted list when the user has multiple roles (role-aware: many roles)", () => {
        mockUseMe({ data: { ...baseUser, roles: ["student", "instructor"] } });

        render(<UserInfo />);

        expect(screen.getByText("Roles:")).toBeInTheDocument();
        // Each <li> is its own leaf node, so exact text matches work here.
        expect(screen.getByText("student")).toBeInTheDocument();
        expect(screen.getByText("instructor")).toBeInTheDocument();
        expect(screen.queryByText("Role:")).not.toBeInTheDocument();
    });
});