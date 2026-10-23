/**
 * next/navigation stub for Storybook (Batch 4.1 corrective follow-up).
 *
 * The auth-entry components (OidcEntryButton, OidcEntryBridge) use the
 * App Router's `useRouter`/`useSearchParams`, and the REAL
 * implementation throws "invariant expected app router to be mounted"
 * outside a Next.js runtime — which made every story that renders them
 * crash. This module is aliased over `next/navigation` in
 * `.storybook/main.ts` (viteFinal) for the Storybook bundle ONLY:
 * application builds and runtime behavior are untouched.
 *
 * Navigation is a no-op in stories (they assert rendering and
 * interaction, not navigation side effects), and `useSearchParams`
 * returns ONE module-stable instance — React compares snapshot
 * identity, so a fresh object per call would loop effects forever.
 */

const routerStub = {
    push: () => {},
    replace: () => {},
    refresh: () => {},
    back: () => {},
    forward: () => {},
    prefetch: () => {},
};

const searchParamsStub = new URLSearchParams();

export function useRouter() {
    return routerStub;
}

export function usePathname() {
    return "/";
}

export function useSearchParams() {
    return searchParamsStub;
}

export function useParams() {
    return {};
}

export function useSelectedLayoutSegment() {
    return null;
}

export function useSelectedLayoutSegments() {
    return [];
}

export function redirect() {
    /* no-op in stories */
}

export function notFound() {
    /* no-op in stories */
}

export const unstable_noStore = () => {};

// A default export keeps imports of the namespace shape working too.
const navigationStub = { useRouter, usePathname, useSearchParams, useParams };
export default navigationStub;
