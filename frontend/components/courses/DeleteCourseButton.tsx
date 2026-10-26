"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useDeleteCourse } from "@/features/courses/api/useCourseMutations";
import { ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/dialog";

/**
 * Delete-course action with explicit confirmation (Phase 4 Patch 8;
 * confirmation extracted onto the shared alert-dialog primitive in
 * Batch 3.2 — behavior preserved).
 *
 * Renders a "Delete Course" button. When clicked, it opens a modal
 * alert dialog ("Delete this course?" + Cancel / confirm buttons) so
 * the user can abort. The mutation is disabled while pending (prevents
 * double submission, and the dialog cannot be dismissed mid-deletion).
 * On success, the course cache is invalidated by the mutation and the
 * user is navigated to `redirectTo`.
 *
 * The dialog is the reusable `components/ui/dialog.tsx` primitive
 * (role="alertdialog", labelled by `courseTitle`, focus-trapped).
 * Error messages keep the same mapping as before and render inline
 * (role="alert", aria-live="assertive") while the dialog stays open.
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
    const [open, setOpen] = useState(false);

    const handleConfirm = () => {
        deleteCourse.mutate(courseId, {
            onSuccess: () => {
                setOpen(false);
                router.push(redirectTo);
            },
        });
    };

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
        <AlertDialog
            open={open}
            onOpenChange={(nextOpen) => {
                // While the deletion is in flight the dialog cannot be
                // dismissed (the pre-extraction panel was equally rigid);
                // the mutation itself closes it on success.
                if (!deleteCourse.isPending) {
                    setOpen(nextOpen);
                }
            }}
        >
            <AlertDialogTrigger
                render={
                    <Button
                        variant="destructive"
                        disabled={deleteCourse.isPending}
                    >
                        Delete Course
                    </Button>
                }
            />

            <AlertDialogContent aria-label={`Delete course: ${courseTitle}`}>
                <AlertDialogHeader>
                    <AlertDialogTitle>Delete this course?</AlertDialogTitle>
                    <AlertDialogDescription>
                        This will permanently delete{" "}
                        <span className="font-medium">{courseTitle}</span> and
                        cannot be undone.
                    </AlertDialogDescription>
                </AlertDialogHeader>

                {errorMessage && (
                    <p
                        role="alert"
                        aria-live="assertive"
                        className="text-sm text-destructive"
                    >
                        {errorMessage}
                    </p>
                )}

                <AlertDialogFooter>
                    <AlertDialogCancel disabled={deleteCourse.isPending}>
                        Cancel
                    </AlertDialogCancel>
                    <AlertDialogAction
                        variant="destructive"
                        size="sm"
                        onClick={handleConfirm}
                        disabled={deleteCourse.isPending}
                    >
                        {deleteCourse.isPending
                            ? "Deleting..."
                            : "Yes, delete it"}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}
