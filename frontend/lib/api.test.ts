import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Mock the config module so apiFetch uses a deterministic base URL and
// lib/config's Zod parse does not require real env vars at import time.
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

// Mock the Keycloak token helper so apiFetch does not touch keycloak-js.
// Use vi.hoisted so the mock factory can reference it safely (vi.mock
// factories are hoisted above all imports).
const { getAccessTokenMock } = vi.hoisted(() => ({
    getAccessTokenMock: vi.fn<() => Promise<string | null>>(),
}));

vi.mock("@/lib/keycloak", () => ({
    getAccessToken: getAccessTokenMock,
}));

import { apiFetch, ApiError } from "@/lib/api";
import { courseResponseSchema } from "@/features/courses/schemas";
import { z } from "zod";

const sampleCourse = {
    id: "550e8400-e29b-41d4-a716-446655440000",
    owner_id: "550e8400-e29b-41d4-a716-446655440001",
    title: "Intro to Testing",
    description: "A course about tests.",
    created_at: "2026-09-29T12:00:00.000Z",
};

const courseSchema = z.object({
    id: z.string().uuid(),
    owner_id: z.string().uuid(),
    title: z.string(),
    description: z.string().nullable(),
    created_at: z.string(),
});

beforeEach(() => {
    getAccessTokenMock.mockReset();
});

afterEach(() => {
    vi.restoreAllMocks();
});

describe("apiFetch — authentication", () => {
    it("throws ApiError with status 401 when no token is available", async () => {
        getAccessTokenMock.mockResolvedValue(null);

        await expect(apiFetch("/v1/courses")).rejects.toMatchObject({
            name: "ApiError",
            status: 401,
            message: "Not authenticated",
        });
    });

    it("does not call fetch when no token is available", async () => {
        getAccessTokenMock.mockResolvedValue(null);
        const fetchSpy = vi.spyOn(globalThis, "fetch");

        await expect(apiFetch("/v1/courses")).rejects.toBeInstanceOf(ApiError);
        expect(fetchSpy).not.toHaveBeenCalled();
    });
});

describe("apiFetch — successful responses", () => {
    it("attaches the bearer token and returns parsed JSON", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify(sampleCourse), {
                status: 200,
                headers: { "Content-Type": "application/json" },
            }),
        );

        const result = await apiFetch("/v1/courses/123");

        expect(fetchSpy).toHaveBeenCalledWith(
            "https://api.test.local/v1/courses/123",
            expect.objectContaining({
                method: "GET",
                headers: expect.objectContaining({
                    Authorization: "Bearer fake-token",
                }),
            }),
        );
        expect(result).toEqual(sampleCourse);
    });

    it("validates the response against the provided schema", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify(sampleCourse), {
                status: 200,
                headers: { "Content-Type": "application/json" },
            }),
        );

        const result = await apiFetch("/v1/courses/123", {
            schema: courseSchema,
        });

        expect(result).toEqual(sampleCourse);
    });

    it("serializes the body as JSON and sets Content-Type for POST", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify(sampleCourse), { status: 201 }),
        );

        await apiFetch("/v1/courses", {
            method: "POST",
            body: { title: "New Course", description: null },
        });

        const call = fetchSpy.mock.calls[0];
        expect(call[1]).toMatchObject({
            method: "POST",
            body: JSON.stringify({ title: "New Course", description: null }),
            headers: expect.objectContaining({
                "Content-Type": "application/json",
                Authorization: "Bearer fake-token",
            }),
        });
    });

    it("returns undefined for 204 No Content", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(null, { status: 204 }),
        );

        const result = await apiFetch("/v1/courses/123", {
            method: "DELETE",
        });

        expect(result).toBeUndefined();
    });
});

