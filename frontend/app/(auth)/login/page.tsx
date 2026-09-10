import { LoginForm } from "@/components/auth/LoginForm";
import { ThemeToggle } from "@/components/theme-toggle";

export default function LoginPage() {
    return (
        <main className="relative flex min-h-screen items-center justify-center bg-background px-4 py-8">
            <div className="absolute right-4 top-4">
                <ThemeToggle />
            </div>

            <LoginForm />
        </main>
    );
}