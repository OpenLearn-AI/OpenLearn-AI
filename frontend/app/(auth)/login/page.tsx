import { Suspense } from "react";
import { LoginForm } from "@/components/auth/LoginForm";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export default function LoginPage() {
    return (
        <>
            <div className="absolute end-6 top-6">
                <ThemeToggle />
            </div>

            {/* Brand Header */}
            <div className="text-center mb-8">
                <h1 className="text-2xl sm:text-3xl font-bold tracking-wider text-white">OPENLEARN</h1>
            </div>

            <div className="w-full max-w-md bg-white text-slate-800 p-8 rounded-2xl shadow-xl border border-slate-200">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-slate-900">Sign in to your account</h2>
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
        </>
    );
}