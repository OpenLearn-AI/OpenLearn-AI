import Link from "next/link";

import { Button } from "@/components/ui/button";
import type { Course } from "@/features/courses/schemas";

/**
 * Shared course presentation card (D2 / D9).
 *
 * Presentational only — no API calls, no business logic, no mutation
 * hooks. Consumed by the courses list and the dashboard so both
 * surfaces render courses identically.
 *
 * Token-only styling (no raw slate-/indigo- classes) with correct
 * dark-mode behavior via the established token system.
 */
export function CourseCard({ course }: { course: Course }) {
    return (
        <div className="bg-card rounded-2xl border border-border p-6 shadow-xs flex flex-col justify-between space-y-4 hover:border-primary/50 transition">
            <div className="space-y-2">
                <div className="flex justify-between items-start gap-2">
                    <h2 className="text-xl font-bold text-foreground">
                        {course.title}
                    </h2>
                    <span className="text-xs bg-secondary text-secondary-foreground px-2.5 py-1 rounded-full font-medium shrink-0">
                        Course
                    </span>
                </div>

                <p className="text-sm text-muted-foreground line-clamp-2">
                    {course.description || "No description"}
                </p>
            </div>

            <div className="space-y-3 pt-2 border-t border-border">
                <div className="flex justify-between items-center pt-2">
                    <span className="text-xs text-muted-foreground">
                        Created{" "}
                        {new Date(course.created_at).toLocaleDateString()}
                    </span>

                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            render={<Link href={`/courses/${course.id}/edit`} />}
                        >
                            Edit
                        </Button>

                        <Button
                            size="sm"
                            render={<Link href={`/courses/${course.id}`} />}
                        >
                            Open Hub &rarr;
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
