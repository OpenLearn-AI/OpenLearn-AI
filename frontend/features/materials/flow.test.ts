import { describe, expect, it, vi } from "vitest";

// Mock the config module so the ApiError import chain (lib/api →
// lib/config) does not require real env vars at import time — the
// same hermeticity pattern as lib/api.test.ts.
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

vi.mock("@/lib/keycloak", () => ({
    getAccessToken: vi.fn(async () => "test-token"),
}));

import { ApiError } from "@/lib/api";
import {
    buildUploadFormData,
    describeMaterialFlowError,
    describeMaterialPagesError,
    describeMaterialProcessError,
    formatByteSize,
    isTerminalMaterialStatus,
    MATERIAL_EMPTY_PAGE_COPY,
    MATERIAL_FAILED_COPY,
    MATERIAL_NO_PAGES_COPY,
    MATERIAL_PROCESS_ACCEPTED_COPY,
    MATERIAL_STATUS_LABELS,
    materialPageLabel,
    mayHaveMorePages,
} from "./flow";
import { materialKeys } from "./keys";
import { materialPagesResponseSchema } from "./schemas";

/**
 * Unit tests for the Batch 4.3 material flow helpers (pure module —
 * the same isolation pattern as user-identity/gate-state), extended
 * in Batch 4.5 for the extracted-text viewer and the reprocess
 * control.
 *
 * What is pinned: the presigned-POST form-data construction (signed
 * fields FIRST, the file LAST under the contract's `file` name — the
 * order the UploadUrlResponse documents), the terminal-status
 * predicate that drives polling shutdown, the honest error mapping,
 * and the status label vocabulary (the contract's four literals —
 * never a phase name or percentage). Batch 4.5 adds: the Week 9
 * page-list response shape, the pages key branch, the page labels
 * and the honest pagination predicate, the exact viewer/reprocess
 * copy, and both documented 409 classes' honest mapping.
 */

describe("buildUploadFormData", () => {
    it("appends every signed field first and the file LAST", () => {
        const file = new File(["hello"], "lecture-1.pdf", {
            type: "application/pdf",
        });
        const formData = buildUploadFormData(
            {
                key: "courses/x/materials/y",
                "x-amz-algorithm": "AWS4-HMAC-SHA256",
                policy: "abc",
            },
            file,
        );

        const entries = [...formData.entries()];
        expect(entries.map(([name]) => name)).toEqual([
            "key",
            "x-amz-algorithm",
            "policy",
            "file",
        ]);
        expect(formData.get("key")).toBe("courses/x/materials/y");
        expect(formData.get("file")).toBe(file);
    });

    it("sends no fields when the policy carries none — the file is still last", () => {
        const file = new File(["x"], "a.txt", { type: "text/plain" });
        const formData = buildUploadFormData({}, file);

        expect([...formData.keys()]).toEqual(["file"]);
    });
});

describe("isTerminalMaterialStatus", () => {
    it("ready and failed are terminal", () => {
        expect(isTerminalMaterialStatus("ready")).toBe(true);
        expect(isTerminalMaterialStatus("failed")).toBe(true);
    });

    it("pending and processing are NOT terminal (polling continues)", () => {
        expect(isTerminalMaterialStatus("pending")).toBe(false);
        expect(isTerminalMaterialStatus("processing")).toBe(false);
    });
});

describe("formatByteSize", () => {
    it("renders binary units for the storage limit messages", () => {
        expect(formatByteSize(10 * 1024 * 1024)).toBe("10 MB");
        expect(formatByteSize(512)).toBe("512 bytes");
        expect(formatByteSize(2048)).toBe("2 KB");
        expect(formatByteSize(10.5 * 1024 * 1024)).toBe("10.5 MB");
    });
});

describe("MATERIAL_STATUS_LABELS", () => {
    it("covers exactly the contract's four statuses with honest copy", () => {
        expect(Object.keys(MATERIAL_STATUS_LABELS).sort()).toEqual([
            "failed",
            "pending",
            "processing",
            "ready",
        ]);
        expect(MATERIAL_STATUS_LABELS.pending).toBe("Queued");
        expect(MATERIAL_STATUS_LABELS.processing).toBe("Processing");
        expect(MATERIAL_STATUS_LABELS.ready).toBe("Ready");
        expect(MATERIAL_STATUS_LABELS.failed).toBe("Failed");
    });

    it("the failed copy names the plausible cause class without claiming the exact cause", () => {
        expect(MATERIAL_FAILED_COPY).toContain("OCR");
        expect(MATERIAL_FAILED_COPY).not.toContain("%");
    });
});

