"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useMe } from "@/features/auth/api/useMe";
import { Button } from "@/components/ui/button";

export default function Home() {
    const { isAuthenticated, isLoading: authLoading } = useAuth();
    const { isLoading: userLoading } = useMe();

    const isLoading = authLoading || userLoading;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground p-6 sm:p-8 rounded-2xl shadow-sm space-y-4">
                <div className="inline-block bg-primary-foreground/10 text-primary-foreground px-3 py-1 rounded-lg text-xs font-medium backdrop-blur-xs">
                    Welcome to OpenLearn AI
                </div>
                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
                    One home for your courses — and a clearer picture of what
                    you know
                </h1>
                <p className="text-primary-foreground/80 text-sm max-w-2xl">
                    Study materials end up scattered across folders, drives,
                    and platforms, and it is hard to see what you have actually
                    mastered and what still needs review. OpenLearn AI brings
                    your courses together in one place today, and is building
                    toward AI-assisted insight into your own learning.
                </p>
                <div className="pt-2 flex flex-wrap gap-3">
                    {!isLoading &&
                        (isAuthenticated ? (
                            <Button
                                size="lg"
                                render={<Link href="/dashboard" />}
                            >
                                Go to Dashboard
                            </Button>
                        ) : (
                            <>
                                <Button
                                    size="lg"
                                    render={<Link href="/register" />}
                                >
                                    Get Started
                                </Button>
                                <Button
                                    size="lg"
                                    variant="outline"
                                    render={<Link href="/login" />}
                                >
                                    Log in
                                </Button>
                            </>
                        ))}
                </div>
            </div>

            {/* Capabilities Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Available today */}
                <div className="bg-card p-6 rounded-2xl border border-border shadow-xs space-y-4 flex flex-col justify-between transition-colors">
                    <div className="space-y-2">
                        <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                            Available today
                        </span>
                        <h3 className="font-bold text-card-foreground text-lg">
                            Organize your learning
                        </h3>
                        <p className="text-xs text-muted-foreground">
                            Create courses, keep them in one place, and set up
                            your learner profile so the platform fits how you
                            study.
                        </p>
                    </div>
                    <div className="flex gap-3 pt-2">
                        <Button
                            className="flex-1"
                            render={<Link href="/courses/new" />}
                        >
                            Create a course
                        </Button>
                        <Button
                            variant="outline"
                            className="flex-1"
                            render={<Link href="/courses" />}
                        >
                            Browse courses
                        </Button>
                    </div>
                </div>

                {/* Future direction — clearly labeled, not clickable */}
                <div className="bg-card p-6 rounded-2xl border border-border shadow-xs space-y-4 flex flex-col justify-between transition-colors">
                    <div className="space-y-2">
                        <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                                Where we&apos;re headed
                            </span>
                            <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-md font-semibold">
                                Planned
                            </span>
                        </div>
                        <h3 className="font-bold text-card-foreground text-lg">
                            On the roadmap
                        </h3>
                        <p className="text-xs text-muted-foreground">
                            These capabilities are planned and are not part of
                            the product yet.
                        </p>
                    </div>
                    <ul className="space-y-2 pt-2 text-sm text-card-foreground">
                        <li className="flex items-center justify-between gap-2 border border-border rounded-xl px-3 py-2 bg-secondary/50">
                            <span>Material upload and processing</span>
                            <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-md font-semibold">
                                Planned
                            </span>
                        </li>
                        <li className="flex items-center justify-between gap-2 border border-border rounded-xl px-3 py-2 bg-secondary/50">
                            <span>AI chat on your course materials</span>
                            <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-md font-semibold">
                                Planned
                            </span>
                        </li>
                        <li className="flex items-center justify-between gap-2 border border-border rounded-xl px-3 py-2 bg-secondary/50">
                            <span>Knowledge graphs of course concepts</span>
                            <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-md font-semibold">
                                Planned
                            </span>
                        </li>
                        <li className="flex items-center justify-between gap-2 border border-border rounded-xl px-3 py-2 bg-secondary/50">
                            <span>
                                Adaptive learning paths, quizzes, and
                                flashcards
                            </span>
                            <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-md font-semibold">
                                Planned
                            </span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
