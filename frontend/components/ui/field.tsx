import * as React from "react";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

/**
 * Field wrapper (D8).
 *
 * Bundles a label, a control (input/select/textarea), and an error
 * message into a single accessible group. Reduces the per-field
 * boilerplate in manual controlled forms (no form library needed).
 *
 * The control is passed as `children` so any input primitive can be
 * composed; the caller wires `id`, `aria-invalid`, and `disabled`
 * on the control itself.
 */
export function Field({
    label,
    htmlFor,
    error,
    hint,
    className,
    children,
}: {
    label: string;
    htmlFor: string;
    error?: string;
    hint?: string;
    className?: string;
    children: React.ReactNode;
}) {
    return (
        <div className={cn("space-y-2", className)}>
            <Label htmlFor={htmlFor}>{label}</Label>
            {children}
            {error ? (
                <p
                    id={`${htmlFor}-error`}
                    role="alert"
                    className="text-sm text-destructive"
                >
                    {error}
                </p>
            ) : hint ? (
                <p className="text-xs text-muted-foreground">{hint}</p>
            ) : null}
        </div>
    );
}
