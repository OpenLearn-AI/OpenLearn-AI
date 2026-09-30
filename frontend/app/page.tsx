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
                    Your Personal AI-Powered Learning Hub
                </h1>
                <p className="text-primary-foreground/80 text-sm max-w-2xl">
                    Upload your course materials, interact with intelligent RAG
                    assistants, explore dynamic knowledge graphs, and master your
                    subjects with custom generated quizzes and flashcards.
                </p>
                <div className="pt-2">
                    {!isLoading &&
                        (isAuthenticated ? (
                            <Button
                                size="lg"
                                render={<Link href="/dashboard" />}
                            >
                                Go to Dashboard
                            </Button>
                        ) : (
                            <Button
                                size="lg"
                                render={<Link href="/login" />}
                            >
                                Get Started - Sign In
                            </Button>
                        ))}
                </div>
            </div>

            {/* Features & Quick Actions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Quick Course / Material Actions */}
                <div className="bg-card p-6 rounded-2xl border border-border shadow-xs space-y-4 flex flex-col justify-between transition-colors">
                    <div className="space-y-2">
                        <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                            Materials &amp; RAG
                        </span>
                        <h3 className="font-bold text-card-foreground text-lg">
                            Start Learning a New Subject
                        </h3>
                        <p className="text-xs text-muted-foreground">
                            Create a course and upload study documents to generate
                            an adaptive learning path.
                        </p>
                    </div>
                    <div className="flex gap-3 pt-2">
                        <Button
                            className="flex-1"
                            render={<Link href="/courses/new" />}
                        >
                            Create Course
                        </Button>
                        <Button
                            variant="outline"
                            className="flex-1"
                            render={<Link href="/courses" />}
                        >
                            View My Materials
                        </Button>
                    </div>
                </div>

                {/* AI Tools & Capabilities */}
                <div className="bg-card p-6 rounded-2xl border border-border shadow-xs space-y-4 flex flex-col justify-between transition-colors">
                    <div className="space-y-2">
                        <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                            Platform Features
                        </span>
                        <h3 className="font-bold text-card-foreground text-lg">
                            Interactive AI Tools
                        </h3>
                        <p className="text-xs text-muted-foreground">
                            Leverage cutting-edge models to accelerate your
                            comprehension.
                        </p>
                    </div>
                    <div className="grid grid-cols-2 gap-3 pt-2">
                        <Link
                            href="/dashboard"
                            className="p-3 rounded-xl border border-border bg-secondary/50 hover:border-primary/50 hover:bg-secondary transition group block"
                        >
                            <div className="font-semibold text-sm text-card-foreground group-hover:text-primary">
                                RAG Chat
                            </div>
                            <div className="text-xs text-muted-foreground mt-0.5">
                                Ask questions on your docs
                            </div>
                        </Link>
                        <Link
                            href="/dashboard"
                            className="p-3 rounded-xl border border-border bg-secondary/50 hover:border-primary/50 hover:bg-secondary transition group block"
                        >
                            <div className="font-semibold text-sm text-card-foreground group-hover:text-primary">
                                Knowledge Graph
                            </div>
                            <div className="text-xs text-muted-foreground mt-0.5">
                                Visualize concepts map
                            </div>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
