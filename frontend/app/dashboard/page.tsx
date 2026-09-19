"use client";

import { useState } from "react";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  BrainCircuit,
  Clock3,
  LayoutDashboard,
  LogOut,
  Moon,
  Settings,
  Sparkles,
  Sun,
  Target,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { logout } from "@/lib/auth";
import { useMe } from "@/src/features/auth/api/useMe";

function DashboardContent() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const {
    data: me,
    isLoading: isMeLoading,
    isError: isMeError,
  } = useMe();

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
      setIsLoggingOut(false);
    }
  };

  return (
    <div className={isDarkMode ? "dark" : ""}>
      <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
        {/* =====================================================
            SIDEBAR
        ====================================================== */}
        <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-border bg-sidebar lg:flex lg:flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center border-b border-sidebar-border px-6">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sidebar-primary font-bold text-sidebar-primary-foreground shadow-sm">
                O
              </div>

              <div>
                <p className="text-sm font-bold tracking-tight">
                  OpenLearn AI
                </p>
                <p className="text-xs text-muted-foreground">
                  Learning Platform
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            <p className="mb-3 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Workspace
            </p>

            <Button
              variant="secondary"
              className="w-full justify-start gap-3"
            >
              <LayoutDashboard className="h-4 w-4" />
              Dashboard
            </Button>

            <Button
              variant="ghost"
              className="w-full justify-start gap-3"
            >
              <BookOpen className="h-4 w-4" />
              My Courses
            </Button>

            <Button
              variant="ghost"
              className="w-full justify-start gap-3"
            >
              <BrainCircuit className="h-4 w-4" />
              AI Assistant
            </Button>

            <Button
              variant="ghost"
              className="w-full justify-start gap-3"
            >
              <Activity className="h-4 w-4" />
              Progress
            </Button>

            <div className="my-5 border-t border-sidebar-border" />

            <p className="mb-3 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Account
            </p>

            <Button
              variant="ghost"
              className="w-full justify-start gap-3"
            >
              <Settings className="h-4 w-4" />
              Settings
            </Button>
          </nav>

          {/* AI Help */}
          <div className="border-t border-sidebar-border p-4">
            <div className="rounded-xl border border-sidebar-border bg-sidebar-accent p-4">
              <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Sparkles className="h-4 w-4" />
              </div>

              <p className="text-sm font-semibold">
                Need help?
              </p>

              <p className="mt-1 text-xs leading-5 text-muted-foreground">
                Ask the AI assistant about your courses and concepts.
              </p>

              <Button size="sm" className="mt-3 w-full gap-2">
                <Sparkles className="h-3.5 w-3.5" />
                Ask AI
              </Button>
            </div>
          </div>
        </aside>

        {/* =====================================================
            MAIN AREA
        ====================================================== */}
        <div className="min-h-screen lg:pl-64">
          {/* Header */}
          <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-border bg-background/90 px-4 backdrop-blur-md sm:px-6 lg:px-8">
            <div>
              <p className="text-xs text-muted-foreground">
                OpenLearn AI
              </p>

              <p className="text-sm font-medium">
                Learning Dashboard
              </p>
            </div>

            <div className="flex items-center gap-3">
              {/* Profile state */}
              {isMeLoading && (
                <span className="hidden text-xs text-muted-foreground sm:block">
                  Loading profile...
                </span>
              )}

              {isMeError && (
                <span className="hidden text-xs text-destructive sm:block">
                  Failed to load profile
                </span>
              )}

              {me && (
                <div className="hidden text-right sm:block">
                  <p className="text-sm font-medium">
                    {me.email}
                  </p>

                  <p className="text-xs text-muted-foreground">
                    {me.roles.length > 0
                      ? me.roles.join(", ")
                      : "Student"}
                  </p>
                </div>
              )}

              {/* Avatar */}
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                {me?.email?.slice(0, 2).toUpperCase() ?? "IM"}
              </div>

              {/* Theme */}
              <Button
                variant="outline"
                size="icon"
                onClick={() =>
                  setIsDarkMode((previous) => !previous)
                }
                className="h-9 w-9 rounded-full"
                aria-label="Toggle theme"
              >
                {isDarkMode ? (
                  <Sun className="h-4 w-4" />
                ) : (
                  <Moon className="h-4 w-4" />
                )}
              </Button>

              {/* Logout */}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="gap-2"
              >
                <LogOut className="h-3.5 w-3.5" />

                <span className="hidden sm:inline">
                  {isLoggingOut
                    ? "Logging out..."
                    : "Logout"}
                </span>
              </Button>
            </div>
          </header>

          {/* =====================================================
              CONTENT
          ====================================================== */}
          <main className="bg-background p-4 sm:p-6 lg:p-8">
            <div className="mx-auto max-w-7xl space-y-6">

              {/* Hero */}
              <section className="relative overflow-hidden rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8">
                <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/10 blur-3xl" />

                <div className="relative z-10 max-w-3xl">
                  <Badge className="mb-4 gap-1.5">
                    <Sparkles className="h-3 w-3" />
                    OpenLearn AI
                  </Badge>

                  <h1 className="text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
                    Keep learning.
                    <br />
                    <span className="text-primary">
                      Let AI guide you.
                    </span>
                  </h1>

                  <p className="mt-4 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">
                    Continue your courses, track your progress,
                    and use AI to understand difficult concepts
                    faster.
                  </p>

                  <div className="mt-6 flex flex-wrap gap-3">
                    <Button className="gap-2">
                      <BookOpen className="h-4 w-4" />
                      Continue Learning
                    </Button>

                    <Button
                      variant="outline"
                      className="gap-2"
                    >
                      Explore Courses
                      <ArrowUpRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </section>

              {/* Stats */}
              <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard
                  icon={<BookOpen className="h-4 w-4" />}
                  label="Active Courses"
                  value="4"
                  description="Currently learning"
                />

                <StatCard
                  icon={<Target className="h-4 w-4" />}
                  label="Overall Progress"
                  value="68%"
                  description="Across your courses"
                />

                <StatCard
                  icon={<Clock3 className="h-4 w-4" />}
                  label="Learning Hours"
                  value="24h"
                  description="This month"
                />

                <StatCard
                  icon={<Activity className="h-4 w-4" />}
                  label="Completed"
                  value="12"
                  description="Lessons completed"
                />
              </section>

              {/* Continue + Goal */}
              <section className="grid gap-6 lg:grid-cols-3">

                {/* Continue Learning */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <CardTitle>
                          Continue Learning
                        </CardTitle>

                        <CardDescription>
                          Pick up where you left off.
                        </CardDescription>
                      </div>

                      <Badge variant="secondary">
                        72% Complete
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent>
                    <div className="rounded-xl border border-border bg-muted/30 p-5">
                      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <Badge variant="outline">
                            Machine Learning
                          </Badge>

                          <h3 className="mt-3 text-xl font-semibold">
                            Machine Learning Fundamentals
                          </h3>

                          <p className="mt-1 text-sm text-muted-foreground">
                            Chapter 7 · Neural Networks
                          </p>
                        </div>

                        <Button className="gap-2">
                          Continue
                          <ArrowUpRight className="h-4 w-4" />
                        </Button>
                      </div>

                      <div className="mt-5">
                        <div className="mb-2 flex justify-between text-xs">
                          <span className="text-muted-foreground">
                            Course progress
                          </span>

                          <span className="font-medium">
                            72%
                          </span>
                        </div>

                        <div className="h-2 overflow-hidden rounded-full bg-muted">
                          <div
                            className="h-full rounded-full bg-primary"
                            style={{ width: "72%" }}
                          />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Weekly Goal */}
                <Card>
                  <CardHeader>
                    <CardTitle>
                      Weekly Goal
                    </CardTitle>

                    <CardDescription>
                      Your learning activity
                    </CardDescription>
                  </CardHeader>

                  <CardContent>
                    <div className="flex items-center justify-center py-4">
                      <div className="relative flex h-36 w-36 items-center justify-center rounded-full border-8 border-primary/15">
                        <div className="absolute inset-0 rounded-full border-8 border-transparent border-t-primary border-r-primary rotate-[-25deg]" />

                        <div className="text-center">
                          <p className="text-3xl font-bold">
                            76%
                          </p>

                          <p className="text-xs text-muted-foreground">
                            completed
                          </p>
                        </div>
                      </div>
                    </div>

                    <p className="text-center text-sm text-muted-foreground">
                      3.8 / 5 hours this week
                    </p>
                  </CardContent>
                </Card>
              </section>

              {/* AI Assistant */}
              <section>
                <Card className="overflow-hidden border-primary/20 bg-card">
                  <CardContent className="p-6 sm:p-8">
                    <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
                      <div>
                        <Badge className="mb-3 gap-1.5">
                          <Sparkles className="h-3 w-3" />
                          AI Learning Assistant
                        </Badge>

                        <h2 className="text-2xl font-bold">
                          Stuck on something?
                        </h2>

                        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
                          Ask questions about your current course,
                          get explanations, examples, or help
                          understanding difficult concepts.
                        </p>

                        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
                          <Input
                            placeholder="Ask something about Machine Learning..."
                            className="bg-background sm:max-w-xl"
                          />

                          <Button className="gap-2">
                            <Sparkles className="h-4 w-4" />
                            Ask AI
                          </Button>
                        </div>
                      </div>

                      <div className="hidden h-24 w-24 items-center justify-center rounded-2xl bg-primary/10 text-primary lg:flex">
                        <BrainCircuit className="h-10 w-10" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </section>

              {/* Recommended */}
              <section>
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold">
                      Recommended for You
                    </h2>

                    <p className="text-sm text-muted-foreground">
                      Courses based on your learning journey.
                    </p>
                  </div>

                  <Button
                    variant="ghost"
                    className="hidden sm:flex"
                  >
                    View all
                  </Button>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <CourseCard
                    category="Artificial Intelligence"
                    title="Deep Learning with PyTorch"
                    description="Build neural networks and practical AI models."
                    progress="32%"
                  />

                  <CourseCard
                    category="Data Science"
                    title="Data Analysis with Python"
                    description="Learn data processing, visualization, and analysis."
                    progress="18%"
                  />

                  <CourseCard
                    category="AI Engineering"
                    title="Building AI Applications"
                    description="Turn AI models into production-ready applications."
                    progress="0%"
                  />
                </div>
              </section>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   STAT CARD
========================================================= */

function StatCard({
  icon,
  label,
  value,
  description,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  description: string;
}) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">
              {label}
            </p>

            <p className="mt-2 text-3xl font-bold tracking-tight">
              {value}
            </p>

            <p className="mt-1 text-xs text-muted-foreground">
              {description}
            </p>
          </div>

          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/* =========================================================
   COURSE CARD
========================================================= */

function CourseCard({
  category,
  title,
  description,
  progress,
}: {
  category: string;
  title: string;
  description: string;
  progress: string;
}) {
  return (
    <Card className="group transition-all hover:-translate-y-1 hover:shadow-lg">
      <CardHeader>
        <Badge
          variant="secondary"
          className="w-fit"
        >
          {category}
        </Badge>

        <CardTitle className="mt-2">
          {title}
        </CardTitle>

        <CardDescription>
          {description}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="mb-2 flex justify-between text-xs">
          <span className="text-muted-foreground">
            Progress
          </span>

          <span className="font-medium">
            {progress}
          </span>
        </div>

        <div className="h-2 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: progress }}
          />
        </div>

        <Button
          variant="outline"
          className="mt-4 w-full gap-2"
        >
          View Course
          <ArrowUpRight className="h-3.5 w-3.5" />
        </Button>
      </CardContent>
    </Card>
  );
}

/* =========================================================
   PAGE
========================================================= */

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}