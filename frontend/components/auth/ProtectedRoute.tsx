"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/lib/auth-store";
import { getCurrentUser } from "@/lib/auth";

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({
  children,
}: ProtectedRouteProps) {
  const router = useRouter();

  const status = useAuthStore((state) => state.status);
  const setAuthenticated = useAuthStore(
    (state) => state.setAuthenticated,
  );
  const setUnauthenticated = useAuthStore(
    (state) => state.setUnauthenticated,
  );

  useEffect(() => {
    let mounted = true;

    const restoreSession = async () => {
      try {
        const user = await getCurrentUser();

        if (!mounted) {
          return;
        }

        if (!user || user.expired) {
          setUnauthenticated();
          router.replace("/login");
          return;
        }

        setAuthenticated(user);
      } catch (error) {
        console.error("Session restoration failed:", error);

        if (!mounted) {
          return;
        }

        setUnauthenticated();
        router.replace("/login");
      }
    };

    restoreSession();

    return () => {
      mounted = false;
    };
  }, [
    router,
    setAuthenticated,
    setUnauthenticated,
  ]);

  if (status === "unknown") {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">
          Restoring session...
        </p>
      </main>
    );
  }

  if (status === "unauthenticated") {
    return null;
  }

  return <>{children}</>;
}