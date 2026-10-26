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
    // Batch 4.2 correction A9: the favicon referenced the removed
    // `/logo.png` (a 404 since the owner's asset cleanup); the
    // authoritative brand asset is the supplied `public/logo.svg`.
    icon: { url: "/logo.svg", type: "image/svg+xml" },
  },
};

type LayoutProps = {
  children: React.ReactNode;
};

/**
 * Pre-paint direction restoration (Batch 4.4).
 *
 * A stored RTL/LTR preference (set by the sidebar's direction
 * control — `lib/direction.ts`) is applied to `<html dir>` BEFORE
 * first paint, so a returning RTL user never sees an LTR flash.
 * This is the same mechanism next-themes uses for the theme class:
 * an inline script in the server-rendered markup, executed during
 * HTML parsing, with `suppressHydrationWarning` on `<html>` (already
 * present for the theme class) covering the attribute delta during
 * hydration. Deliberately tiny and dependency-free; the `try/catch`
 * keeps private-mode/unavailable storage harmless. Anything other
 * than an exact "rtl"/"ltr" value is ignored — the SSR default
 * ("ltr") stands.
 */
const DIRECTION_INIT_SCRIPT = `(function(){try{var d=localStorage.getItem("openlearn-direction");if(d==="rtl"||d==="ltr"){document.documentElement.dir=d;}}catch(e){}})();`;

export default function RootLayout({ children }: LayoutProps) {
  return (
    <html
      lang="en"
      dir="ltr"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} ${notoSansArabic.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground transition-colors">
        <script dangerouslySetInnerHTML={{ __html: DIRECTION_INIT_SCRIPT }} />
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
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