import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the config module: session-recovery imports ApiError from
// lib/api, which imports lib/config — lib/config's Zod parse requires
// real env vars at import time, which unit tests do not have (same
// pattern as lib/api.test.ts).
vi.mock("@/lib/config", () => ({
    config: {
        apiUrl: "https://api.test.local",
        keycloak: {
            url: "https://kc.test.local",
            realm: "openlearn",
            clientId: "openlearn-frontend",
        },
        sentryDsn: null,
        sentryEnvironment: "development",
    },
}));

import { ApiError } from "@/lib/api";
import {
    currentLocationPath,
    isSessionExpiredError,
    sessionRecoveryTarget,
} from "@/lib/session-recovery";

describe("isSessionExpiredError", () => {
    it("accepts an ApiError with status 401", () => {
        expect(isSessionExpiredError(new ApiError(401, "Not authenticated"))).toBe(
            true,
        );
    });

    it("rejects ApiErrors with other statuses (network, 403, 404, 500)", () => {
        expect(isSessionExpiredError(new ApiError(0, "Network request failed"))).toBe(
            false,
        );
        expect(
            isSessionExpiredError(new ApiError(403, "Forbidden")),
        ).toBe(false);
        expect(isSessionExpiredError(new ApiError(404, "Not found"))).toBe(
            false,
        );
        expect(
            isSessionExpiredError(new ApiError(500, "Server error")),
        ).toBe(false);
    });

    it("rejects non-ApiError values (Error, string, null, undefined, object)", () => {
        expect(isSessionExpiredError(new Error("generic"))).toBe(false);
        expect(isSessionExpiredError("Not authenticated")).toBe(false);
        expect(isSessionExpiredError(null)).toBe(false);
        expect(isSessionExpiredError(undefined)).toBe(false);
        expect(isSessionExpiredError({ status: 401 })).toBe(false);
    });
});

describe("sessionRecoveryTarget", () => {
    it("carries a plain deep link as redirectedFrom", () => {
        expect(sessionRecoveryTarget("/dashboard")).toBe(
            "/login?redirectedFrom=%2Fdashboard",
        );
    });

    it("encodes a deep link with a query string", () => {
        expect(sessionRecoveryTarget("/courses?title=ai")).toBe(
            "/login?redirectedFrom=%2Fcourses%3Ftitle%3Dai",
        );
    });

    it("carries the root path", () => {
        expect(sessionRecoveryTarget("/")).toBe(
            "/login?redirectedFrom=%2F",
        );
    });

    it("carries an empty path as an empty redirectedFrom", () => {
        expect(sessionRecoveryTarget("")).toBe("/login?redirectedFrom=");
    });
});

describe("currentLocationPath (no window)", () => {
    it("falls back to / when no window exists (SSR / node tests)", () => {
        expect(currentLocationPath()).toBe("/");
    });
});

describe("triggerSessionRecovery", () => {
    // The recovery latches at most once per module lifetime; each test
    // reloads the module with vi.resetModules so it starts un-latched.
    async function loadFreshModule() {
        vi.resetModules();
        return await import("@/lib/session-recovery");
    }

    beforeEach(() => {
        vi.unstubAllGlobals();
    });

    it("clears the cache, then routes to /login with redirectedFrom", async () => {
        const { triggerSessionRecovery } = await loadFreshModule();

        const clearCache = vi.fn();
        const redirect = vi.fn();

        triggerSessionRecovery({
            clearCache,
            redirect,
            currentPath: "/dashboard",
        });

        expect(clearCache).toHaveBeenCalledTimes(1);
        expect(redirect).toHaveBeenCalledTimes(1);
        expect(redirect).toHaveBeenCalledWith(
            "/login?redirectedFrom=%2Fdashboard",
        );
        expect(clearCache.mock.invocationCallOrder[0]).toBeLessThan(
            redirect.mock.invocationCallOrder[0],
        );
    });

    it("uses the current window location when no path is supplied", async () => {
        const { triggerSessionRecovery } = await loadFreshModule();

        const assign = vi.fn();
        vi.stubGlobal("window", {
            location: { assign, pathname: "/courses", search: "?page=2" },
        });

        triggerSessionRecovery();

        expect(assign).toHaveBeenCalledTimes(1);
        expect(assign).toHaveBeenCalledWith(
            "/login?redirectedFrom=%2Fcourses%3Fpage%3D2",
        );
    });

    it("is a no-op without a window and without an injected redirect", async () => {
        const { triggerSessionRecovery } = await loadFreshModule();

        expect(() => triggerSessionRecovery()).not.toThrow();
    });

    it("ignores subsequent triggers for the lifetime of the page", async () => {
        const { triggerSessionRecovery } = await loadFreshModule();

        const firstRedirect = vi.fn();
        const secondRedirect = vi.fn();
        const clearCache = vi.fn();

        triggerSessionRecovery({ clearCache, redirect: firstRedirect });
        triggerSessionRecovery({ redirect: secondRedirect });

        expect(firstRedirect).toHaveBeenCalledTimes(1);
        expect(secondRedirect).not.toHaveBeenCalled();
        expect(clearCache).toHaveBeenCalledTimes(1);
    });
});
