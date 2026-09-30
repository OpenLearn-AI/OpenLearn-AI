import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Textarea primitive styled to match the Input token dialect.
 * Generated-equivalent for shadcn `textarea` (D8).
 */
function Textarea({
    className,
    ...props
}: React.ComponentProps<"textarea">) {
    return (
        <textarea
            data-slot="textarea"
            className={cn(
                "flex min-h-20 w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-xs outline-none transition-colors placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 md:text-sm dark:bg-input/30",
                className,
            )}
            {...props}
        />
    );
}

export { Textarea };
