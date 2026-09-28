import { LoginForm } from "@/components/auth/LoginForm";
import { ThemeToggle } from "@/components/theme-toggle";

export default function LoginPage() {
    return (
        <main className="relative min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-4">
            <div className="absolute right-6 top-6">
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
                <LoginForm />
            </div>
        </main>
    );
}