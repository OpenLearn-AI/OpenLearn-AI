"use client";

import { useSyncExternalStore } from "react";

import { getInitializedKeycloak } from "@/lib/keycloak";
import { useMe } from "@/features/auth/api/useMe";
import {
    composeUserDisplayName,
    type UserDisplayIdentity,
} from "./user-identity";

/**
 * Shared display-name extraction (§9.1 — D2 component rule).
 *
 * Relocated from `components/UserName.tsx` in Batch 3.3 (roadmap W4);
 * the hook was a data hook, not a component, so it lives with the
 * auth feature's queries. SIDE-01 (2026-10-24) refined WHAT the
 * display name is, without changing the data sources or adding any
 * request:
 *
 * 1. The authenticated person's real name — the OIDC standard
 *    `given_name` / `family_name` claims of the session's ID token
 *    (the realm's `openlearn-frontend` default client scopes include
 *    `basic` + `profile`, which carry those claims when the user's
 *    Keycloak profile has names). The claims are read from the
 *    ALREADY-initialized Keycloak singleton via the passive
 *    `getInitializedKeycloak()` accessor — no new API request, no
 *    duplicate user state, no auth-flow change. The singleton is
 *    consumed as an external store with a stable snapshot (the
 *    instance reference), so the identity is derived during render
 *    with no state and no effect. Everywhere the singleton is not
 *    initialized (SSR, stories, tests) the snapshot is `null` and the
 *    hook deterministically falls back.
 * 2. Fallback — the existing established chain: `user.email` (the
 *    canonical `Me` response), then "User". When the ID token carries
 *    no usable name fields, the identity presentation keeps this
 *    established behavior rather than rendering `undefined`, `null`,
 *    or a broken empty element.
 *
 * An identifier (email local-part, preferred username) is NEVER
 * repurposed as a person's name — only real `given_name` /
 * `family_name` claims compose the person-name presentation. The pure
 * composition lives in `user-identity.ts` (unit-tested in isolation).
 *
 * Display rules (SIDE-01): the expanded identity shows first and last
 * name ("First Last"; one missing name degrades gracefully to the one
 * that exists), and the collapsed avatar's initial is derived from the
 * composed display value's first character — i.e. the first name's
 * first letter whenever a first name exists.
 *
 * Consumers read the exported `useUserName` hook.
 */

/** Reads a string claim defensively from the parsed ID token. */
function readClaim(value: unknown): string | undefined {
    return typeof value === "string" ? value : undefined;
}

/** The singleton's claims are session-stable; no subscription exists. */
const subscribeToKeycloak = () => () => {};

/** Server snapshot: there is no Keycloak instance outside the browser. */
const getServerKeycloak = () => null;

export function useUserName(): UserDisplayIdentity & {
    isLoading: boolean;
} {
    const { data: user, isLoading } = useMe();

    // AuthGuard renders the shell only after `AuthProvider`'s init has
    // resolved, so inside the guarded shell this snapshot is the live,
    // authenticated instance on the very first render — no fallback
    // flash. The instance reference is stable across calls, so React's
    // snapshot-consistency check cannot loop.
    const keycloak = useSyncExternalStore(
        subscribeToKeycloak,
        getInitializedKeycloak,
        getServerKeycloak,
    );
    const claims = keycloak?.idTokenParsed;

    return {
        ...composeUserDisplayName({
            givenName: readClaim(claims?.given_name),
            familyName: readClaim(claims?.family_name),
            email: user?.email,
        }),
        isLoading,
    };
}
