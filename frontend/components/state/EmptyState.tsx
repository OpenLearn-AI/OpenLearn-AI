import Link from "next/link";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

/**
 * Reusable empty-state presentation (D11). Renders a friendly message
 * when a data collection is empty, with an optional call-to-action.
 * No business logic — purely presentational.
 */
export function EmptyState({
    message = "Nothing here yet.",
    actionHref,
    actionLabel,
    className,
}: {
    message?: string;
    actionHref?: string;
    actionLabel?: string;
    className?: string;
}) {
    return (
        <div
            className={cn(
                "flex flex-col items-center justify-center gap-4 rounded-2xl border border-border bg-card p-8 text-center shadow-xs",
                className,
            )}
        >
            <p className="text-sm text-muted-foreground">{message}</p>
            {actionHref && actionLabel && (
                <Button size="sm" render={<Link href={actionHref} />}>
                    {actionLabel}
                </Button>
            )}
        </div>
    );
}
