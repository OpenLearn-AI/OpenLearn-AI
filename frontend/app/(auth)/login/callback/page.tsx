"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { createUserManager } from "@/lib/oidc";

export default function LoginCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const userManager = createUserManager();

        await userManager.signinRedirectCallback();

        router.replace("/dashboard");
      } catch (error) {
        console.error("OIDC callback failed:", error);
        router.replace("/login?error=callback");
      }
    };

    handleCallback();
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center">
      <p>Signing you in...</p>
    </main>
  );
}