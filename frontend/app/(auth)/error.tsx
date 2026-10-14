"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";

/**
 * Route-level error boundary for the `(auth)` route group (S8).
 *
 * Mirrors the `(app)` boundary's contract and copy (Next.js App Router
 * error boundary: `error` + `reset` props, internal details never
 * exposed) inside the auth shell's centered card language — before
 * Batch 1.2 auth-route render errors hit the unstyled default. Batch
 * 4.1 restyles the auth screens on the token system; this boundary
 * exists so both route groups are styled from now on.
 */
export default function AuthError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log to the console for developer visibility; the real
        // observability integration (Sentry) is Batch 1.3's chain.
        console.error("Auth route error:", error);
    }, [error]);

    return (
        <div className="w-full max-w-md bg-card text-card-foreground p-8 rounded-2xl shadow-xl border border-border text-center space-y-4">
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
        </div>
    );
}
