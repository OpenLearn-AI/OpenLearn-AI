"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

export function RequireAuth({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, isLoading, initialize } = useAuthStore();
    const router = useRouter();

    useEffect(() => {
        initialize();
    }, [initialize]);

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.replace("/login");
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <p className="text-muted-foreground">Checking your session...</p>
            </div>
        );
    }

    if (!isAuthenticated) {
        return null;
    }

    return <>{children}</>;
}