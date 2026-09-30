import { cn } from "@/lib/utils";

/**
 * Reusable loading presentation (D11).
 *
 * Renders an accessible, animated loading indicator with an optional
 * message. No business logic — purely presentational.
 */
export function LoadingBlock({
    message = "Loading...",
    className,
}: {
    message?: string;
    className?: string;
}) {
    return (
        <div
            role="status"
            aria-live="polite"
            className={cn(
                "flex items-center justify-center gap-3 rounded-2xl border border-border bg-card p-8 text-sm text-muted-foreground shadow-xs",
                className,
            )}
        >
            <span
                className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent"
                aria-hidden="true"
            />
            <span>{message}</span>
        </div>
    );
}
