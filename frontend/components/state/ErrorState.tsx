import { CircleAlert } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

/**
 * Reusable error presentation (D11), compatible with the Phase 2
 * `ApiError` abstraction (D8). Renders a safe, user-friendly error
 * message with an optional retry action. No business logic — purely
 * presentational. Stack traces / internal details are never shown.
 *
 * Restyled in Batch 3.2 to the minimalist semantic-feedback policy
 * (ADR-0010 §2.7): a neutral card surface with a compact semantic
 * indicator and the error as text — no tinted panel, and the state
 * never rides color alone (the message text carries it).
 */
export function ErrorState({
    message = "Something went wrong.",
    onRetry,
    retryLabel = "Try again",
    className,
}: {
    message?: string;
    onRetry?: () => void;
    retryLabel?: string;
    className?: string;
}) {
    return (
        <div
            role="alert"
            className={cn(
                "flex flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-card p-8 text-center shadow-xs",
                className,
            )}
        >
            <CircleAlert
                aria-hidden="true"
                className="size-4 text-destructive"
            />
            <p className="text-sm text-destructive">{message}</p>
            {onRetry && (
                <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={onRetry}
                >
                    {retryLabel}
                </Button>
            )}
        </div>
    );
}
