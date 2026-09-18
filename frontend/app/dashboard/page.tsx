"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { UserInfo } from "@/components/auth/UserInfo";
import { LogoutButton } from "@/components/auth/LogoutButton";

export default function DashboardPage() {
    const { isAuthenticated, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.replace("/login");
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading || !isAuthenticated) {
        return (
            <main className="min-h-screen flex items-center justify-center">
                <p className="text-muted-foreground">Loading...</p>
            </main>
        );
    }

    return (
        <main className="min-h-screen p-8">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="mt-2 text-muted-foreground">
                This page is protected. You can only see it if you are logged in.
            </p>

            <div className="mt-6 max-w-sm rounded-lg border p-4">
                <UserInfo />
            </div>

            <div className="mt-4">
                <LogoutButton />
            </div>
        </main>
    );
}