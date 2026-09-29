import Link from "next/link";

import { Button } from "@/components/ui/button";

/**
 * Root 404 page (D11). Rendered when:
 *   - a visitor hits a URL that does not match any route, or
 *   - any page throws `notFound()` (e.g. an invalid course ID once
 *     Phase 4 wires that into the course detail page).
 *
 * Keeps the design intentionally simple — no new design system, just
 * existing tokens and a single clear action back to the application.
 */
export default function NotFound() {
    return (
        <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-4 py-8 text-center">
            <div className="space-y-2">
                <h1 className="text-4xl font-bold tracking-tight text-foreground">
                    404
                </h1>
                <p className="text-sm text-muted-foreground">
                    The page you are looking for does not exist or may have
                    been moved.
                </p>
            </div>
            <Button size="lg" render={<Link href="/" />}>
                Back to home
            </Button>
        </main>
    );
}
