import { LoadingBlock } from "@/components/state/LoadingBlock";

/**
 * Route-level loading boundary for the `(app)` route group (Batch
 * 4.4 — the roadmap's Table 26 files-affected list includes this
 * boundary; it completes the pair with the existing `(auth)`
 * boundary so BOTH route groups have an honest instant loading
 * state instead of Next.js's blank default).
 *
 * Mirrors the `(auth)` boundary using the shared async-state kit
 * (the only sanctioned loading presentation). Unlike `(auth)`, the
 * `(app)` layout does not center its children — the shell's content
 * column hosts this state — so the boundary owns its centering:
 * one quiet block in the content area, never a fake skeleton or
 * invented progress. The shell (sidebar, navigation) stays
 * interactive around it: shared layouts remain mounted while the
 * next segment's payload streams in, which is exactly the App
 * Router's instant-loading contract. Route behavior, guards, and
 * the gate are untouched — this file only renders BETWEEN
 * navigations.
 */
export default function AppLoading() {
    return (
        <main className="flex min-h-screen items-center justify-center bg-background px-4 py-8">
            <LoadingBlock message="Loading..." />
        </main>
    );
}
