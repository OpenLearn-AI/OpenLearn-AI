"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useDeleteCourse } from "@/features/courses/api/useCourseMutations";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";

/**
 * Delete-course action with explicit confirmation (Phase 4 Patch 8).
 *
 * Renders a "Delete" button. When clicked, it reveals a confirmation
 * panel ("Are you sure?" + Cancel / Delete buttons) so the user can
 * abort. The mutation is disabled while pending (prevents double
 * submission). On success, the course cache is invalidated by the
 * mutation and the user is navigated to `/courses`.
 *
 * The confirmation panel is inline (no external dialog dependency)
 * and accessible (role="alertdialog", aria-live for error messages).
 */
export function DeleteCourseButton({
    courseId,
    courseTitle,
    redirectTo = "/courses",
}: {
    courseId: string;
    courseTitle: string;
    redirectTo?: string;
}) {
    const router = useRouter();
    const deleteCourse = useDeleteCourse();
    const [confirming, setConfirming] = useState(false);

    const handleConfirm = () => {
        deleteCourse.mutate(courseId, {
            onSuccess: () => {
                setConfirming(false);
                router.push(redirectTo);
            },
        });
    };

    const handleCancel = () => {
        setConfirming(false);
    };

    if (!confirming) {
        return (
            <Button
                variant="destructive"
                size="sm"
                onClick={() => setConfirming(true)}
                disabled={deleteCourse.isPending}
            >
                Delete Course
            </Button>
        );
    }

    const errorMessage =
        deleteCourse.error instanceof ApiError
            ? deleteCourse.error.status === 404
                ? "This course no longer exists."
                : deleteCourse.error.status === 403
                  ? "You do not have permission to delete this course."
                  : deleteCourse.error.message
            : deleteCourse.error instanceof Error
                ? deleteCourse.error.message
                : null;

    return (
        <div
            role="alertdialog"
            aria-label={`Delete course: ${courseTitle}`}
            className="space-y-4 rounded-2xl border border-destructive/30 bg-destructive/5 p-6"
        >
            <div className="space-y-1">
                <h3 className="text-base font-bold text-foreground">
                    Delete this course?
                </h3>
                <p className="text-sm text-muted-foreground">
                    This will permanently delete{" "}
                    <span className="font-medium">{courseTitle}</span> and
                    cannot be undone.
                </p>
            </div>

            {errorMessage && (
                <p
                    role="alert"
                    aria-live="assertive"
                    className="text-sm text-destructive"
                >
                    {errorMessage}
                </p>
            )}

            <div className="flex gap-3">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancel}
                    disabled={deleteCourse.isPending}
                >
                    Cancel
                </Button>
                <Button
                    variant="destructive"
                    size="sm"
                    onClick={handleConfirm}
                    disabled={deleteCourse.isPending}
                >
                    {deleteCourse.isPending
                        ? "Deleting..."
                        : "Yes, delete it"}
                </Button>
            </div>
        </div>
    );
}
