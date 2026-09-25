"use client";

import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { useMe } from "@/features/auth/api/useMe";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export function Navbar() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { data: user, isLoading: userLoading } = useMe();

  const isLoading = authLoading || userLoading;
  const userName = user?.email || "My Profile";
  const userInitial = typeof userName === "string" ? userName.charAt(0).toUpperCase() : "U";

  return (
    <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50 transition-colors w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between w-full">
        
        {/* Logo & Brand */}
        <Link href="/" className="flex items-center gap-3 cursor-pointer">
          <div className="relative w-10 h-10 overflow-hidden rounded-xl shadow-sm flex items-center justify-center bg-indigo-50 dark:bg-indigo-950">
            <Image 
              src="/logo.png" 
              alt="OpenLearn AI Logo"
              width={40}
              height={40}
              className="object-cover w-full h-full"
            />
          </div>
          <div>
            <span className="font-bold text-xl text-slate-900 dark:text-white">OpenLearn AI</span>
            <span className="block text-xs text-slate-500 dark:text-slate-400">Adaptive Learning Platform</span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600 dark:text-slate-300">
          <Link href="/" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Home</Link>
          <Link href="/courses" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">My Materials</Link>
          <Link href="/dashboard" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">RAG Chat</Link>
          <Link href="/dashboard" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Knowledge Graph</Link>
          <Link href="/profile" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition">Profile & Settings</Link>
        </nav>

        {/* User Menu & Theme Toggle */}
        <div className="flex items-center gap-3">
          <div className="border-s ps-3 border-slate-200 dark:border-slate-800">
            <ThemeToggle />
          </div>

          {!isLoading && (
            <div>
              {isAuthenticated ? (
                <Link href="/profile" className="flex items-center gap-2 border-s ps-3 border-slate-200 dark:border-slate-800 cursor-pointer">
                  <div className="w-9 h-9 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 flex items-center justify-center font-bold text-sm">
                    {userInitial}
                  </div>
                  <span className="text-sm font-semibold hidden md:inline text-slate-800 dark:text-slate-200 max-w-[120px] truncate">
                    {userName}
                  </span>
                </Link>
              ) : (
                <Link href="/login" className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-2 rounded-xl font-medium transition">
                  Sign In
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}