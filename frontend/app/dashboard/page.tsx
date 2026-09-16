"use client";

import { useState } from "react";
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
import { Sun, Moon, ArrowUpRight } from "lucide-react";

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
      <div className="min-h-screen bg-slate-50 text-slate-900 transition-colors duration-200 dark:bg-slate-950 dark:text-slate-100">
        {/* Navigation Bar */}
        <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/80 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/85">
          <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
            <div className="flex items-center gap-3">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-xs font-bold text-white shadow-sm">
                O
              </div>

              <span className="text-sm font-semibold tracking-tight">
                OpenLearn AI
              </span>

              <span className="text-slate-300 dark:text-slate-700">
                /
              </span>

              <span className="font-mono text-xs text-slate-500">
                v1.2.4
              </span>
            </div>

            <div className="flex items-center gap-3">
              {/* Current User */}
              {isMeLoading && (
                <span className="hidden text-xs text-slate-500 sm:block">
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

                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {me.roles.length > 0
                      ? me.roles.join(", ")
                      : "No role"}
                  </p>
                </div>
              )}

              {/* Theme Toggle */}
              <Button
                variant="outline"
                size="icon"
                onClick={() =>
                  setIsDarkMode((previous) => !previous)
                }
                className="h-9 w-9 rounded-full border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900"
                aria-label="Toggle theme"
              >
                {isDarkMode ? (
                  <Sun className="h-4 w-4 text-amber-400 transition-transform hover:rotate-45" />
                ) : (
                  <Moon className="h-4 w-4 text-slate-600 transition-transform hover:-rotate-12" />
                )}
              </Button>

              {/* Dashboard */}
              <Button
                size="sm"
                className="h-9 bg-indigo-600 text-xs font-medium text-white shadow-sm hover:bg-indigo-700"
              >
                Dashboard
              </Button>

              {/* Logout */}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="h-9 border-slate-200 text-xs font-medium dark:border-slate-800"
              >
                {isLoggingOut
                  ? "Logging out..."
                  : "Logout"}
              </Button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="mx-auto max-w-5xl space-y-8 px-6 py-10">
          {/* Page Heading */}
          <div className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs dark:border-slate-800 dark:bg-slate-900 md:flex-row md:items-center">
            <div className="space-y-1">
              <div className="mb-1 flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-600 dark:border-emerald-900/50 dark:bg-emerald-950/50 dark:text-emerald-400">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
                  All Systems Normal
                </span>
              </div>

              <h1 className="text-2xl font-bold tracking-tight">
                Workspace & Components
              </h1>

              <p className="text-sm text-slate-500 dark:text-slate-400">
                Manage your active learning workflows and test
                interface tokens in real-time.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="border-slate-200 text-xs dark:border-slate-800"
              >
                Export Data
              </Button>
            </div>
          </div>

          {/* Grid */}
          <div className="grid gap-6 md:grid-cols-12">
            {/* Quick Launch */}
            <Card className="rounded-xl border-slate-200/80 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900 md:col-span-7">
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold">
                  Quick Launch
                </CardTitle>

                <CardDescription className="text-xs text-slate-500 dark:text-slate-400">
                  Instantly bootstrap a new learning container or
                  course session.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="space-y-1.5">
                  <label
                    htmlFor="course-name"
                    className="text-xs font-medium text-slate-600 dark:text-slate-400"
                  >
                    Course / Module Name
                  </label>

                  <Input
                    id="course-name"
                    placeholder="e.g. Advanced TypeScript & Next.js"
                    className="h-10 border-slate-200 bg-slate-50/50 text-sm dark:border-slate-800 dark:bg-slate-950/50"
                  />
                </div>

                <div className="flex items-center gap-2.5 pt-1">
                  <Button
                    size="sm"
                    className="bg-indigo-600 text-xs font-medium text-white hover:bg-indigo-700"
                  >
                    Start Session
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    className="gap-1 text-xs text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                  >
                    Documentation
                    <ArrowUpRight className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Environment */}
            <Card className="rounded-xl border-slate-200/80 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900 md:col-span-5">
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold">
                  Environment
                </CardTitle>

                <CardDescription className="text-xs text-slate-500 dark:text-slate-400">
                  Runtime metrics and active packages.
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div className="space-y-3 text-xs">
                  <div className="flex items-center justify-between border-b border-slate-100 py-1.5 dark:border-slate-800/60">
                    <span className="text-slate-500">
                      Framework
                    </span>

                    <span className="font-mono font-medium">
                      Next.js 16
                    </span>
                  </div>

                  <div className="flex items-center justify-between border-b border-slate-100 py-1.5 dark:border-slate-800/60">
                    <span className="text-slate-500">
                      UI Library
                    </span>

                    <span className="font-mono font-medium">
                      Shadcn / Tailwind
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5">
                    <span className="text-slate-500">
                      Response Time
                    </span>

                    <span className="font-mono font-medium text-emerald-600 dark:text-emerald-400">
                      18ms
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Design System */}
            <Card className="rounded-xl border-slate-200/80 bg-white shadow-xs dark:border-slate-800 dark:bg-slate-900 md:col-span-12">
              <CardHeader className="pb-4">
                <CardTitle className="text-base font-semibold">
                  Design System Tokens
                </CardTitle>

                <CardDescription className="text-xs text-slate-500 dark:text-slate-400">
                  Standardized badges and UI component states.
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div className="flex flex-wrap items-center gap-3">
                  <Badge className="bg-indigo-600 font-normal text-white">
                    Primary Badge
                  </Badge>

                  <Badge
                    variant="secondary"
                    className="font-normal"
                  >
                    Secondary
                  </Badge>

                  <Badge
                    variant="outline"
                    className="border-slate-200 font-normal dark:border-slate-800"
                  >
                    Outline
                  </Badge>

                  <div className="mx-1 h-4 w-px bg-slate-200 dark:bg-slate-800" />

                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 border-slate-200 text-xs dark:border-slate-800"
                  >
                    Secondary Action
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 text-xs text-slate-600 dark:text-slate-400"
                  >
                    Ghost Button
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}