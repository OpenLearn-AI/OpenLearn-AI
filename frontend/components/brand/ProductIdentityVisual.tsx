/**
 * Product Identity Visual (Batch 4.1 — owner decision Q1).
 *
 * An original, maintainable composition that communicates OpenLearn AI's
 * identity: two arcs, two dots, and an open center — a connected,
 * organized learning journey.
 *
 * Reading of the composition (deliberate, not decorative clutter):
 *   - The outer arc is the learning journey, carrying three growing
 *     milestone nodes; it is open at the upper right — the journey
 *     continues, nothing is "finished".
 *   - The inner arc is the learner profile that supports the journey;
 *     it carries the second dot.
 *   - The two dots (the learner on the outer arc, the next step on the
 *     inner arc) are tied into the composition by the arcs and a short
 *     dashed connector running toward the center — and stopping short.
 *     The center stays open: room for the product to grow
 *     (personalization, AI assistance) without claiming any of it is
 *     here today.
 *
 * Honesty constraint (Q1): the visual communicates identity and
 * direction only. It deliberately does NOT depict a dashboard, a
 * knowledge graph, recommendations, or any specific unimplemented
 * capability.
 *
 * Implementation constraints honored:
 *   - Native SVG + semantic design tokens only (the stroke and fill
 *     color utilities map to the Light Steel token layer), so Light and
 *     Dark themes both work with zero raster assets and no
 *     theme-specific variants (Q6).
 *   - Fully decorative: `aria-hidden` + `focusable="false"`; the hero's
 *     headings carry the meaning, so no accessible name is duplicated
 *     here.
 *   - Static composition — no animation — so reduced-motion preferences
 *     are honored trivially and motion is never needed to understand it.
 *   - Abstract geometry: no text, no directional reading order, so RTL
 *     layouts need no mirroring; size is controlled by the container.
 */

export function ProductIdentityVisual({
    className,
}: {
    className?: string;
}) {
    return (
        <svg
            viewBox="0 0 480 480"
            aria-hidden="true"
            focusable="false"
            className={className}
        >
            {/* Inner arc — the learner profile supporting the journey. */}
            <path
                d="M 116.4 206.9 A 128 128 0 1 1 356.0 294.1"
                fill="none"
                strokeWidth={2}
                strokeLinecap="round"
                className="stroke-primary/35"
            />

            {/* Outer arc — the learning journey, open at the upper right. */}
            <path
                d="M 256.2 425.3 A 186 186 0 1 1 408.6 318.6"
                fill="none"
                strokeWidth={3}
                strokeLinecap="round"
                className="stroke-primary"
            />

            {/* Milestone nodes along the journey, growing with progress. */}
            <circle cx="56.8" cy="272.3" r="6" className="fill-primary/45" />
            <circle cx="176.4" cy="65.2" r="8" className="fill-primary/55" />
            <circle cx="401.1" cy="147.0" r="10" className="fill-primary/70" />

            {/* Dot 1 — the learner, at the journey's current position. */}
            <circle cx="408.6" cy="318.6" r="14" className="fill-primary" />

            {/* Dot 2 — the next step, carried by the profile arc. */}
            <circle cx="356.0" cy="294.1" r="10" className="fill-primary/60" />

            {/* Dashed connector toward the open center — it stops short:
                the center belongs to what the product will become, and
                the visual must not imply it is already built. */}
            <path
                d="M 341.5 287.3 L 292.6 264.5"
                fill="none"
                strokeWidth={2}
                strokeLinecap="round"
                strokeDasharray="0.1 11"
                className="stroke-primary/40"
            />
        </svg>
    );
}
