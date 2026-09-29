"use client";

import Link from "next/link";
import { UserInfo } from "@/components/auth/UserInfo";
import { LogoutButton } from "@/components/auth/LogoutButton";
import { CourseCard } from "@/components/CourseCard";
import { LoadingBlock } from "@/components/state/LoadingBlock";
import { ErrorState } from "@/components/state/ErrorState";
import { EmptyState } from "@/components/state/EmptyState";
import { Button } from "@/components/ui/button";
import { useCourses } from "@/features/courses/api/useCourses";

export default function DashboardPage() {
    const { data: courses, isLoading, isError, error, refetch } = useCourses();

    const courseCount = courses?.length ?? 0;

    return (
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8 bg-background min-h-screen">
            {/* Header Banner */}
            <div className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground p-6 sm:p-8 rounded-2xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="space-y-1">
                    <span className="bg-primary-foreground/10 text-primary-foreground/90 text-xs px-3 py-1 rounded-full font-medium">
                        Student Dashboard
                    </span>
                    <h1 className="text-2xl sm:text-3xl font-bold tracking-tight pt-1">
                        Welcome Back!
                    </h1>
                    <p className="text-primary-foreground/80 text-sm max-w-xl">
                        Continue your adaptive learning journey, interact with
                        your documents via RAG, and track your active modules.
                    </p>
                </div>
            </div>

            {/* Quick Stats Grid — real data only */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Active Materials
                    </span>
                    <div className="text-2xl font-bold text-foreground">
                        {courseCount} {courseCount === 1 ? "Course" : "Courses"}
                    </div>
                    <p className="text-xs text-muted-foreground">
                        {courseCount > 0
                            ? "View in your materials list"
                            : "Create your first course to get started"}
                    </p>
                </div>
                <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        RAG Sessions
                    </span>
                    <div className="text-2xl font-bold text-foreground">
                        Coming soon
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Not available yet
                    </p>
                </div>
                <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Generated Quizzes
                    </span>
                    <div className="text-2xl font-bold text-foreground">
                        Coming soon
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Not available yet
                    </p>
                </div>
                <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                        Knowledge Nodes
                    </span>
                    <div className="text-2xl font-bold text-foreground">
                        Coming soon
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Not available yet
                    </p>
                </div>
            </div>

            {/* Main Tools & Chat Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left 2 Columns: Courses + Quick Access */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Your Courses */}
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                        <div className="flex justify-between items-center">
                            <div>
                                <h3 className="font-bold text-foreground text-base">
                                    Your Courses
                                </h3>
                                <p className="text-xs text-muted-foreground">
                                    Pick up where you left off.
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

                        {isLoading ? (
                            <LoadingBlock message="Loading your courses..." />
                        ) : isError ? (
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

                    {/* RAG Chat Quick Access Box */}
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                        <div className="flex justify-between items-center">
                            <div>
                                <h3 className="font-bold text-foreground text-base">
                                    Intelligent RAG Assistant
                                </h3>
                                <p className="text-xs text-muted-foreground">
                                    Ask questions directly based on your uploaded
                                    course files.
                                </p>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                render={<Link href="/courses" />}
                            >
                                Open Chat &rarr;
                            </Button>
                        </div>
                        <div className="bg-secondary/50 p-4 rounded-xl border border-border flex items-center justify-between">
                            <span className="text-xs text-muted-foreground font-medium">
                                Coming soon
                            </span>
                            <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-md font-semibold">
                                Planned
                            </span>
                        </div>
                    </div>

                    {/* Knowledge Graph Preview Box */}
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                        <div className="flex justify-between items-center">
                            <div>
                                <h3 className="font-bold text-foreground text-base">
                                    Knowledge Graph Visualizer
                                </h3>
                                <p className="text-xs text-muted-foreground">
                                    Explore relationship maps between core
                                    concepts.
                                </p>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                render={<Link href="/courses" />}
                            >
                                View Graph &rarr;
                            </Button>
                        </div>
                        <div className="h-32 bg-secondary/50 rounded-xl border border-dashed border-border flex items-center justify-center text-xs text-muted-foreground">
                            Coming soon
                        </div>
                    </div>
                </div>

                {/* Right Column: User Info & Session Controls */}
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

                    {/* Session Management Card */}
                    <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4 flex flex-col justify-between">
                        <div>
                            <h3 className="font-bold text-foreground text-base mb-1">
                                Session Control
                            </h3>
                            <p className="text-xs text-muted-foreground">
                                Securely manage your active login session.
                            </p>
                        </div>
                        <div className="pt-2">
                            <LogoutButton />
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
