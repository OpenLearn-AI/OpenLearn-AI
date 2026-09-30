import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Select primitive styled to match the Input token dialect (D8).
 *
 * A thin wrapper around the native `<select>` element — no external
 * select library is needed at the current form scale.
 */
function Select({
    className,
    ...props
}: React.ComponentProps<"select">) {
    return (
        <select
            data-slot="select"
            className={cn(
                "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-base shadow-xs outline-none transition-colors focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 md:text-sm dark:bg-input/30",
                className,
            )}
            {...props}
        />
    );
}

export { Select };