describe("apiFetch — error mapping", () => {
    it("throws ApiError with the HTTP status on a non-OK response", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify({ detail: "Course not found" }), {
                status: 404,
            }),
        );

        await expect(apiFetch("/v1/courses/missing")).rejects.toMatchObject({
            name: "ApiError",
            status: 404,
            message: "Course not found",
            body: { detail: "Course not found" },
        });
    });

    it("preserves the FastAPI detail message when present", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(
                JSON.stringify({
                    detail: [
                        {
                            loc: ["body", "title"],
                            msg: "field required",
                            type: "value_error.missing",
                        },
                    ],
                }),
                { status: 422 },
            ),
        );

        await expect(apiFetch("/v1/courses", { method: "POST", body: {} }))
            .rejects.toMatchObject({
                status: 422,
                message: expect.stringContaining("field required"),
            });
    });

    it("falls back to a status-derived message when body is not JSON", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response("Forbidden", { status: 403 }),
        );

        await expect(apiFetch("/v1/courses/123", { method: "PUT", body: {} }))
            .rejects.toMatchObject({
                status: 403,
                message: "Request failed with status 403",
                body: null,
            });
    });

    it("falls back to a generic message when body is empty", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(null, { status: 500 }),
        );

        await expect(apiFetch("/v1/courses")).rejects.toMatchObject({
            status: 500,
            message: "Request failed with status 500",
            body: null,
        });
    });

    it("throws ApiError with status 0 on a network failure", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockRejectedValue(
            new TypeError("Failed to fetch"),
        );

        await expect(apiFetch("/v1/courses")).rejects.toMatchObject({
            status: 0,
            message: expect.stringContaining("Network request failed"),
        });
    });

    it("throws ApiError with status 0 when schema validation fails", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify({ id: "not-a-uuid" }), { status: 200 }),
        );

        await expect(
            apiFetch("/v1/courses/123", { schema: courseSchema }),
        ).rejects.toMatchObject({
            status: 0,
            message: expect.stringContaining("schema validation failed"),
        });
    });
});

/**
 * Focused datetime-contract coverage (Batch 1.4 — F5 settlement).
 *
 * The tracked contract (`docs/openapi.json`) declares
 * `CourseResponse.created_at` as `format: date-time` (RFC 3339), so every
 * contract-valid value carries a timezone offset. The live API probe
 * (Batch 0.1 owner-machine run, 2026-10-14) observed exactly that: 5/5
 * values offset-bearing (sample `2026-10-14T15:52:48.551399Z`).
 * `courseResponseSchema` therefore keeps `z.string().datetime({
 * offset: true })` unchanged, which accepts both offset-bearing shapes —
 * the UTC `Z` form and an explicit `±HH:MM` offset — and rejects a naive
 * datetime instead of silently treating it as UTC. These tests pin that
 * settlement against the real response schema at the apiFetch boundary.
 */
const liveProbeCreatedAt = "2026-10-14T15:52:48.551399Z";

const offsetCreatedAt = "2026-10-14T18:52:48.551399+03:00";

const courseWithCreatedAt = (created_at: string) => ({
    id: "550e8400-e29b-41d4-a716-446655440000",
    owner_id: "550e8400-e29b-41d4-a716-446655440001",
    title: "Intro to Testing",
    description: "A course about tests.",
    created_at,
});

describe("courseResponseSchema — created_at datetime contract (F5)", () => {
    it("accepts the UTC Z shape observed from the live API", () => {
        const result = courseResponseSchema.safeParse(
            courseWithCreatedAt(liveProbeCreatedAt),
        );

        expect(result.success).toBe(true);
    });

    it("accepts an explicit ±HH:MM offset shape (date-time contract)", () => {
        const result = courseResponseSchema.safeParse(
            courseWithCreatedAt(offsetCreatedAt),
        );

        expect(result.success).toBe(true);
    });

    it("rejects a naive datetime without an offset (never coerced to UTC)", () => {
        const result = courseResponseSchema.safeParse(
            courseWithCreatedAt("2026-10-14T15:52:48"),
        );

        expect(result.success).toBe(false);
    });

    it("apiFetch validates a course list carrying both datetime shapes", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        const list = [
            courseWithCreatedAt(liveProbeCreatedAt),
            courseWithCreatedAt(offsetCreatedAt),
        ];
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify(list), {
                status: 200,
                headers: { "Content-Type": "application/json" },
            }),
        );

        const result = await apiFetch("/v1/courses", {
            schema: courseResponseSchema.array(),
        });

        expect(result).toEqual(list);
    });

    it("apiFetch throws a validation ApiError when created_at is naive", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(
                JSON.stringify(courseWithCreatedAt("2026-10-14T15:52:48")),
                { status: 200, headers: { "Content-Type": "application/json" } },
            ),
        );

        await expect(
            apiFetch("/v1/courses/123", { schema: courseResponseSchema }),
        ).rejects.toMatchObject({
            name: "ApiError",
            status: 0,
            message: expect.stringContaining("schema validation failed"),
        });
    });
});
