import { describe, expect, it } from "vitest";

import { safeRedirectTarget } from "@/features/auth/redirect";

/**
 * Focused tests for the F6 redirect-safety policy (Batch 1.1).
 *
 * `safeRedirectTarget` validates the `redirectedFrom` query value that
 * AuthGuard attaches to `/login`. The policy pinned here is the
 * behavior the login flow has always had; Batch 1.1 aligned the
 * function's documentation with it and added these tests so any future
 * change to the policy is explicit and reviewed (the open-redirect
 * logic itself must not drift silently).
 */
describe("safeRedirectTarget", () => {
    describe("rejects unsafe targets", () => {
        it("rejects null (no redirectedFrom param)", () => {
            expect(safeRedirectTarget(null)).toBeNull();
        });

        it("rejects an empty value", () => {
            expect(safeRedirectTarget("")).toBeNull();
        });

        it("rejects an absolute external URL", () => {
            expect(safeRedirectTarget("https://evil.example/dashboard")).toBeNull();
        });

        it("rejects an absolute non-http scheme", () => {
            expect(safeRedirectTarget("javascript:alert(1)")).toBeNull();
        });

        it("rejects a protocol-relative URL (resolved against a foreign origin)", () => {
            expect(safeRedirectTarget("//evil.example/dashboard")).toBeNull();
        });

        it("rejects the login route itself (no login loops)", () => {
            expect(safeRedirectTarget("/login")).toBeNull();
        });

        it("rejects the login route with a query string", () => {
            expect(safeRedirectTarget("/login?redirectedFrom=/dashboard")).toBeNull();
        });

        it("rejects the register route", () => {
            expect(safeRedirectTarget("/register")).toBeNull();
        });

        it("rejects a nested auth-route path", () => {
            expect(safeRedirectTarget("/register/extra")).toBeNull();
        });

        it("rejects auth-route prefixes (prefix-based matching, documented as-is)", () => {
            expect(safeRedirectTarget("/login-page")).toBeNull();
        });
    });

    describe("accepts safe local in-app targets", () => {
        it("accepts the default dashboard deep link", () => {
            expect(safeRedirectTarget("/dashboard")).toBe("/dashboard");
        });

        it("accepts a plain local route", () => {
            expect(safeRedirectTarget("/courses")).toBe("/courses");
        });

        it("accepts a deep link with a dynamic segment", () => {
            expect(safeRedirectTarget("/courses/123")).toBe("/courses/123");
        });

        it("accepts a local route with a query string", () => {
            expect(safeRedirectTarget("/courses?page=2")).toBe("/courses?page=2");
        });

        it("accepts the profile route", () => {
            expect(safeRedirectTarget("/profile")).toBe("/profile");
        });
    });
});
