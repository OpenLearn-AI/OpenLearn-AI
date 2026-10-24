/**
 * Pure display-identity composition (SIDE-01).
 *
 * Deliberately free of any import: no config, no Keycloak adapter, no
 * React — the same module-isolation pattern as the onboarding
 * `gate-state.ts`, so the composition is unit-testable in the plain
 * node vitest project without dragging the env-gated client
 * configuration into the test environment.
 *
 * Contract: person name first (first + last, tolerant of missing or
 * blank parts), then the established fallback chain `email` → "User".
 * The avatar initial is always the composed display value's first
 * character — the first name's first letter whenever a first name
 * exists, never `undefined`, `null`, or an empty label.
 */

/** A display name with its avatar initial, derived from one source. */
export interface UserDisplayIdentity {
    /** The visible identity label (person name, else the fallback). */
    name: string;
    /** Single-character avatar initial derived from `name`. */
    initial: string;
}

/**
 * Compose the visible identity from the available fields.
 *
 * `givenName` / `familyName` are the raw claim values (may be
 * `undefined`, blank, or whitespace-only — all treated as absent).
 * An identifier (email local-part, preferred username) is never
 * repurposed as a person's name: the email is only ever the
 * established fallback, never the source of a person-name
 * presentation.
 */
export function composeUserDisplayName(fields: {
    givenName?: string | null;
    familyName?: string | null;
    email?: string | null;
}): UserDisplayIdentity {
    const given = fields.givenName?.trim() ?? "";
    const family = fields.familyName?.trim() ?? "";
    const email = fields.email?.trim() ?? "";

    const personName = [given, family].filter(Boolean).join(" ");
    const name = personName || email || "User";
    const initial = name.charAt(0).toUpperCase();

    return { name, initial };
}
