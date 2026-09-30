import { describe, expect, it } from "vitest";

import { courseKeys } from "@/features/courses/keys";

describe("courseKeys — stability and hierarchy", () => {
    it("exposes a stable `all` root", () => {
        expect(courseKeys.all).toEqual(["courses"]);
        // Same reference every time (no array rebuild).
        expect(courseKeys.all).toBe(courseKeys.all);
    });

    it("list keys are distinguishable from detail keys", () => {
        expect(courseKeys.lists()).toEqual(["courses", "list"]);
        expect(courseKeys.details()).toEqual(["courses", "detail"]);

        // A list key never collides with a detail key.
        expect(courseKeys.lists()).not.toEqual(courseKeys.details());
    });

    it("detail keys are per-id and nested under details", () => {
        expect(courseKeys.detail("abc")).toEqual([
            "courses",
            "detail",
            "abc",
        ]);
        expect(courseKeys.detail("abc")).not.toEqual(
            courseKeys.detail("def"),
        );
    });

    it("supports the invalidation strategy", () => {
        // After a create/update, invalidating `courseKeys.lists()` must
        // match the list query key, but must NOT match a detail key
        // (because invalidation is prefix-based in TanStack Query).
        const listKey = courseKeys.lists();
        const detailKey = courseKeys.detail("abc");

        // listKey is a prefix of any list() query key, so
        // invalidateQueries({ queryKey: listKey }) matches all list queries.
        // A detail key is NOT prefixed by listKey because the second
        // element differs ("detail" vs "list"), so invalidating lists()
        // does NOT touch detail queries.
        expect(detailKey[0]).toBe(listKey[0]); // "courses" root matches
        expect(detailKey[1]).not.toBe(listKey[1]); // "detail" != "list"
    });

    it("list(filters) produces filter-scoped keys under lists()", () => {
        expect(courseKeys.list()).toEqual(["courses", "list", {}]);
        expect(courseKeys.list({ search: "math" })).toEqual([
            "courses",
            "list",
            { search: "math" },
        ]);
        // Different filters produce different keys.
        expect(courseKeys.list({ search: "math" })).not.toEqual(
            courseKeys.list({ search: "cs" }),
        );
    });
});
