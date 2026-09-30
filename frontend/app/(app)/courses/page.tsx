"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CourseCard } from "@/components/CourseCard";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { EmptyState } from "@/components/state/EmptyState";
import { useCourses } from "@/features/courses/api/useCourses";
import Link from "next/link";

export default function CoursesPage() {
    const [searchQuery, setSearchQuery] = useState("");

    const {
        data: courses,
        isLoading,
        isError,
        error,
        refetch,
    } = useCourses();

    const filteredCourses = (courses ?? []).filter(
        (course) =>
            course.title
                .toLowerCase()
                .includes(searchQuery.toLowerCase()) ||
            (course.description ?? "")
                .toLowerCase()
                .includes(searchQuery.toLowerCase()),
    );

    return (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8 bg-background min-h-screen">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">
                        Courses &amp; Learning Hub
                    </h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Manage your active learning modules, course materials,
                        and RAG knowledge bases.
                    </p>
                </div>
                <Button render={<Link href="/courses/new" />}>
                    + Create New Course
                </Button>
            </div>

            {/* Search & Filter Bar */}
            <div className="flex items-center gap-4">
                <div className="w-full md:max-w-md">
                    <Input
                        placeholder="Search your courses or topics..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="bg-card text-foreground"
                    />
                </div>
            </div>

            {/* Courses Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {isLoading ? (
                    <div className="col-span-full">
                        <LoadingBlock message="Loading courses..." />
                    </div>
                ) : isError ? (
                    <div className="col-span-full">
                        <ErrorState
                            message={
                                error instanceof Error
                                    ? error.message
                                    : "Failed to load courses."
                            }
                            onRetry={() => void refetch()}
                        />
                    </div>
                ) : filteredCourses.length > 0 ? (
                    filteredCourses.map((course) => (
                        <CourseCard key={course.id} course={course} />
                    ))
                ) : (
                    <div className="col-span-full">
                        <EmptyState
                            message={
                                searchQuery
                                    ? "No courses found matching your search."
                                    : "You don't have any courses yet."
                            }
                            actionHref={
                                searchQuery ? undefined : "/courses/new"
                            }
                            actionLabel={
                                searchQuery ? undefined : "Create your first course"
                            }
                        />
                    </div>
                )}
            </div>
        </main>
    );
}
