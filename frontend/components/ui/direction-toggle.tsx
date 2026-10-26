"use client";

import { ArrowLeftRight } from "lucide-react";

import { cn } from "@/lib/utils";
import { useDirection, toggleDirection } from "@/lib/direction";

/**
 * Layout-direction control (Batch 4.4 — the user-requested RTL/LTR
 * toggle, placed with the theme control in the shell's account
 * region: desktop sidebar + mobile drawer).
 *
 * Visual grammar: the exact `ThemeToggle` treatment (36px bordered
 * square, same radius/border/focus ring), so the two controls read
 * as one family of appearance-and-layout switches — related, but
 * clearly distinct in name and icon (theme = sun/moon; direction =
 * a bidirectional arrow, deliberately NOT a "languages" glyph since
 * this is layout direction, not language selection).
 *
 * Accessibility — the state is NEVER the icon alone:
 * - `aria-pressed` carries the current state (the WAI-ARIA toggle
 *   button pattern): screen readers announce "Right-to-left layout,
 *   toggle button, pressed/not pressed".
 * - The accessible name is stable ("Right-to-left layout") so the
 *   announcement is deterministic in both states.
 * - The icon is decorative (`aria-hidden`) and horizontally
 *   symmetric, so it is never mirrored or misleading in RTL.
 * The surrounding sidebar adds a reinforcing tooltip in the
 * collapsed rail (same as every other icon-only control there).
 */
export function DirectionToggle({ className }: { className?: string }) {
    const direction = useDirection();
    const isRtl = direction === "rtl";

    return (
        <button
            type="button"
            onClick={toggleDirection}
            aria-pressed={isRtl}
            aria-label="Right-to-left layout"
            className={cn(
                "flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-background text-foreground outline-none transition-colors hover:bg-muted focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                className,
            )}
        >
            <ArrowLeftRight className="h-4 w-4" aria-hidden="true" />
        </button>
    );
}
