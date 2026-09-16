import { afterEach, describe, expect, it, vi } from "vitest";
import type { User } from "oidc-client-ts";
import { render, screen, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { useAuthStore } from "@/lib/auth-store";
import { getCurrentUser } from "@/lib/auth";

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

vi.mock("@/lib/auth", () => ({
  getCurrentUser: vi.fn(),
}));

describe("ProtectedRoute", () => {
  const replaceMock = vi.fn();

  const routerMock = {
    back: vi.fn(),
    forward: vi.fn(),
    refresh: vi.fn(),
    push: vi.fn(),
    replace: replaceMock,
    prefetch: vi.fn(),
  };

  afterEach(() => {
    vi.clearAllMocks();

    useAuthStore.setState({
      status: "unknown",
      user: null,
    });
  });

  const renderProtectedRoute = () => {
    return render(
      <ProtectedRoute>
        <div>Protected content</div>
      </ProtectedRoute>,
    );
  };

  it("shows loading state while restoring the session", () => {
    vi.mocked(useRouter).mockReturnValue(
      routerMock as unknown as ReturnType<typeof useRouter>,
    );

    vi.mocked(getCurrentUser).mockImplementation(
      () => new Promise(() => {}),
    );

    renderProtectedRoute();

    expect(screen.getByText("Restoring session...")).toBeInTheDocument();
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("renders protected content for an authenticated user", async () => {
    vi.mocked(useRouter).mockReturnValue(
      routerMock as unknown as ReturnType<typeof useRouter>,
    );

    const user = {
      expired: false,
      access_token: "test-access-token",
    } as unknown as User;

    vi.mocked(getCurrentUser).mockResolvedValue(user);

    renderProtectedRoute();

    await waitFor(() => {
      expect(
        screen.getByText("Protected content"),
      ).toBeInTheDocument();
    });

    expect(replaceMock).not.toHaveBeenCalled();
  });

  it("redirects unauthenticated users to login", async () => {
    vi.mocked(useRouter).mockReturnValue(
      routerMock as unknown as ReturnType<typeof useRouter>,
    );

    vi.mocked(getCurrentUser).mockResolvedValue(null);

    renderProtectedRoute();

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/login");
    });

    expect(
      screen.queryByText("Protected content"),
    ).not.toBeInTheDocument();
  });

  it("redirects expired users to login", async () => {
    vi.mocked(useRouter).mockReturnValue(
      routerMock as unknown as ReturnType<typeof useRouter>,
    );

    const expiredUser = {
      expired: true,
      access_token: "expired-token",
    } as unknown as User;

    vi.mocked(getCurrentUser).mockResolvedValue(expiredUser);

    renderProtectedRoute();

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/login");
    });

    expect(
      screen.queryByText("Protected content"),
    ).not.toBeInTheDocument();
  });

  it("redirects to login when session restoration fails", async () => {
    vi.mocked(useRouter).mockReturnValue(
      routerMock as unknown as ReturnType<typeof useRouter>,
    );

    vi.mocked(getCurrentUser).mockRejectedValue(
      new Error("Session restoration failed"),
    );

    renderProtectedRoute();

    await waitFor(() => {
      expect(replaceMock).toHaveBeenCalledWith("/login");
    });

    expect(
      screen.queryByText("Protected content"),
    ).not.toBeInTheDocument();
  });
});
