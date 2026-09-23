"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useMe } from "@/features/auth/api/useMe";

export default function Home() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { data: user, isLoading: userLoading } = useMe() as { data: any; isLoading: boolean };

  const isLoading = authLoading || userLoading;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-indigo-900 to-indigo-700 text-white p-6 sm:p-8 rounded-2xl shadow-sm space-y-4">
        <div className="inline-block bg-white/10 text-white px-3 py-1 rounded-lg text-xs font-medium backdrop-blur-xs">
          Welcome to OpenLearn AI
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
          Your Personal AI-Powered Learning Hub 
        </h1>
        <p className="text-indigo-100 text-sm max-w-2xl">
          Upload your course materials, interact with intelligent RAG assistants, explore dynamic knowledge graphs, and master your subjects with custom generated quizzes and flashcards.
        </p>
        <div className="pt-2">
          {!isLoading && (
            isAuthenticated ? (
              <Link href="/dashboard" className="inline-block bg-white text-indigo-900 hover:bg-indigo-50 text-sm font-semibold px-5 py-2.5 rounded-xl transition shadow-sm">
                Go to Dashboard
              </Link>
            ) : (
              <Link href="/login" className="inline-block bg-white text-indigo-900 hover:bg-indigo-50 text-sm font-semibold px-5 py-2.5 rounded-xl transition shadow-sm">
                Get Started - Sign In
              </Link>
            )
          )}
        </div>
      </div>

      {/* Features & Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Quick Course / Material Actions */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4 flex flex-col justify-between transition-colors">
          <div className="space-y-2">
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">Materials & RAG</span>
            <h3 className="font-bold text-slate-900 dark:text-white text-lg">Start Learning a New Subject</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Enter a course title or upload study documents to generate an adaptive path.
            </p>
          </div>
          <div className="space-y-4 pt-2">
            <input 
              type="text" 
              placeholder="e.g., Advanced Software Architecture, Machine Learning..." 
              className="w-full border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 bg-slate-50/50 dark:bg-slate-800 text-slate-900 dark:text-white"
            />
            <div className="flex gap-3">
              <Link href="/courses" className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-2 rounded-xl transition text-center flex-1">
                Create Course
              </Link>
              <Link href="/courses" className="border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm font-medium px-4 py-2 rounded-xl transition text-center flex-1">
                View My Materials
              </Link>
            </div>
          </div>
        </div>

        {/* AI Tools & Capabilities */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4 flex flex-col justify-between transition-colors">
          <div className="space-y-2">
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">Platform Features</span>
            <h3 className="font-bold text-slate-900 dark:text-white text-lg">Interactive AI Tools</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Leverage cutting-edge models to accelerate your comprehension.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3 pt-2">
            <Link href="/dashboard" className="p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 hover:border-indigo-200 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/30 transition group block">
              <div className="font-semibold text-sm text-slate-800 dark:text-slate-200 group-hover:text-indigo-600"> RAG Chat</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Ask questions on your docs</div>
            </Link>
            <Link href="/dashboard" className="p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 hover:border-indigo-200 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/30 transition group block">
              <div className="font-semibold text-sm text-slate-800 dark:text-slate-200 group-hover:text-indigo-600"> Knowledge Graph</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Visualize concepts map</div>
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}

/*
cd frontend
npm run dev  
Local: http://localhost:3000
document.documentElement.classList.add("dark")
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000  (backend)
*/