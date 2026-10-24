"use client";

import Link from "next/link";
import { UserInfo } from "@/components/auth/UserInfo";
import { CourseCard } from "@/components/CourseCard";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { EmptyState } from "@/components/state/EmptyState";
import { Button } from "@/components/ui/button";
import { useCourses } from "@/features/courses/api/useCourses";
import { useProfile } from "@/features/profile/api/useProfile";
import type { Profile } from "@/features/profile/schemas";

/**
 * The six user-facing content fields of `ProfileResponse` (the identity
 * fields `id`/`user_id` are excluded). This is the denominator of the
 * profile-completeness measure — the same derivation recorded in the
 * ledger's Batch 1.4 real-metric inventory: a field counts as carried
 * when it is non-null AND non-empty. Four fields are non-nullable in the
 * contract (guaranteed present once a profile exists); `university` and
 * `learning_style_vark` are the only variable ones.
 */
const PROFILE_FIELD_COUNT = 6;

function countMissingProfileFields(profile: Profile): number {
    const values = [
        profile.education_level,
        profile.major,
        profile.preferred_language,
        profile.university,
        profile.learning_style_vark,
        profile.daily_available_minutes,
    ];
    const carried = values.filter(
        (value) => value !== null && String(value).trim() !== "",
    ).length;
    return PROFILE_FIELD_COUNT - carried;
}

export default function DashboardPage() {
    const {
        data: courses,
        isLoading: coursesLoading,
        isError: coursesError,
        error,
        refetch,
    } = useCourses();
    const {
        data: profile,
        isLoading: profileLoading,
        isError: profileError,
    } = useProfile();

    const courseCount = courses?.length ?? 0;
    const missingProfileFields = profile === null || profile === undefined
        ? null
        : countMissingProfileFields(profile);

    return (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8 bg-background min-h-screen">
            {/* Header Banner */}
            <div className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground p-6 sm:p-8 rounded-2xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="space-y-1">
                    <span className="bg-primary-foreground/10 text-primary-foreground/90 text-xs px-3 py-1 rounded-full font-medium">
                        Dashboard
                    </span>
                    <h1 className="text-2xl sm:text-3xl font-bold tracking-tight pt-1">
                        Welcome Back!
                    </h1>
                    <p className="text-primary-foreground/80 text-sm max-w-xl">
                        Manage your courses and keep your profile up to date.
                    </p>
                </div>
            </div>

            {/* Quick Stats Grid — real data only (owner-scoped course count
                via GET /v1/courses, and the profile-field measure derived
                from GET /v1/users/me) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Your Courses
                    </span>
                    <div className="text-2xl font-bold text-foreground">
                        {coursesLoading
                            ? "Loading..."
                            : coursesError
                              ? "-"
                              : `${courseCount} ${courseCount === 1 ? "Course" : "Courses"}`}
                    </div>
                    <p className="text-xs text-muted-foreground">
                        {coursesLoading
                            ? "Fetching your courses."
                            : coursesError
                              ? "Couldn't load your courses."
                              : courseCount > 0
                                ? "The courses you own. Browse them below."
                                : "Create your first course to get started."}
                    </p>
                </div>
                <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Profile
                    </span>
                    <div className="text-2xl font-bold text-foreground">
                        {profileLoading
                            ? "Loading..."
                            : profileError
                              ? "-"
                              : profile === null
                                ? "Not set up"
                                : missingProfileFields === 0
                                  ? "Complete"
                                  : `${missingProfileFields} of ${PROFILE_FIELD_COUNT} fields left`}
                    </div>
                    <p className="text-xs text-muted-foreground">
                        {profileLoading
                            ? "Fetching your profile."
                            : profileError
                              ? "Couldn't load your profile."
                              : profile === null
                                ? "Create your profile to personalize your dashboard."
                                : missingProfileFields === 0
                                  ? "All profile fields are filled in."
                                  : "Fields you can still fill in on your profile."}
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left 2 Columns: Courses + Quick Actions */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Your Courses */}
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                        <div className="flex justify-between items-center">
                            <div>
                                <h3 className="font-bold text-foreground text-base">
                                    Your Courses
                                </h3>
                                <p className="text-xs text-muted-foreground">
                                    The four most recently created of your
                                    courses.
                                </p>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                render={<Link href="/courses" />}
                            >
                                View all &rarr;
                            </Button>
                        </div>

                        {coursesLoading ? (
                            <LoadingBlock message="Loading your courses..." />
                        ) : coursesError ? (
                            <ErrorState
                                message={
                                    error instanceof Error
                                        ? error.message
                                        : "Failed to load your courses."
                                }
                                onRetry={() => void refetch()}
                            />
                        ) : courseCount === 0 ? (
                            <EmptyState
                                message="You don't have any courses yet."
                                actionHref="/courses/new"
                                actionLabel="Create your first course"
                            />
                        ) : (
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {courses!
                                    .slice(0, 4)
                                    .map((course) => (
                                        <CourseCard
                                            key={course.id}
                                            course={course}
                                        />
                                    ))}
                            </div>
                        )}
                    </div>

                    {/* Quick Actions — real destinations only */}
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                        <div>
                            <h3 className="font-bold text-foreground text-base">
                                Quick Actions
                            </h3>
                            <p className="text-xs text-muted-foreground">
                                Things you can do in the product today.
                            </p>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <Button
                                variant="outline"
                                size="sm"
                                render={<Link href="/courses/new" />}
                            >
                                Create a course
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                render={<Link href="/courses" />}
                            >
                                Browse your courses
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                render={<Link href="/profile" />}
                            >
                                Update your profile
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Right Column: User Info. Logout moved to the shared
                    shell account region in Batch 3.3 — the former
                    Dashboard-only Session Control card hosted the same
                    LogoutButton component and was removed once the shell
                    replacement was in place. */}
                <div className="space-y-6">
                    {/* User Profile Card */}
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                        <h3 className="font-bold text-foreground text-base border-b border-border pb-3">
                            User Profile
                        </h3>
                        <div className="bg-secondary/50 p-4 rounded-xl border border-border">
                            <UserInfo />
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
