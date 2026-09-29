"use client";

import { useMe } from "@/features/auth/api/useMe";

/**
 * Shared UserName extraction (§9.1 — D2 component rule).
 *
 * The architecture document identified that `app/page.tsx`,
 * `app/profile/page.tsx`, and `components/Navbar.tsx` each
 * re-implemented the "email-or-fallback plus initial computation"
 * — three duplications of the same logic. This component extracts
 * that logic into a single shared component.
 *
 * Display name = `user.email` (from the canonical `Me` response).
 * Fallback = "User" when no usable email is available.
 *
 * The component is presentational: it reads `useMe()` and renders
 * the display name. Callers that need just the raw string can use
 * the exported `useUserName` hook instead.
 */

export function useUserName(): {
    name: string;
    initial: string;
    isLoading: boolean;
} {
    const { data: user, isLoading } = useMe();

    const name = user?.email || "User";
    const initial =
        typeof name === "string"
            ? name.charAt(0).toUpperCase()
            : "U";

    return { name, initial, isLoading };
}
