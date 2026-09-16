import { create } from "zustand";
import type { User } from "oidc-client-ts";

type AuthStatus =
  | "unknown"
  | "authenticated"
  | "unauthenticated";

interface AuthState {
  status: AuthStatus;
  user: User | null;

  setAuthenticated: (user: User) => void;
  setUnauthenticated: () => void;
  setChecking: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: "unknown",
  user: null,

  setAuthenticated: (user) =>
    set({
      status: "authenticated",
      user,
    }),

  setUnauthenticated: () =>
    set({
      status: "unauthenticated",
      user: null,
    }),

  setChecking: () =>
    set({
      status: "unknown",
    }),
}));