describe("describeMaterialFlowError", () => {
    it("maps the contract's documented statuses to honest copy", () => {
        expect(
            describeMaterialFlowError(new ApiError(403, "nope")),
        ).toBe(
            "You do not have permission to manage materials in this course.",
        );
        expect(describeMaterialFlowError(new ApiError(429, "slow down"))).toBe(
            "Too many requests. Please wait a moment and try again.",
        );
        expect(describeMaterialFlowError(new ApiError(422, "bad"))).toBe(
            "The submitted values are invalid.",
        );
        // The API's own detail wins when it is more specific (409/413
        // carry backend-composed messages).
        expect(
            describeMaterialFlowError(
                new ApiError(413, "Stored object exceeds the maximum upload size of 10485760 bytes"),
            ),
        ).toContain("maximum upload size");
    });

    it("falls back to the error message for unexpected statuses", () => {
        expect(describeMaterialFlowError(new ApiError(500, "boom"))).toBe(
            "boom",
        );
        expect(describeMaterialFlowError(new Error("offline"))).toBe(
            "offline",
        );
        expect(describeMaterialFlowError("mystery")).toBe(
            "The upload could not be completed.",
        );
    });
});

describe("materialKeys (D5 convention)", () => {
    it("builds hierarchical keys under one root", () => {
        expect(materialKeys.all).toEqual(["materials"]);
        expect(materialKeys.list("course-1")).toEqual([
            "materials",
            "list",
            "course-1",
        ]);
        expect(materialKeys.status("material-1")).toEqual([
            "materials",
            "status",
            "material-1",
        ]);
    });

    it("nests the 4.5 pages branch under the same root (prefix-invalidatable)", () => {
        expect(materialKeys.pages("material-1")).toEqual([
            "materials",
            "pages",
            "material-1",
        ]);
    });
});

/* -------------------------------------------------------------------------
 * Batch 4.5 — the extracted-text viewer and the reprocess control.
 * ---------------------------------------------------------------------- */

describe("materialPagesResponseSchema (Week 9 contract)", () => {
    const materialId = "660e8400-e29b-41d4-a716-446655440200";

    it("accepts the contract's page-list shape, including empty text pages", () => {
        const parsed = materialPagesResponseSchema.safeParse({
            material_id: materialId,
            pages: [
                { page_number: 1, text: "Introduction to the course." },
                { page_number: 2, text: "" },
                { page_number: 3, text: "التعلم الآلي — مقدمة قصيرة." },
            ],
        });

        expect(parsed.success).toBe(true);
        if (parsed.success) {
            expect(parsed.data.pages).toHaveLength(3);
            expect(parsed.data.pages[1]?.text).toBe("");
        }
    });

    it("accepts the honest empty page list (empty until processed)", () => {
        const parsed = materialPagesResponseSchema.safeParse({
            material_id: materialId,
            pages: [],
        });

        expect(parsed.success).toBe(true);
    });

    it("rejects 0-based page numbers, non-uuid material ids, and non-string text", () => {
        expect(
            materialPagesResponseSchema.safeParse({
                material_id: materialId,
                pages: [{ page_number: 0, text: "x" }],
            }).success,
        ).toBe(false);

        expect(
            materialPagesResponseSchema.safeParse({
                material_id: "not-a-uuid",
                pages: [{ page_number: 1, text: "x" }],
            }).success,
        ).toBe(false);

        expect(
            materialPagesResponseSchema.safeParse({
                material_id: materialId,
                pages: [{ page_number: 1, text: 42 }],
            }).success,
        ).toBe(false);
    });

    it("rejects a missing pages array (the field is required)", () => {
        expect(
            materialPagesResponseSchema.safeParse({
                material_id: materialId,
            }).success,
        ).toBe(false);
    });
});

