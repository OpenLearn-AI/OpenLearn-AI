/**
 * Shared API boundary (D3). One typed fetch helper for every feature
 * domain — the only place that knows about the API base URL, the
 * Keycloak bearer token, JSON serialization, and HTTP-error mapping.
 * Response types are `z.infer` derivations (D4); pass a schema to
 * `apiFetch` to validate responses before they reach callers.
 */

import { config } from "@/lib/config";
import { getAccessToken } from "@/lib/keycloak";
import type { ZodType } from "zod";

/**
 * Application-level error for failed HTTP responses (D8 error half).
 * `status` is the HTTP status code (0 for network/validation
 * failures). `body` is the parsed JSON response when one was sent
 * (e.g. FastAPI's `{"detail": "..."}` shape), otherwise `null`.
 */
export class ApiError extends Error {
    readonly status: number;
    readonly body: unknown;

    constructor(status: number, message: string, body: unknown = null) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.body = body;
    }
}

export interface ApiFetchOptions<T> {
    method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
    body?: unknown;
    schema?: ZodType<T>;
}

/**
 * Perform an authenticated JSON request against the OpenLearn API.
 * `path` is appended to `config.apiUrl` (e.g. `"/v1/courses"`).
 * Non-2xx responses throw `ApiError`. When `schema` is provided the
 * parsed response is validated; a validation failure throws `ApiError`
 * with status 0. 204 responses resolve to `undefined` (DELETE).
 */
export async function apiFetch<T>(
    path: string,
    options: ApiFetchOptions<T> = {},
): Promise<T> {
    const { method = "GET", body, schema } = options;

    const token = await getAccessToken();

    if (!token) {
        throw new ApiError(401, "Not authenticated");
    }

    const headers: Record<string, string> = {
        Authorization: `Bearer ${token}`,
    };

    if (body !== undefined) {
        headers["Content-Type"] = "application/json";
    }

    let response: Response;

    try {
        response = await fetch(`${config.apiUrl}${path}`, {
            method,
            headers,
            body: body !== undefined ? JSON.stringify(body) : undefined,
        });
    } catch (cause) {
        if (cause instanceof ApiError) {
            throw cause;
        }
        throw new ApiError(
            0,
            cause instanceof Error
                ? `Network request failed: ${cause.message}`
                : "Network request failed",
        );
    }

    if (!response.ok) {
        let parsedBody: unknown = null;
        try {
            parsedBody = await response.json();
        } catch {
            // No JSON body; leave as null.
        }
        const detail = extractDetail(parsedBody);
        throw new ApiError(
            response.status,
            detail ?? `Request failed with status ${response.status}`,
            parsedBody,
        );
    }

    if (response.status === 204) {
        return undefined as T;
    }

    let payload: unknown;
    try {
        payload = await response.json();
    } catch (cause) {
        throw new ApiError(
            0,
            cause instanceof Error
                ? `Response was not valid JSON: ${cause.message}`
                : "Response was not valid JSON",
        );
    }

    if (schema) {
        const result = schema.safeParse(payload);
        if (!result.success) {
            throw new ApiError(
                0,
                `Response schema validation failed: ${result.error.message}`,
                payload,
            );
        }
        return result.data;
    }

    return payload as T;
}

/** Pull a human-readable message out of a parsed error body.
 * Handles FastAPI shapes: `{"detail": "..."}` (HTTPException),
 * `{"detail": [{"msg": "...", ...}]}` (422 validation), and plain strings. */
function extractDetail(body: unknown): string | null {
    if (typeof body === "string" && body.length > 0) return body;
    if (body !== null && typeof body === "object" && "detail" in body) {
        const detail = (body as { detail: unknown }).detail;
        if (typeof detail === "string" && detail.length > 0) return detail;
        // FastAPI 422: detail is an array of { msg, loc, ... } objects.
        if (Array.isArray(detail) && detail.length > 0) {
            const first = detail[0] as { msg?: unknown } | null;
            if (first && typeof first.msg === "string") return first.msg;
        }
    }
    return null;
}
