"use client";

import Link from "next/link";
import { RequireAuth } from "@/components/auth/RequireAuth";
import { UserInfo } from "@/components/auth/UserInfo";
import { LogoutButton } from "@/components/auth/LogoutButton";

export default function DashboardPage() {
    return (
        <RequireAuth>
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8 bg-background min-h-screen">

                {/* Header Banner */}
                <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-indigo-700 dark:from-indigo-950 dark:via-indigo-900 dark:to-indigo-800 text-white p-6 sm:p-8 rounded-2xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div className="space-y-1">
                        <span className="bg-white/10 text-indigo-100 text-xs px-3 py-1 rounded-full font-medium">
                            Student Dashboard
                        </span>
                        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight pt-1">
                            Welcome Back!
                        </h1>
                        <p className="text-indigo-100 text-sm max-w-xl">
                            Continue your adaptive learning journey, interact with your documents via RAG, and track your active modules.
                        </p>
                    </div>
                </div>

                {/* Quick Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Active Materials</span>
                        <div className="text-2xl font-bold text-foreground">4 Courses</div>
                        <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium"> 2 updated recently</p>
                    </div>
                    <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">RAG Sessions</span>
                        <div className="text-2xl font-bold text-foreground">12 Queries</div>
                        <p className="text-xs text-primary font-medium"> High accuracy match</p>
                    </div>
                    <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Generated Quizzes</span>
                        <div className="text-2xl font-bold text-foreground">8 Quizzes</div>
                        <p className="text-xs text-muted-foreground">Avg. Score: 85%</p>
                    </div>
                    <div className="bg-card p-5 rounded-2xl border border-border shadow-xs space-y-1">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Knowledge Nodes</span>
                        <div className="text-2xl font-bold text-foreground">142 Concepts</div>
                        <p className="text-xs text-primary font-medium"> Fully mapped</p>
                    </div>
                </div>

                {/* Main Tools & Chat Section */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Left 2 Columns: Quick Access to RAG & Materials */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* RAG Chat Quick Access Box */}
                        <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h3 className="font-bold text-foreground text-base"> Intelligent RAG Assistant</h3>
                                    <p className="text-xs text-muted-foreground">Ask questions directly based on your uploaded course files.</p>
                                </div>
                                <Link href="/courses" className="text-xs font-semibold text-primary hover:opacity-80 bg-secondary px-3 py-1.5 rounded-xl transition">
                                    Open Chat &rarr;
                                </Link>
                            </div>
                            <div className="bg-secondary/50 p-4 rounded-xl border border-border flex items-center justify-between">
                                <span className="text-xs text-secondary-foreground font-medium">Active Context: Advanced Software Architecture.pdf</span>
                                <span className="text-[10px] bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 px-2 py-0.5 rounded-md font-semibold">Ready</span>
                            </div>
                        </div>

                        {/* Knowledge Graph Preview Box */}
                        <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                            <div className="flex justify-between items-center">
                                <div>
                                    <h3 className="font-bold text-foreground text-base"> Knowledge Graph Visualizer</h3>
                                    <p className="text-xs text-muted-foreground">Explore relationship maps between core concepts.</p>
                                </div>
                                <Link href="/courses" className="text-xs font-semibold text-primary hover:opacity-80 bg-secondary px-3 py-1.5 rounded-xl transition">
                                    View Graph &rarr;
                                </Link>
                            </div>
                            <div className="h-32 bg-secondary/50 rounded-xl border border-dashed border-border flex items-center justify-center text-xs text-muted-foreground">
                                Interactive graph nodes preview placeholder
                            </div>
                        </div>

                    </div>

                    {/* Right Column: User Info & Session Controls */}
                    <div className="space-y-6">

                        {/* User Profile Card */}
                        <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4">
                            <h3 className="font-bold text-foreground text-base border-b border-border pb-3">User Profile</h3>
                            <div className="bg-secondary/50 p-4 rounded-xl border border-border">
                                <UserInfo />
                            </div>
                        </div>

                        {/* Session Management Card */}
                        <div className="bg-card rounded-2xl border border-border p-6 shadow-xs space-y-4 flex flex-col justify-between">
                            <div>
                                <h3 className="font-bold text-foreground text-base mb-1">Session Control</h3>
                                <p className="text-xs text-muted-foreground">Securely manage your active login session.</p>
                            </div>
                            <div className="pt-2">
                                <LogoutButton />
                            </div>
                        </div>

                    </div>

                </div>
            </main>
        </RequireAuth>
    );
}