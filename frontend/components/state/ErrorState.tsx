import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

/**
 * Reusable error presentation (D11), compatible with the Phase 2
 * `ApiError` abstraction (D8). Renders a safe, user-friendly error
 * message with an optional retry action. No business logic — purely
 * presentational. Stack traces / internal details are never shown.
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
                "flex flex-col items-center justify-center gap-4 rounded-2xl border border-border bg-card p-8 text-center shadow-xs",
                className,
            )}
        >
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
