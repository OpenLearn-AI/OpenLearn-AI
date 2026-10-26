import { describe, expect, it } from "vitest";

import {
    clearOidcAttempt,
    hasOidcAttempt,
    markOidcAttempt,
} from "./oidc-attempt";

/**
 * Unit coverage for the OIDC attempt marker (Batch 4.1 corrective
 * follow-up §C.4). The unit project runs in plain Node (no DOM), so
 * what is pinned here is the SSR/storage-absent guard: every helper is
 * a safe no-op when `window` is undefined — the same code path a
 * server render takes. The marker's real loop-breaking behavior is
 * exercised in the browser layer (Storybook interaction tests render
 * the entry bridge's manual state from a seeded marker, and the E2E
 * suite drives the real flow).
 */
describe("oidc-attempt (SSR guard)", () => {
    it("markOidcAttempt is a no-op without a window", () => {
        expect(() => markOidcAttempt("login")).not.toThrow();
        expect(() => markOidcAttempt("register")).not.toThrow();
    });

    it("hasOidcAttempt reports false without a window", () => {
        expect(hasOidcAttempt("login")).toBe(false);
        expect(hasOidcAttempt("register")).toBe(false);
    });

    it("clearOidcAttempt is a no-op without a window", () => {
        expect(() => clearOidcAttempt("login")).not.toThrow();
    });
});
