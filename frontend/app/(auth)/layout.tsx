/**
 * Shared minimal layout for the `(auth)` route group (D1).
 *
 * `/login` and `/register` share this centered, full-screen shell so
 * they don't each re-implement the dark background and centering
 * wrapper. No Navbar, no application navigation, no authenticated UI —
 * those belong to `app/(app)/layout.tsx`.
 */
export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <main className="relative min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-4">
            {children}
        </main>
    );
}
