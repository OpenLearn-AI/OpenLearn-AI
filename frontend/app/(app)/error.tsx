"use client";

import { useEffect } from "react";
import { CircleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";

/**
 * Route-level error boundary for the `(app)` route group (D11;
 * Batch 4.4 editorial pass).
 *
 * The Next.js App Router client error boundary contract is
 * unchanged: `error` + `reset` props, internal details and stack
 * traces never exposed, and the reset/retry path is the single
 * primary action. The `(app)` layout (sidebar shell) keeps
 * rendering around this boundary, so no escape-hatch links are
 * invented — the shell's navigation is the escape; "Try again" is
 * the appropriate next action.
 *
 * Presentation: the redesign's state language — a compact semantic
 * indicator (the ErrorState kit's marker, never color alone), a
 * quiet heading, honest copy, one filled action. Direction-safe
 * (centered composition, logical spacing) and theme-safe (tokens
 * only). The console log stays: developer visibility until the
 * Phase 6 observability integration.
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
        <main className="@container flex min-h-screen flex-col items-center justify-center bg-background px-4 py-8 text-center">
            <CircleAlert
                aria-hidden="true"
                className="size-5 text-destructive"
            />
            <h1 className="mt-4 text-[clamp(1.25rem,3cqi,1.5rem)] font-semibold tracking-tight text-foreground">
                Something went wrong
            </h1>
            <p className="mt-3 max-w-[46ch] text-sm leading-relaxed text-muted-foreground">
                An unexpected error occurred while loading this page.
                Please try again.
            </p>
            <div className="mt-8">
                <Button size="lg" onClick={reset}>
                    Try again
                </Button>
            </div>
        </main>
    );
}
