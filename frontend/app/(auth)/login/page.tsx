import { Suspense } from "react";
import { LoginForm } from "@/components/auth/LoginForm";

/**
 * Login entry (Batch 4.1 presentation refresh).
 *
 * The page owns the entry card and the pinned heading "Sign in to your
 * account" (the E2E login spec locates it by role + name); the brand
 * identity and theme toggle come from the shared `(auth)` layout.
 * `LoginForm` provides the OIDC button and its states — the button's
 * text ("Sign in with OpenLearn AI") and the redirect handler are
 * unchanged.
 */
export default function LoginPage() {
    return (
        <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-card-foreground shadow-xs">
            <div className="mb-6 space-y-1.5">
                <h2 className="text-2xl font-bold text-card-foreground">
                    Sign in to your account
                </h2>
                <p className="text-sm text-muted-foreground">
                    Welcome back — your courses are right where you left them.
                </p>
            </div>

            {/*
              Suspense boundary required by Next.js because LoginForm
              uses useSearchParams() to read the `redirectedFrom`
              query param carried over by AuthGuard.
            */}
            <Suspense fallback={null}>
                <LoginForm />
            </Suspense>
        </div>
    );
}
