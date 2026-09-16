import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { logout } from "@/lib/auth";

const mockSignoutRedirect = vi.fn();

vi.mock("@/lib/oidc", () => ({
  createUserManager: () => ({
    signoutRedirect: mockSignoutRedirect,
  }),
}));

describe("logout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("starts the OIDC logout flow", async () => {
    mockSignoutRedirect.mockResolvedValue(undefined);

    await logout();

    expect(mockSignoutRedirect).toHaveBeenCalledTimes(1);
  });

  it("propagates logout errors", async () => {
    const error = new Error("Logout failed");

    mockSignoutRedirect.mockRejectedValue(error);

    await expect(logout()).rejects.toThrow("Logout failed");

    expect(mockSignoutRedirect).toHaveBeenCalledTimes(1);
  });
});