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
    formatByteSize,
    isTerminalMaterialStatus,
    MATERIAL_FAILED_COPY,
    MATERIAL_STATUS_LABELS,
} from "./flow";
import { materialKeys } from "./keys";

/**
 * Unit tests for the Batch 4.3 material flow helpers (pure module —
 * the same isolation pattern as user-identity/gate-state).
 *
 * What is pinned: the presigned-POST form-data construction (signed
 * fields FIRST, the file LAST under the contract's `file` name — the
 * order the UploadUrlResponse documents), the terminal-status
 * predicate that drives polling shutdown, the honest error mapping,
 * and the status label vocabulary (the contract's four literals —
 * never a phase name or percentage).
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
});
