"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCourses } from "@/features/courses/api/useCourses";

export default function CoursesPage() {
    const [searchQuery, setSearchQuery] = useState("");

    const {
        data: courses,
        isLoading,
        isError,
        error,
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
                        Courses & Learning Hub
                    </h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        Manage your active learning modules, course materials, and RAG knowledge bases.
                    </p>
                </div>
                <Link href="/courses/new">
                    <Button>+ Create New Course</Button>
                </Link>
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
                {isLoading ? (
                    <div className="col-span-full text-center py-12 bg-card rounded-2xl border border-border">
                        <p className="text-muted-foreground text-sm">
                            Loading courses...
                        </p>
                    </div>
                ) : isError ? (
                    <div className="col-span-full text-center py-12 bg-card rounded-2xl border border-border">
                        <p className="text-destructive text-sm">
                            {error instanceof Error
                                ? error.message
                                : "Failed to load courses."}
                        </p>
                    </div>
                ) : filteredCourses.length > 0 ? (
                    filteredCourses.map((course) => (
                        <div
                            key={course.id}
                            className="bg-card rounded-2xl border border-border p-6 shadow-xs flex flex-col justify-between space-y-4 hover:border-primary/50 transition"
                        >
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
                                        {new Date(
                                            course.created_at,
                                        ).toLocaleDateString()}
                                    </span>

                                    <div className="flex items-center gap-2">
                                        <Link
                                            href={`/courses/${course.id}/edit`}
                                        >
                                            <Button
                                                variant="outline"
                                                size="sm"
                                            >
                                                Edit
                                            </Button>
                                        </Link>

                                        <Link
                                            href={`/courses/${course.id}`}
                                        >
                                            <Button size="sm">
                                                Open Hub &rarr;
                                            </Button>
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="col-span-full text-center py-12 bg-card rounded-2xl border border-border">
                        <p className="text-muted-foreground text-sm">
                            {searchQuery
                                ? "No courses found matching your search."
                                : "No courses found."}
                        </p>
                    </div>
                )}
            </div>
        </main>
    );
}