import Link from "next/link";

import { cn } from "@/lib/utils";

/**
 * The shared quiet page-link grammar (Batch 4.2, Swiss Editorial Grid).
 *
 * One vocabulary for every in-content link on the dashboard and the
 * courses list: inherit the surrounding text color, no resting
 * underline, a 1px brass underline that appears on hover
 * (`decoration-ring`, 3px offset), and the page-wide focus treatment
 * (2px brass outline at 3px offset). Color is never the only signal —
 * the underline/outline carry hover and focus.
 *
 * The courses surfaces render user-authored titles and descriptions
 * as plain text (no rich links), so this grammar is deliberately
 * attached to real navigation actions only (Edit, Open Hub, the
 * facts-band links).
 */
export const courseLinkClass =
    "text-sm text-inherit no-underline underline-offset-[3px] hover:underline hover:decoration-ring focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-ring";

/**
 * The entry-TITLE link grammar (Batch 4.2 corrections, A2/A8): the
 * same quiet vocabulary as `courseLinkClass`, at the title's
 * inherited size and weight — the ruled entry's title IS the link to
 * the course hub, so the largest, most natural target carries the
 * primary navigation without adding any container or chrome.
 *
 * The courses surfaces render user-authored titles and descriptions
 * as plain text inside these links (no rich links), and the title
 * keeps its heading role — `<h2>/<h3>` wrapping the link preserves
 * both the document outline and the accessible name.
 */
export const entryTitleLinkClass =
    "text-inherit no-underline underline-offset-[3px] hover:underline hover:decoration-ring focus-visible:outline-2 focus-visible:outline-offset-[3px] focus-visible:outline-ring";

/**
 * The "Open Hub →" course-entry action — the pinned link name the
 * courses-crud E2E spec clicks (`getByRole("link", { name: "Open Hub →" })`).
 *
 * Contract notes:
 * - The arrow is a literal text character INSIDE the accessible name
 *   (never an SVG icon and never `aria-hidden`), so the pinned name
 *   survives verbatim.
 * - In RTL compositions the arrow MIRRORS (a "→" pointing with the
 *   reading direction) via a scale flip, and the hover nudge travels
 *   with the reading direction too — direction as composition, not
 *   translation.
 * - Rendered emphasized (medium weight) beside the quieter "Edit"
 *   link in the entry's action row.
 */
export function OpenHubLink({ courseId }: { courseId: string }) {
    return (
        <Link
            href={`/courses/${courseId}`}
            className={cn(courseLinkClass, "group/link font-medium")}
        >
            Open Hub{" "}
            <span className="inline-block rtl:-scale-x-100 group-hover/link:translate-x-0.5 rtl:group-hover/link:-translate-x-0.5">
                →
            </span>
        </Link>
    );
}
