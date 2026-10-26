"use client";

import * as React from "react";

/**
 * Layout-direction support (Batch 4.4 — RTL/LTR direction control).
 *
 * A deliberate, minimal mechanism — NOT an i18n framework and NOT a
 * language selection. The product UI stays English; this module only
 * controls the document's layout direction (`dir` attribute) so the
 * RTL-readiness of the design can be exercised for real by users and
 * reviewers (roadmap §8 Q3: Phases 3–4 deliver RTL-READY design; full
 * bilingual depth stays with the plan's W37/W41 pass).
 *
 * Architecture (mirrors the proven next-themes pattern already in the
 * repository — no new dependency, no new state framework):
 *
 * - The `<html dir>` attribute IS the single source of truth for the
 *   current direction. Everything (the toggle's `aria-pressed`, the
 *   layout's logical CSS utilities) reads the live DOM.
 * - A tiny inline script in the root layout (`components/theme-provider`
 *   precedent — see `app/layout.tsx`) applies a stored preference
 *   BEFORE first paint, so a returning RTL user never sees an LTR
 *   flash. `suppressHydrationWarning` (already present on `<html>`
 *   for next-themes' `class` mutation) covers the attribute delta on
 *   hydration.
 * - `applyDirection`/`toggleDirection` write the attribute AND
 *   `localStorage` AND dispatch a custom event, so every mounted
 *   `useDirection` subscriber re-renders in sync. The `storage` event
 *   keeps multiple open tabs consistent.
 * - `useDirection` reads through `useSyncExternalStore` with a static
 *   server snapshot (`"ltr"` — the SSR default), which is the
 *   React-sanctioned way to adopt a client-only value without
 *   hydration mismatches: after hydration React simply re-renders
 *   with the client snapshot.
 */

export type Direction = "ltr" | "rtl";

/** localStorage key. Plain, namespaced to the product (next-themes'
 * own key is the bare `"theme"` — same convention, one level). */
export const DIRECTION_STORAGE_KEY = "openlearn-direction";

/** The custom event dispatched on every applied change. */
const DIRECTION_EVENT = "openlearn:directionchange";

export function isDirection(value: unknown): value is Direction {
    return value === "ltr" || value === "rtl";
}

/**
 * Read a stored direction without touching the DOM. Returns `null`
 * when absent or unreadable (private mode, quota, SSR) — callers
 * decide their own default; the app default is `"ltr"`.
 */
export function readStoredDirection(): Direction | null {
    if (typeof window === "undefined") return null;
    try {
        const stored = window.localStorage.getItem(DIRECTION_STORAGE_KEY);
        return isDirection(stored) ? stored : null;
    } catch {
        // localStorage can throw (privacy settings / disabled storage).
        return null;
    }
}

/** The live direction straight from the document element. */
export function currentDirection(): Direction {
    if (typeof document === "undefined") return "ltr";
    return document.documentElement.dir === "rtl" ? "rtl" : "ltr";
}

/**
 * Apply a direction: DOM attribute first (the layout flips instantly),
 * then persistence (best-effort — a storage failure must never block
 * the direction change), then notify subscribers.
 */
export function applyDirection(direction: Direction): void {
    if (typeof document === "undefined") return;
    document.documentElement.dir = direction;
    try {
        window.localStorage.setItem(DIRECTION_STORAGE_KEY, direction);
    } catch {
        // Persistence is best-effort; the session still works.
    }
    window.dispatchEvent(new CustomEvent(DIRECTION_EVENT));
}

/** Flip the current direction and return the new value. */
export function toggleDirection(): Direction {
    const next: Direction = currentDirection() === "rtl" ? "ltr" : "rtl";
    applyDirection(next);
    return next;
}

/**
 * Subscribe to direction changes. Listens to the in-page event AND
 * the cross-tab `storage` event, so every instance (and every tab)
 * stays in sync. Returns the unsubscribe function expected by
 * `useSyncExternalStore`.
 */
export function subscribeToDirection(callback: () => void): () => void {
    window.addEventListener(DIRECTION_EVENT, callback);
    window.addEventListener("storage", callback);
    return () => {
        window.removeEventListener(DIRECTION_EVENT, callback);
        window.removeEventListener("storage", callback);
    };
}

/**
 * React hook over the live direction. Server snapshot is the static
 * `"ltr"` default; the client snapshot reads the DOM attribute, so
 * the pre-paint script's value is adopted right after hydration
 * without any mismatch (React re-renders on snapshot change).
 */
export function useDirection(): Direction {
    return React.useSyncExternalStore(
        subscribeToDirection,
        currentDirection,
        () => "ltr" as const,
    );
}