describe("materialPageLabel", () => {
    it("labels pages exactly as the contract numbers them (1-based)", () => {
        expect(materialPageLabel(1)).toBe("Page 1");
        expect(materialPageLabel(2)).toBe("Page 2");
        expect(materialPageLabel(42)).toBe("Page 42");
    });
});

describe("mayHaveMorePages (honest pagination — no invented totals)", () => {
    it("offers more ONLY when a window came back full", () => {
        expect(mayHaveMorePages(100, 100)).toBe(true);
        expect(mayHaveMorePages(99, 100)).toBe(false);
        expect(mayHaveMorePages(1, 100)).toBe(false);
    });

    it("an empty window is the last window", () => {
        expect(mayHaveMorePages(0, 100)).toBe(false);
    });
});

describe("viewer and reprocess copy (pinned exactly)", () => {
    it("the empty states name exactly what is absent — no invented causes", () => {
        expect(MATERIAL_NO_PAGES_COPY).toBe(
            "No extracted text stored for this material yet.",
        );
        expect(MATERIAL_EMPTY_PAGE_COPY).toBe(
            "This page has no extractable text.",
        );
    });

    it("the acceptance copy states the 202's own meaning, never a fabricated processing state", () => {
        expect(MATERIAL_PROCESS_ACCEPTED_COPY).toBe(
            "Processing is queued — its status appears in the list.",
        );
    });
});

describe("describeMaterialProcessError (reprocess flow)", () => {
    it("surfaces both documented 409 classes through the backend's own readable detail", () => {
        // Class 1 — already queued or processing.
        expect(
            describeMaterialProcessError(
                new ApiError(
                    409,
                    "Material is already queued or processing (current status: processing)",
                ),
            ),
        ).toBe(
            "Material is already queued or processing (current status: processing)",
        );

        // Class 2 — the manual retry budget is exhausted.
        expect(
            describeMaterialProcessError(
                new ApiError(
                    409,
                    "Manual retry budget exhausted (3 of 3 manual retries consumed)",
                ),
            ),
        ).toBe(
            "Manual retry budget exhausted (3 of 3 manual retries consumed)",
        );
    });

    it("maps the write-rate-limit 429 and the permission/not-found/session classes", () => {
        expect(describeMaterialProcessError(new ApiError(429, "slow down"))).toBe(
            "Too many requests — wait a moment and try again.",
        );
        expect(
            describeMaterialProcessError(new ApiError(403, "denied")),
        ).toBe(
            "You do not have permission to manage materials in this course.",
        );
        expect(describeMaterialProcessError(new ApiError(404, "gone"))).toBe(
            "The material was not found. Refresh the list to see its current state.",
        );
        expect(
            describeMaterialProcessError(new ApiError(401, "expired")),
        ).toBe("Your session has expired. Redirecting to sign in...");
    });

    it("falls back honestly without inventing retry state", () => {
        // No retry_count exists on any response — the fallback never
        // pretends to know the budget.
        expect(describeMaterialProcessError(new ApiError(409, ""))).toContain(
            "could not be started",
        );
        expect(describeMaterialProcessError(new Error("offline"))).toBe(
            "offline",
        );
        expect(describeMaterialProcessError("mystery")).toBe(
            "Processing could not be started.",
        );
    });
});

describe("describeMaterialPagesError (viewer read)", () => {
    it("maps the documented ownership and not-found responses without internal details", () => {
        expect(describeMaterialPagesError(new ApiError(403, "denied"))).toBe(
            "You do not have permission to read this material.",
        );
        expect(describeMaterialPagesError(new ApiError(404, "missing"))).toBe(
            "The material was not found. Refresh the list to see its current state.",
        );
        expect(describeMaterialPagesError(new ApiError(401, "expired"))).toBe(
            "Your session has expired. Redirecting to sign in...",
        );
        expect(
            describeMaterialPagesError(new ApiError(500, "boom")),
        ).toBe("boom");
        expect(describeMaterialPagesError(new Error("offline"))).toBe(
            "offline",
        );
        expect(describeMaterialPagesError("mystery")).toBe(
            "The extracted text could not be loaded.",
        );
    });
});
