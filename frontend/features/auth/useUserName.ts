"use client";

import { useMe } from "@/features/auth/api/useMe";

/**
 * Shared display-name extraction (§9.1 — D2 component rule).
 *
 * Relocated from `components/UserName.tsx` in Batch 3.3 (roadmap W4):
 * the hook was a data hook, not a component, so it lives with the
 * auth feature's queries. Its return contract and runtime behavior
 * are unchanged — this is a pure relocation, not a rewrite.
 *
 * History: the architecture document identified that `app/page.tsx`,
 * `app/profile/page.tsx`, and `components/Navbar.tsx` each
 * re-implemented the "email-or-fallback plus initial computation"
 * — three duplications of the same logic. This hook extracts
 * that logic into a single shared source of truth.
 *
 * Display name = `user.email` (from the canonical `Me` response).
 * Fallback = "User" when no usable email is available (loading or
 * error states surface this fallback, per the original contract).
 *
 * Consumers read the exported `useUserName` hook; the old
 * `components/UserName.tsx` file was removed with the relocation.
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
