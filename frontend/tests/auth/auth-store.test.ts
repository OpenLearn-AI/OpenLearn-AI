import { describe, expect, it } from "vitest";
import type { User } from "oidc-client-ts";

import { useAuthStore } from "@/lib/auth-store";

describe("auth-store", () => {
  it("starts with an unknown authentication status", () => {
    const state = useAuthStore.getState();

    expect(state.status).toBe("unknown");
    expect(state.user).toBeNull();
  });

  it("sets the user as authenticated", () => {
    const user = {
      profile: {
        sub: "user-123",
        email: "test@example.com",
      },
      access_token: "test-access-token",
      token_type: "Bearer",
      expires_at: Math.floor(Date.now() / 1000) + 3600,
    } as unknown as User;

    useAuthStore.getState().setAuthenticated(user);

    const state = useAuthStore.getState();

    expect(state.status).toBe("authenticated");
    expect(state.user).toBe(user);
  });

  it("sets the user as unauthenticated", () => {
    useAuthStore.getState().setUnauthenticated();

    const state = useAuthStore.getState();

    expect(state.status).toBe("unauthenticated");
    expect(state.user).toBeNull();
  });

  it("returns to unknown status when checking starts", () => {
    useAuthStore.getState().setChecking();

    const state = useAuthStore.getState();

    expect(state.status).toBe("unknown");
  });
});
