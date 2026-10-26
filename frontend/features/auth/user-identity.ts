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
 *
 * Batch 4.2 adds `firstName`: the person's first name ALONE (the
 * trimmed `given_name` claim), for the personalized dashboard
 * greeting. It is "" when no first name exists — it NEVER falls back
 * to an identifier (email, username) or to the composed display
 * name, so the greeting can keep its plain "Welcome Back!" wording
 * whenever a first name is genuinely unavailable (the owner's
 * correction D: no full name where the first name satisfies it, no
 * awkward empty-name rendering).
 */

/** A display name with its avatar initial, derived from one source. */
export interface UserDisplayIdentity {
    /** The visible identity label (person name, else the fallback). */
    name: string;
    /** Single-character avatar initial derived from `name`. */
    initial: string;
    /** The person's first name alone; "" when absent (never an
     * identifier fallback and never the full composed name). */
    firstName: string;
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

    return { name, initial, firstName: given };
}

/** The personalized welcome greeting (Batch 4.2 corrections, A3):
 * the composed text plus the isolated name segment the heading
 * renders with `dir="auto"` (empty when no first name exists). */
export interface WelcomeGreeting {
    /** The full greeting text — the heading's accessible name. */
    text: string;
    /** The name as presented (casing normalized); "" when absent. */
    name: string;
}

/**
 * Present a first name for the greeting — display casing only, never
 * a change to the stored account data.
 *
 * Keycloak profiles commonly carry an all-lowercase given name
 * (`muhammad`); the greeting presents it as a name ("Muhammad").
 * Cased scripts without a capitalization concept (e.g. Arabic) pass
 * through unchanged — `toUpperCase` is a no-op on them.
 */
export function presentFirstName(firstName: string): string {
    const trimmed = firstName.trim();
    if (trimmed === "") {
        return "";
    }
    return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}

/**
 * Compose the dashboard greeting (Batch 4.2 corrections, A3).
 *
 * Structure: "Welcome back, <Name>!" — the exclamation mark follows
 * the name; without a first name the plain "Welcome back!" renders
 * alone (no dangling comma, no empty-name gap). The name is the
 * authenticated user's available first name (`firstName` — never an
 * identifier fallback, never the composed full name), with display
 * casing applied; the composition stays in this pure module so the
 * punctuation contract is unit-testable without a session.
 */
export function composeWelcomeGreeting(
    firstName: string,
): WelcomeGreeting {
    const name = presentFirstName(firstName);

    return name === ""
        ? { text: "Welcome back!", name: "" }
        : { text: `Welcome back, ${name}!`, name };
}
