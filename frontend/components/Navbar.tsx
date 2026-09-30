"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Menu, X } from "lucide-react";

import { useAuth } from "@/lib/auth-context";
import { useUserName } from "@/components/UserName";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
    { href: "/", label: "Home" },
    { href: "/courses", label: "My Materials" },
    { href: "/dashboard", label: "Dashboard" },
    { href: "/profile", label: "Profile & Settings" },
];

export function Navbar() {
    const { isAuthenticated, isLoading: authLoading } = useAuth();
    const { name: userName, initial: userInitial, isLoading: userLoading } =
        useUserName();
    const [menuOpen, setMenuOpen] = useState(false);

    const isLoading = authLoading || userLoading;

    return (
        <header className="bg-card border-b border-border sticky top-0 z-50 transition-colors w-full">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between w-full">
                {/* Logo & Brand */}
                <Link
                    href="/"
                    className="flex items-center gap-3 cursor-pointer"
                >
                    <div className="relative w-10 h-10 overflow-hidden rounded-xl shadow-sm flex items-center justify-center bg-primary/10">
                        <Image
                            src="/logo.png"
                            alt="OpenLearn AI Logo"
                            width={40}
                            height={40}
                            className="object-cover w-full h-full"
                        />
                    </div>
                    <div>
                        <span className="font-bold text-xl text-foreground">
                            OpenLearn AI
                        </span>
                        <span className="block text-xs text-muted-foreground">
                            Adaptive Learning Platform
                        </span>
                    </div>
                </Link>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-muted-foreground">
                    {NAV_LINKS.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className="hover:text-primary transition"
                        >
                            {link.label}
                        </Link>
                    ))}
                </nav>

                {/* User Menu & Theme Toggle (desktop) */}
                <div className="hidden md:flex items-center gap-3">
                    <div className="border-s ps-3 border-border">
                        <ThemeToggle />
                    </div>

                    {!isLoading &&
                        (isAuthenticated ? (
                            <Link
                                href="/profile"
                                className="flex items-center gap-2 border-s ps-3 border-border cursor-pointer"
                            >
                                <div className="w-9 h-9 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">
                                    {userInitial}
                                </div>
                                <span className="text-sm font-semibold text-foreground max-w-[120px] truncate">
                                    {userName}
                                </span>
                            </Link>
                        ) : (
                            <Button
                                size="sm"
                                render={<Link href="/login" />}
                            >
                                Sign In
                            </Button>
                        ))}
                </div>

                {/* Mobile: Theme Toggle + Menu Button */}
                <div className="flex md:hidden items-center gap-2">
                    <ThemeToggle />
                    <button
                        type="button"
                        onClick={() => setMenuOpen((v) => !v)}
                        className="p-2 rounded-lg border border-border bg-background text-foreground hover:bg-muted transition flex items-center justify-center w-9 h-9"
                        aria-label={
                            menuOpen ? "Close menu" : "Open menu"
                        }
                        aria-expanded={menuOpen}
                    >
                        {menuOpen ? (
                            <X className="h-5 w-5" />
                        ) : (
                            <Menu className="h-5 w-5" />
                        )}
                    </button>
                </div>
            </div>

            {/* Mobile Navigation Panel */}
            {menuOpen && (
                <nav className="md:hidden border-t border-border bg-card">
                    <div className="max-w-7xl mx-auto px-4 py-4 space-y-2">
                        {NAV_LINKS.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="block py-2 text-sm font-medium text-foreground hover:text-primary transition"
                                onClick={() => setMenuOpen(false)}
                            >
                                {link.label}
                            </Link>
                        ))}

                        {!isLoading && (
                            <div className="pt-2 border-t border-border">
                                {isAuthenticated ? (
                                    <Link
                                        href="/profile"
                                        className="flex items-center gap-2 py-2 cursor-pointer"
                                        onClick={() => setMenuOpen(false)}
                                    >
                                        <div className="w-9 h-9 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">
                                            {userInitial}
                                        </div>
                                        <span className="text-sm font-semibold text-foreground max-w-[180px] truncate">
                                            {userName}
                                        </span>
                                    </Link>
                                ) : (
                                    <Button
                                        size="sm"
                                        className="w-full"
                                        render={<Link href="/login" />}
                                        onClick={() => setMenuOpen(false)}
                                    >
                                        Sign In
                                    </Button>
                                )}
                            </div>
                        )}
                    </div>
                </nav>
            )}
        </header>
    );
}
