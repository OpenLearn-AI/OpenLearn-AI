import Link from "next/link";

import { Button } from "@/components/ui/button";

/**
 * Root 404 page (D11; Batch 4.4 editorial pass). Rendered when:
 *   - a visitor hits a URL that does not match any route, or
 *   - any page throws `notFound()` (e.g. the course detail page on
 *     an actual API 404 — the 404-to-notFound semantics are
 *     unchanged by this presentation pass).
 *
 * The presentation joins the redesign's state language: the code as
 * a large tabular numeral (the display element, decorative — the
 * heading carries the meaning for assistive tech, the same
 * numeral-as-datum grammar as the dashboard's facts band), a quiet
 * heading, honest copy, and exactly one filled action back to the
 * application. No invented diagnostics, no fake search, no actions
 * that do not exist. Direction-safe by construction: centered
 * composition, logical spacing, `@container`-driven type scale.
 */
export default function NotFound() {
    return (
        <main className="@container flex min-h-svh flex-col items-center justify-center bg-background px-4 py-8 text-center">
            <p
                aria-hidden="true"
                className="text-[clamp(3.5rem,12cqi,5rem)] font-semibold leading-none tracking-tight text-foreground tabular-nums"
            >
                404
            </p>
            <h1 className="mt-5 text-[clamp(1.25rem,3cqi,1.5rem)] font-semibold tracking-tight text-foreground">
                Page not found
            </h1>
            <p className="mt-3 max-w-[46ch] text-sm leading-relaxed text-muted-foreground">
                The page you are looking for does not exist or may
                have been moved.
            </p>
            <div className="mt-8">
                <Button size="lg" render={<Link href="/" />}>
                    Back to home
                </Button>
            </div>
        </main>
    );
}
