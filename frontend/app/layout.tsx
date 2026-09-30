import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Sans_Arabic } from "next/font/google";
import "./globals.css";

import { ThemeProvider } from "@/components/theme-provider";
import { AuthProvider } from "@/lib/auth-context";
import { AppQueryProvider } from "@/lib/query-provider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// D10 RTL/font rail: Arabic-capable font so the layout can render
// Arabic text without glyphs falling back to a system default. LTR
// and English remain the baseline; this only activates when Arabic
// content or `dir="rtl"` is present.
const notoSansArabic = Noto_Sans_Arabic({
  variable: "--font-arabic",
  subsets: ["arabic"],
  display: "swap",
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
      dir="ltr"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} ${notoSansArabic.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground transition-colors">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={false}
          disableTransitionOnChange
        >
          <AppQueryProvider>
            <AuthProvider>
              {/*
                Global providers only. The Navbar, footer, and
                AuthGuard now live in app/(app)/layout.tsx so that
                public routes (/login, /register) render without the
                authenticated application shell.
              */}
              <div className="flex-grow flex flex-col">
                {children}
              </div>
            </AuthProvider>
          </AppQueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}