import Link from "next/link";

import { CourseForm } from "@/components/courses/CourseForm";
import { courseLinkClass } from "@/components/courses/OpenHubLink";

/**
 * Create Course (Batch 4.3 presentation pass on the Batch 2 pattern).
 *
 * The pinned heading ("Create Course" — the courses-crud E2E spec
 * waits for it) and the shared `CourseForm` are unchanged; the page
 * frame joins the courses family (a quiet back link, the editorial
 * masthead) and the subtitle states only what is true: materials
 * arrive on the course page afterwards (the Batch 4.3 hub).
 */
export default function NewCoursePage() {
    return (
        <main className="mx-auto w-full max-w-2xl min-h-screen bg-background px-4 py-8 sm:px-6 lg:px-8">
            <p>
                <Link href="/courses" className={courseLinkClass}>
                    All courses
                </Link>
            </p>

            <div className="mt-4">
                <h1 className="text-3xl font-semibold tracking-tight text-foreground">
                    Create Course
                </h1>

                <p className="mt-2 text-sm text-muted-foreground">
                    Set a title and an optional description — you can
                    add materials on the course page afterwards.
                </p>
            </div>

            <hr className="mt-6" />

            <div className="mt-8">
                <CourseForm mode="create" />
            </div>
        </main>
    );
}
