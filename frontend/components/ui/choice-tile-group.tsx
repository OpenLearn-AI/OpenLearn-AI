"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * ChoiceTileGroup (Batch 4.1 corrective follow-up — onboarding UX).
 *
 * An accessible "tile" picker for finite, contract-backed choices. It
 * ships two modes:
 *
 * SINGLE SELECT (default; used by the wizard's daily-minutes presets
 * and formerly by learning-style before the multi select existed):
 *   - WAI-ARIA radio-group: `role="radiogroup"` labelled by the
 *     visible label; `role="radio"` tiles carry `aria-checked`.
 *   - Roving `tabIndex` (only the selected — or, when nothing is
 *     selected yet, the first — tile is tabbable).
 *   - Arrow keys move focus AND selection (selection follows focus);
 *     Home/End jump; the direction respects the document's `dir`, so
 *     Right/Left keep their visual meaning under RTL.
 *   - Space/Enter activate the focused tile (native button semantics).
 *
 * MULTI SELECT (Batch 4.2 redesign; used by the wizard's VARK
 * learning-style step, which is free text in the API contract):
 *   - WAI-ARIA toggle-button pattern: `role="group"` labelled by the
 *     visible label; tiles carry `aria-pressed` (boolean).
 *   - Natural tab order (each tile is its own tab stop — toggles do
 *     not take roving tabindex); Space/Enter press the focused tile.
 *   - No arrow-key selection steering (that is the radio pattern's
 *     contract; multi-select keeps the platform's native toggle
 *     behavior instead).
 *
 * There is deliberately NO tree/grid mode, and single-value fields
 * stay single-select: a mutually exclusive control is the honest
 * mapping for finite enum/preset contracts (owner follow-up §A.2),
 * while free-text-backed fields (VARK) get the toggle mapping.
 *
 * Each tile is a real `<button type="button">` — reachable, focusable,
 * and announced with its pressed state — and the group renders the
 * error/hint line through the same visual language as `Field`.
 */

export interface ChoiceTileOption {
    value: string;
    label: string;
}

type BaseProps = {
    /** Used for the group's label/describedby wiring (not a control id). */
    id: string;
    label: string;
    options: readonly ChoiceTileOption[];
    error?: string;
    hint?: string;
    disabled?: boolean;
    className?: string;
    /** Extra classes for the tile row itself (e.g. equal-width tiles). */
    groupClassName?: string;
    /** Small inline action (e.g. "Clear") rendered at the label row's
     * inline end — kept OUTSIDE the group so it never joins the
     * keyboard behavior of the tiles. */
    action?: React.ReactNode;
};

export type ChoiceTileGroupProps =
    | (BaseProps & {
          /** Single select (default): exactly one value at a time. */
          multiple?: false;
          /** The currently selected value ("" = nothing selected yet). */
          value: string;
          onValueChange: (value: string) => void;
      })
    | (BaseProps & {
          /** Multi select: the toggle-button pattern above. */
          multiple: true;
          /** The currently selected values (in no guaranteed order). */
          value: string[];
          onValueChange: (value: string[]) => void;
      });

export function ChoiceTileGroup(props: ChoiceTileGroupProps) {
    const {
        id,
        label,
        options,
        error,
        hint,
        disabled,
        className,
        groupClassName,
        action,
        multiple,
    } = props;
    const refs = React.useRef<(HTMLButtonElement | null)[]>([]);

    const describedBy = error ? `${id}-error` : undefined;

    const focusTile = (index: number) => {
        const tile = refs.current[index];
        if (tile) {
            tile.focus();
        }
    };

    // ── Single-select keyboard behavior (roving tabindex radio) ────────
    const singleValue = multiple ? "" : props.value;
    const onSingleChange = multiple
        ? undefined
        : (value: string) => props.onValueChange(value);

    const selectedIndex = options.findIndex(
        (option) => option.value === singleValue,
    );
    // Roving tabindex: the selected tile is the tab stop; when nothing
    // is selected yet, the first tile is (WAI-ARIA radio pattern).
    const currentIndex = selectedIndex >= 0 ? selectedIndex : 0;

    const moveSelection = (index: number) => {
        const next = options[index];
        if (!next || multiple) {
            return;
        }
        onSingleChange?.(next.value);
        focusTile(index);
    };

    const handleSingleKeyDown = (event: React.KeyboardEvent) => {
        if (multiple) {
            return;
        }
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

    // ── Multi-select toggle behavior ──────────────────────────────────
    const multiValue = multiple ? props.value : [];
    const onMultiChange = multiple ? props.onValueChange : undefined;

    const toggle = (val: string) => {
        if (!onMultiChange) {
            return;
        }
        onMultiChange(
            multiValue.includes(val)
                ? multiValue.filter((v) => v !== val)
                : [...multiValue, val],
        );
    };

    const isSelected = (val: string) =>
        multiple ? multiValue.includes(val) : val === singleValue;

    const checkedClassNames =
        // Solid primary fill. The tint on tint alternative measured
        // 4.41:1 and failed WCAG AA at this size, so both single and
        // multi selected tiles use the same solid treatment. The Ink
        // and Brass palette keeps the same silhouette in light and
        // in the fixed dark public surfaces (brass fill, warm ink
        // text; both verified in the palette notes).
        "border-primary bg-primary text-primary-foreground hover:bg-primary/90";
    const uncheckedClassNames =
        "border-border bg-card text-card-foreground hover:border-primary/40 hover:bg-muted/60";

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
                role={multiple ? "group" : "radiogroup"}
                aria-labelledby={`${id}-label`}
                aria-describedby={describedBy}
                aria-invalid={error ? true : undefined}
                onKeyDown={handleSingleKeyDown}
                className={cn("flex flex-wrap gap-2", groupClassName)}
            >
                {options.map((option, index) => {
                    const selected = isSelected(option.value);

                    return (
                        <button
                            key={option.value}
                            ref={(node) => {
                                refs.current[index] = node;
                            }}
                            type="button"
                            {...(multiple
                                ? { "aria-pressed": selected }
                                : {
                                      role: "radio",
                                      "aria-checked": selected,
                                      tabIndex: index === currentIndex ? 0 : -1,
                                  })}
                            disabled={disabled}
                            onClick={() =>
                                multiple
                                    ? toggle(option.value)
                                    : onSingleChange?.(option.value)
                            }
                            className={cn(
                                "inline-flex min-h-11 items-center justify-center rounded-xl border px-3.5 text-sm font-medium transition-colors outline-none select-none",
                                "focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                                "disabled:pointer-events-none disabled:opacity-50",
                                selected
                                    ? checkedClassNames
                                    : uncheckedClassNames,
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
