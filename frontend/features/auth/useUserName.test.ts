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
 */
describe("composeUserDisplayName", () => {
    it("composes first and last name with the initial of the first name", () => {
        expect(
            composeUserDisplayName({
                givenName: "Sara",
                familyName: "Hassan",
                email: "sara.hassan@example.com",
            }),
        ).toEqual({ name: "Sara Hassan", initial: "S" });
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
        ).toEqual({ name: "Layla", initial: "L" });
    });

    it("uses only the last name when the first name is missing", () => {
        expect(
            composeUserDisplayName({
                familyName: "Haddad",
                email: "haddad@example.com",
            }),
        ).toEqual({ name: "Haddad", initial: "H" });
    });

    it("treats blank and whitespace-only name fields as absent", () => {
        expect(
            composeUserDisplayName({
                givenName: "   ",
                familyName: "",
                email: "fallback@example.com",
            }),
        ).toEqual({ name: "fallback@example.com", initial: "F" });
    });

    it("trims surrounding whitespace from present name fields", () => {
        expect(
            composeUserDisplayName({
                givenName: "  Nour  ",
                familyName: "\tSaeed\n",
                email: "nour@example.com",
            }),
        ).toEqual({ name: "Nour Saeed", initial: "N" });
    });

    it("falls back to the email when no name fields exist", () => {
        expect(composeUserDisplayName({ email: "instructor@example.com" })).toEqual(
            { name: "instructor@example.com", initial: "I" },
        );
    });

    it("falls back to the established 'User' when nothing usable exists", () => {
        expect(composeUserDisplayName({})).toEqual({
            name: "User",
            initial: "U",
        });
        expect(
            composeUserDisplayName({ givenName: "", familyName: null }),
        ).toEqual({ name: "User", initial: "U" });
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
        ).toEqual({ name: "سارة حسن", initial: "س" });
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
});
