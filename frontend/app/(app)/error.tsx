"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";

/**
 * Route-level error boundary for the `(app)` route group (D11).
 *
 * Follows the Next.js App Router client error boundary contract:
 * receives `error` and `reset` props. Never exposes internal stack
 * traces or sensitive details to the user.
 */
export default function AppError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log to the console for developer visibility; a real
        // observability integration (Sentry) arrives in Phase 6.
        console.error("Application route error:", error);
    }, [error]);

    return (
        <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-background px-4 py-8 text-center">
            <div className="space-y-2">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                    Something went wrong
                </h1>
                <p className="text-sm text-muted-foreground">
                    An unexpected error occurred while loading this page.
                    Please try again.
                </p>
            </div>
            <Button size="lg" onClick={reset}>
                Try again
            </Button>
        </main>
    );
}
