"use client";

import { useEffect } from "react";
import { CircleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";

/**
 * Route-level error boundary for the `(auth)` route group (S8;
 * Batch 4.4 editorial pass).
 *
 * Mirrors the `(app)` boundary's contract and copy (Next.js App
 * Router error boundary: `error` + `reset` props, internal details
 * never exposed) inside the auth shell's centered card language —
 * the same card treatment as the sign-in/register entries (Batch
 * 4.2: `max-w-md rounded-2xl border bg-card p-8 shadow-xs`), with
 * the same compact semantic indicator the ErrorState kit uses. The
 * `shadow-xl` inconsistency is retired with it. The auth layout
 * centers its children, so — as before — no full-screen wrapper is
 * added here.
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
        <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-card-foreground shadow-xs">
            <div className="flex flex-col items-center gap-3 text-center">
                <CircleAlert
                    aria-hidden="true"
                    className="size-4 text-destructive"
                />
                <div className="space-y-2">
                    <h1 className="text-2xl font-bold tracking-tight text-foreground">
                        Something went wrong
                    </h1>
                    <p className="text-sm text-muted-foreground">
                        An unexpected error occurred while loading
                        this page. Please try again.
                    </p>
                </div>
                <Button size="lg" onClick={reset}>
                    Try again
                </Button>
            </div>
        </div>
    );
}
