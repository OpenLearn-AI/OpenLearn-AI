"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { CoursesIndex } from "@/components/courses/CoursesIndex";

/**
 * Courses & Learning Hub (Batch 4.2, Swiss Editorial Grid).
 *
 * The page owns the masthead only; the list pattern (search, live
 * count, entry field, states) is the `CoursesIndex` component.
 *
 * Masthead hierarchy (the owner's correction E — the primary action
 * must be immediately discoverable): the display-scale page title
 * (a container-query clamp, so the scale follows the CONTENT column,
 * not the viewport) and the honest subtitle on one side, and the
 * single primary action — "+ Create New Course" as the app's filled
 * primary Button rendered as a link — at the inline end. One filled
 * control on an otherwise hairline-and-type page is the whole
 * hierarchy: the action is unmissable without the page becoming
 * loud. It renders in EVERY list state (populated, loading, error,
 * empty, and no-results) exactly as before — same route, same flow,
 * same pinned accessible name.
 *
 * Subtitle honesty (D10): "Courses you've created." — the previous
 * subtitle promised course materials and RAG knowledge bases, which
 * are Batch 4.3 surfaces that do not exist yet; the courses you own
 * are what this page actually shows.
 *
 * The `<main>` is the page's inline-size container (`@container`),
 * which drives the title clamp and the entry-field density inside
 * `CoursesIndex`.
 */
export default function CoursesPage() {
    return (
        <main className="@container mx-auto w-full max-w-7xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
            {/* Masthead — title, subtitle, and the primary action. */}
            <header className="grid gap-4 @3xl:grid-cols-[minmax(0,8fr)_minmax(0,4fr)] @3xl:items-end @3xl:gap-8">
                <div>
                    <h1 className="text-[clamp(1.875rem,4cqi,2.5rem)] font-semibold leading-[1.12] tracking-tight text-foreground">
                        Courses &amp; Learning Hub
                    </h1>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Courses you&rsquo;ve created.
                    </p>
                </div>
                <div className="flex @3xl:justify-end">
                    <Button render={<Link href="/courses/new" />}>
                        + Create New Course
                    </Button>
                </div>
            </header>

            <hr className="mt-6" />

            <CoursesIndex />
        </main>
    );
}
