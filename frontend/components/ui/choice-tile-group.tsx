"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * ChoiceTileGroup (Batch 4.1 corrective follow-up — onboarding UX).
 *
 * An accessible single-select "tile" picker for finite, contract-backed
 * choices (the profile API's `preferred_language` enum, minute presets
 * for the integer `daily_available_minutes`, and the four VARK styles
 * the product's own hint documents for `learning_style_vark`). It
 * implements the WAI-ARIA radio-group pattern:
 *
 *   - `role="radiogroup"` labelled by the visible label; `role="radio"`
 *     tiles carry `aria-checked`.
 *   - Roving `tabIndex` (only the selected — or, when nothing is
 *     selected yet, the first — tile is tabbable).
 *   - Arrow keys move focus AND selection (selection follows focus);
 *     Home/End jump; the direction respects the document's `dir`, so
 *     Right/Left keep their visual meaning under RTL.
 *   - Space/Enter activate the focused tile (native button semantics).
 *
 * There is deliberately NO multi-select mode: every profile field is
 * single-valued in the API contract, so a mutually exclusive control is
 * the honest mapping (owner follow-up §A.2).
 *
 * Each tile is a real `<button type="button">` — reachable, focusable,
 * and announced with its checked state — and the group renders the
 * error/hint line through the same visual language as `Field`.
 */

export interface ChoiceTileOption {
    value: string;
    label: string;
}

export function ChoiceTileGroup({
    id,
    label,
    options,
    value,
    onValueChange,
    error,
    hint,
    disabled,
    className,
    groupClassName,
    action,
}: {
    /** Used for the group's label/describedby wiring (not a control id). */
    id: string;
    label: string;
    options: readonly ChoiceTileOption[];
    /** The currently selected value ("" = nothing selected yet). */
    value: string;
    onValueChange: (value: string) => void;
    error?: string;
    hint?: string;
    disabled?: boolean;
    className?: string;
    /** Extra classes for the tile row itself (e.g. equal-width tiles). */
    groupClassName?: string;
    /** Small inline action (e.g. "Clear") rendered at the label row's
     * inline end — kept OUTSIDE the radiogroup so it never joins the
     * roving-tabindex/arrow-key behavior. */
    action?: React.ReactNode;
}) {
    const refs = React.useRef<(HTMLButtonElement | null)[]>([]);

    const describedBy = error ? `${id}-error` : undefined;

    const focusTile = (index: number) => {
        const tile = refs.current[index];
        if (tile) {
            tile.focus();
        }
    };

    const moveSelection = (index: number) => {
        const next = options[index];
        if (!next) {
            return;
        }
        onValueChange(next.value);
        focusTile(index);
    };

    const selectedIndex = options.findIndex(
        (option) => option.value === value,
    );
    // Roving tabindex: the selected tile is the tab stop; when nothing
    // is selected yet, the first tile is (WAI-ARIA radio pattern).
    const currentIndex = selectedIndex >= 0 ? selectedIndex : 0;

    const handleKeyDown = (event: React.KeyboardEvent) => {
        // Radio-group arrows: selection follows focus. Right/Down move
        // forward in LTR and backward in RTL (visually consistent with
        // the rendered tile order, which flips with the document dir).
        const isRtl =
            typeof document !== "undefined" &&
            document.documentElement.dir === "rtl";

        const forwardKey = isRtl ? "ArrowLeft" : "ArrowRight";
        const backKey = isRtl ? "ArrowRight" : "ArrowLeft";

        if (event.key === forwardKey || event.key === "ArrowDown") {
            event.preventDefault();
            moveSelection((currentIndex + 1) % options.length);
        } else if (event.key === backKey || event.key === "ArrowUp") {
            event.preventDefault();
            moveSelection(
                (currentIndex - 1 + options.length) % options.length,
            );
        } else if (event.key === "Home") {
            event.preventDefault();
            moveSelection(0);
        } else if (event.key === "End") {
            event.preventDefault();
            moveSelection(options.length - 1);
        }
    };

    return (
        <div className={cn("space-y-2", className)}>
            <div className="flex items-center justify-between gap-3">
                <span
                    id={`${id}-label`}
                    className="block text-sm font-medium leading-none"
                >
                    {label}
                </span>
                {action}
            </div>

            <div
                role="radiogroup"
                aria-labelledby={`${id}-label`}
                aria-describedby={describedBy}
                aria-invalid={error ? true : undefined}
                onKeyDown={handleKeyDown}
                className={cn("flex flex-wrap gap-2", groupClassName)}
            >
                {options.map((option, index) => {
                    const checked = option.value === value;

                    return (
                        <button
                            key={option.value}
                            ref={(node) => {
                                refs.current[index] = node;
                            }}
                            type="button"
                            role="radio"
                            aria-checked={checked}
                            tabIndex={index === currentIndex ? 0 : -1}
                            disabled={disabled}
                            onClick={() => onValueChange(option.value)}
                            className={cn(
                                "inline-flex min-h-11 items-center justify-center rounded-xl border px-3.5 text-sm font-medium transition-colors outline-none select-none",
                                "focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                                "disabled:pointer-events-none disabled:opacity-50",
                                checked
                                    ? // Solid primary fill: white-on-steel-blue
                                      // (light) and near-black-on-light-steel
                                      // (dark) both clear WCAG AA at 14px —
                                      // the tint-on-tint alternative measured
                                      // 4.41:1 and failed.
                                      "border-primary bg-primary text-primary-foreground hover:bg-primary/90"
                                    : "border-border bg-card text-card-foreground hover:border-primary/40 hover:bg-muted/60",
                            )}
                        >
                            {option.label}
                        </button>
                    );
                })}
            </div>

            {error ? (
                <p
                    id={`${id}-error`}
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
