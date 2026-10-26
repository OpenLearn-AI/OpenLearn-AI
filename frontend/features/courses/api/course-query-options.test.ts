import { describe, expect, it, vi } from "vitest";

// Mock config + keycloak so the query options' queryFn can be called
// without touching the real environment.
vi.mock("@/lib/config", () => ({
    config: {
        apiUrl: "https://api.test.local",
        keycloak: {
            url: "https://kc.test.local",
            realm: "openlearn",
            clientId: "openlearn-frontend",
        },
        sentryDsn: null,
    },
}));

const { getAccessTokenMock } = vi.hoisted(() => ({
    getAccessTokenMock: vi.fn<() => Promise<string | null>>(),
}));

vi.mock("@/lib/keycloak", () => ({
    getAccessToken: getAccessTokenMock,
}));

import type { Course } from "@/features/courses/schemas";
import { coursesListOptions } from "@/features/courses/api/useCourses";
import {
    courseDetailOptions,
} from "@/features/courses/api/useCourse";
import { courseKeys } from "@/features/courses/keys";
import type { QueryFunction, QueryFunctionContext } from "@tanstack/react-query";

const sampleCourse: Course = {
    id: "550e8400-e29b-41d4-a716-446655440000",
    owner_id: "550e8400-e29b-41d4-a716-446655440001",
    title: "Test Course",
    description: "A test.",
    created_at: "2026-09-29T12:00:00.000Z",
};

// Helper: invoke a queryFn that ignores its context (all apiFetch-based
// query functions take zero user-facing arguments).
async function invokeQueryFn<TData, TQueryKey extends readonly unknown[]>(
    fn: QueryFunction<TData, TQueryKey> | undefined,
): Promise<TData> {
    if (!fn) throw new Error("queryFn is undefined");
    return fn({} as QueryFunctionContext<TQueryKey>);
}

describe("coursesListOptions — query options shape (D5)", () => {
    it("uses the courseKeys.lists() key", () => {
        expect(coursesListOptions.queryKey).toEqual(courseKeys.lists());
    });

    it("has a queryFn that returns Course[]", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");

        const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify([sampleCourse]), { status: 200 }),
        );

        const result = await invokeQueryFn(coursesListOptions.queryFn);

        expect(fetchSpy).toHaveBeenCalledWith(
            "https://api.test.local/v1/courses",
            expect.objectContaining({
                method: "GET",
                headers: expect.objectContaining({
                    Authorization: "Bearer fake-token",
                }),
            }),
        );
        expect(result).toEqual([sampleCourse]);
        expect(result[0]).toHaveProperty("id");
        expect(result[0]).toHaveProperty("title");
    });
});

describe("courseDetailOptions(courseId) — per-id query options (D5)", () => {
    it("uses the courseKeys.detail(id) key", () => {
        expect(courseDetailOptions("abc").queryKey).toEqual(
            courseKeys.detail("abc"),
        );
    });

    it("produces different keys for different IDs", () => {
        expect(courseDetailOptions("abc").queryKey).not.toEqual(
            courseDetailOptions("def").queryKey,
        );
    });

    it("has a queryFn that fetches a single course", async () => {
        getAccessTokenMock.mockResolvedValue("fake-token");

        const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify(sampleCourse), { status: 200 }),
        );

        const result = await invokeQueryFn(
            courseDetailOptions("abc").queryFn,
        );

        expect(fetchSpy).toHaveBeenCalledWith(
            "https://api.test.local/v1/courses/abc",
            expect.objectContaining({
                method: "GET",
                headers: expect.objectContaining({
                    Authorization: "Bearer fake-token",
                }),
            }),
        );
        expect(result).toEqual(sampleCourse);
    });
});
