import { describe, expect, it } from "vitest";

import { composeUserDisplayName } from "./user-identity";

/**
 * Unit tests for the SIDE-01 identity composition (pure helper).
 *
 * The hook's data sources are unchanged (`useMe` + the already
 * initialized Keycloak singleton), so what is pinned here is the
 * composition contract: person name first (first + last, tolerant of
 * missing/blank parts), the established email → "User" fallback, and
 * an initial always derived from the composed display value's first
 * character — never `undefined`, `null`, or an empty label.
 *
 * Batch 4.2 also pins `firstName` — the greeting source (owner
 * correction D): the trimmed `given_name` ALONE, "" when absent,
 * never an identifier fallback, never the full composed name (the
 * plain "Welcome Back!" greeting renders when it is empty).
 */
describe("composeUserDisplayName", () => {
    it("composes first and last name with the initial of the first name", () => {
        expect(
            composeUserDisplayName({
                givenName: "Sara",
                familyName: "Hassan",
                email: "sara.hassan@example.com",
            }),
        ).toEqual({ name: "Sara Hassan", initial: "S", firstName: "Sara" });
    });

    it("does not derive the initial from the email when a first name exists", () => {
        const identity = composeUserDisplayName({
            givenName: "Omar",
            familyName: "Khaled",
            email: "okhaled@university.edu",
        });

        expect(identity.initial).toBe("O");
        expect(identity.name).not.toContain("@");
    });

    it("uses only the first name when the last name is missing", () => {
        expect(
            composeUserDisplayName({
                givenName: "Layla",
                email: "layla@example.com",
            }),
        ).toEqual({ name: "Layla", initial: "L", firstName: "Layla" });
    });

    it("uses only the last name when the first name is missing", () => {
        expect(
            composeUserDisplayName({
                familyName: "Haddad",
                email: "haddad@example.com",
            }),
        ).toEqual({ name: "Haddad", initial: "H", firstName: "" });
    });

    it("treats blank and whitespace-only name fields as absent", () => {
        expect(
            composeUserDisplayName({
                givenName: "   ",
                familyName: "",
                email: "fallback@example.com",
            }),
        ).toEqual({ name: "fallback@example.com", initial: "F", firstName: "" });
    });

    it("trims surrounding whitespace from present name fields", () => {
        expect(
            composeUserDisplayName({
                givenName: "  Nour  ",
                familyName: "\tSaeed\n",
                email: "nour@example.com",
            }),
        ).toEqual({ name: "Nour Saeed", initial: "N", firstName: "Nour" });
    });

    it("falls back to the email when no name fields exist", () => {
        expect(composeUserDisplayName({ email: "instructor@example.com" })).toEqual(
            { name: "instructor@example.com", initial: "I", firstName: "" },
        );
    });

    it("falls back to the established 'User' when nothing usable exists", () => {
        expect(composeUserDisplayName({})).toEqual({
            name: "User",
            initial: "U",
            firstName: "",
        });
        expect(
            composeUserDisplayName({ givenName: "", familyName: null }),
        ).toEqual({ name: "User", initial: "U", firstName: "" });
    });

    it("never renders undefined, null, or an empty label", () => {
        for (const fields of [
            {},
            { givenName: undefined, familyName: undefined, email: undefined },
            { givenName: "  ", familyName: "  ", email: " " },
        ]) {
            const identity = composeUserDisplayName(fields);
            expect(identity.name.length).toBeGreaterThan(0);
            expect(identity.name).not.toBe("undefined");
            expect(identity.name).not.toBe("null");
            expect(identity.initial).toMatch(/^\S/u);
        }
    });

    it("derives the initial from Arabic first names safely", () => {
        expect(
            composeUserDisplayName({
                givenName: "سارة",
                familyName: "حسن",
                email: "sara@example.com",
            }),
        ).toEqual({ name: "سارة حسن", initial: "س", firstName: "سارة" });
    });

    it("uppercases a lowercase first letter for the initial", () => {
        expect(
            composeUserDisplayName({
                givenName: "adam",
                familyName: "Smith",
                email: "adam@example.com",
            }).initial,
        ).toBe("A");
    });

    it("Batch 4.2 (greeting): firstName is the given name alone, trimmed", () => {
        expect(
            composeUserDisplayName({
                givenName: "  Muhammad  ",
                familyName: "Seyam",
                email: "muhammad@example.com",
            }).firstName,
        ).toBe("Muhammad");
    });

    it("Batch 4.2 (greeting): firstName NEVER falls back to an identifier or the full name", () => {
        // No given name but an email exists → "", NOT the email or its
        // local part (SIDE-01: identifiers are never person names).
        expect(
            composeUserDisplayName({ email: "instructor@example.com" }).firstName,
        ).toBe("");
        // Only a family name exists → "", NOT the last name.
        expect(
            composeUserDisplayName({ familyName: "Haddad" }).firstName,
        ).toBe("");
        // Nothing at all → "", NOT "User".
        expect(composeUserDisplayName({}).firstName).toBe("");
    });

    it("Batch 4.2 (greeting): firstName with an Arabic given name is passed through verbatim", () => {
        expect(
            composeUserDisplayName({
                givenName: "محمد",
                email: "m@example.com",
            }).firstName,
        ).toBe("محمد");
    });
});
