import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { ThemeProvider } from "@/components/theme-provider";
import { AuthProvider } from "@/lib/auth-context";
import { AppQueryProvider } from "@/lib/query-provider";
import { Navbar } from "@/components/Navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "OpenLearn AI",
  description: "AI-powered learning platform",
  icons: {
    icon: "/logo.png",
  },
};

type LayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: LayoutProps) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 transition-colors">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={false}
          disableTransitionOnChange
        >
          <AppQueryProvider>
            <AuthProvider>
              {/* الـ Navbar محطوط هنا بره أي حاجة عشان يفضل ثابت تماماً */}
              <Navbar />

              {/* محتوى الصفحات */}
              <div className="flex-grow flex flex-col">
                {children}
              </div>

              {/* الفوتر */}
              <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-500 dark:text-slate-400 mt-auto">
                <p>OpenLearn AI Adaptive Learning Platform</p>
              </footer>
            </AuthProvider>
          </AppQueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}