"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Onboarding journey visual (Batch 4.2 public-direction redesign).
 *
 * The product's identity composition — two arcs, two dots, and an
 * open center — animated for the onboarding experience's left column:
 *   - the two identity arcs draw themselves on once (SVG stroke
 *     dashoffset), in sequence;
 *   - the dots and the dashed connector fade into place after them;
 *   - the two main dots then keep a very quiet, slow "breathe"
 *     (opacity only), so the panel feels alive without greedy motion.
 *
 * Honesty constraint (kept from the identity visual, Q1): it
 * communicates identity and direction only — no dashboard, no
 * knowledge graph, no unimplemented capability is depicted.
 *
 * Motion/accessibility contract (mirrors the public motion rules):
 *   - All animations are CSS only, text-safe (opacity/stroke-dashoffset
 *     transforms only, no layout shift), and UNDER the global
 *     prefers-reduced-motion guard in globals.css, which collapses
 *     them to an instant final state. No JS is ever needed: with JS
 *     off, or after the animations have run, the SVG's attribute
 *     values ARE the resting composition.
 *   - Fully decorative: `aria-hidden` + `focusable="false"`; the
 *     step headings carry the meaning, so nothing is duplicated here.
 *   - Static geometry, no text, no directional reading order: RTL
 *     layouts need no mirroring; size is controlled by the container.
 *   - The visual identity matches the fixed dark public surfaces by
 *     design: identity strokes/dots read from the brass token layer
 *     (--primary) plus ambient halo mixes, never hardcoded colors.
 */

export function OnboardingJourneyVisual({
    className,
}: {
    className?: string;
}) {
    // Entrance (fade-in) + the long quiet breathe, per dot: the later
    // animation in the list owns opacity once it starts, so the dot
    // fades in, then all dots breathe together one step apart.
    const dotAnimation = (enterAt: number, breatheAt: number) =>
        `ol-enter 0.6s cubic-bezier(0.22, 0.61, 0.21, 1) ${enterAt}s both, ol-breathe 7s ease-in-out ${breatheAt}s infinite`;

    return (
        <div className={cn("relative", className)}>
            {/* Ambient halo behind the composition: the documented dark
                ambient brass mixes at their soft strength, fading out
                radially. Decorative only. */}
            <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-x-10 top-10 bottom-6 rounded-full bg-[radial-gradient(closest-side,var(--ambient-brass-soft),transparent)] opacity-70"
            />

            <svg
                viewBox="0 0 480 480"
                aria-hidden="true"
                focusable="false"
                className="relative h-auto w-full"
            >
                {/* Inner arc — the learner profile supporting the journey.
                    Draws on first (--ol-draw-length is the arc's rough
                    stroke length, generously rounded up). */}
                <path
                    d="M 116.4 206.9 A 128 128 0 1 1 356.0 294.1"
                    fill="none"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeDasharray={1200}
                    style={
                        {
                            "--ol-draw-length": 1200,
                            animation:
                                "ol-draw 1.5s cubic-bezier(0.4, 0, 0.2, 1) both",
                        } as React.CSSProperties
                    }
                    className="stroke-primary/35"
                />

                {/* Outer arc — the learning journey, open at the upper
                    right. Starts slightly after the inner arc. */}
                <path
                    d="M 256.2 425.3 A 186 186 0 1 1 408.6 318.6"
                    fill="none"
                    strokeWidth={3}
                    strokeLinecap="round"
                    strokeDasharray={1900}
                    style={
                        {
                            "--ol-draw-length": 1900,
                            animation:
                                "ol-draw 2.1s cubic-bezier(0.4, 0, 0.2, 1) 0.5s both",
                        } as React.CSSProperties
                    }
                    className="stroke-primary"
                />

                {/* Milestone nodes along the journey, growing with
                    progress. They fade in as the outer arc passes them. */}
                <circle
                    cx="56.8"
                    cy="272.3"
                    r="6"
                    className="fill-primary/45"
                    style={{ animation: dotAnimation(2.2, 3.2) }}
                />
                <circle
                    cx="176.4"
                    cy="65.2"
                    r="8"
                    className="fill-primary/55"
                    style={{ animation: dotAnimation(2.5, 3.4) }}
                />
                <circle
                    cx="401.1"
                    cy="147.0"
                    r="10"
                    className="fill-primary/70"
                    style={{ animation: dotAnimation(2.8, 3.6) }}
                />

                {/* Dot 1 — the learner, at the journey's current position
                    (enters last, after both arcs are drawn). */}
                <circle
                    cx="408.6"
                    cy="318.6"
                    r="14"
                    className="fill-primary"
                    style={{ animation: dotAnimation(3.0, 3.8) }}
                />

                {/* Dot 2 — the next step, carried by the profile arc. */}
                <circle
                    cx="356.0"
                    cy="294.1"
                    r="10"
                    className="fill-primary/60"
                    style={{ animation: dotAnimation(3.2, 4.0) }}
                />

                {/* Dashed connector toward the open center — stops short:
                    the center stays open, as in the identity composition. */}
                <path
                    d="M 341.5 287.3 L 292.6 264.5"
                    fill="none"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeDasharray="0.1 11"
                    className="ol-enter ol-enter-delay-3 stroke-primary/40"
                />
            </svg>
        </div>
    );
}
