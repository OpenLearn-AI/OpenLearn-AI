import { BrandMark } from "@/components/brand/BrandMark";
import { ProductIdentityVisual } from "@/components/brand/ProductIdentityVisual";
import { OidcEntryButton } from "@/components/auth/OidcEntryButton";

/**
 * The public landing page (Batch 4.1; navbar + CTA placement corrected
 * by the follow-up).
 *
 * This component is deliberately free of auth/data hooks: the page
 * wrapper (`app/page.tsx`) owns the small auth-aware redirect, and this
 * composition renders identically for visitors, during auth
 * initialization, and for authenticated users in the moment before
 * their redirect to `/dashboard` completes. That separation keeps the
 * page public at runtime (no `useMe` call — the pre-4.1 landing's
 * unconditional `useMe` bounced signed-out visitors to `/login` via the
 * global 401 recovery) and makes the whole surface hermetically
 * storyable. The navbar's auth actions initiate the existing Keycloak
 * flows DIRECTLY through `OidcEntryButton` (whose adapter import is
 * click-time dynamic), so the page never initializes Keycloak at rest.
 *
 * Content rules (owner-approved messaging, Batch 4.1 brief §3):
 *   - Only verified capabilities are presented as available; every
 *     forward-looking item carries an explicit "In development" or
 *     "Planned" chip and is non-interactive.
 *   - No screenshots (Q1): the hero is paired with the original
 *     Product Identity Visual.
 *   - No fabricated metrics, testimonials, logos, ratings, pricing, or
 *     policy claims — none of those exist in the repository.
 *   - Light Steel only: semantic tokens, no gradients, no
 *     glassmorphism, logical CSS properties throughout (RTL-ready), and
 *     no decorative motion (reduced-motion safe by construction).
 *
 * Auth-CTA placement (corrective follow-up §B.2): "Log in" and "Create
 * account" appear ONLY in the sticky top bar (§B.1) — the hero and the
 * closing section carry no duplicate authentication buttons, and the
 * footer repeats none either. The sticky bar keeps the entry points one
 * glance away everywhere on the page.
 */

const CAPABILITIES = [
    {
        title: "Organized courses",
        body: "Create courses, keep them in one place, and edit them anytime. Your courses belong to your account.",
    },
    {
        title: "A profile that sets the basics",
        body: "Record your education, field of study, preferred language, and daily study time in a short guided setup.",
    },
    {
        title: "Your sessions, your theme",
        body: "Sign in securely through OpenLearn's single sign-on, and work in light or dark — whatever fits your study space.",
    },
] as const;

const STEPS = [
    {
        title: "Create an account",
        body: "Register through OpenLearn's secure sign-on — no separate password to manage here.",
    },
    {
        title: "Set up your profile",
        body: "A short guided setup records the basics: education, field of study, language, and study time.",
    },
    {
        title: "Add and organize your courses",
        body: "Bring your courses together in one place and keep them up to date.",
    },
] as const;

const FUTURE_ITEMS = [
    {
        label: "Material upload and automatic processing",
        status: "In development",
    },
    {
        label: "AI-assisted search, citations, and chat on your materials",
        status: "Planned",
    },
    {
        label: "Knowledge graphs, quizzes, and flashcards",
        status: "Planned",
    },
] as const;

export function LandingPage() {
    return (
        <div className="flex min-h-svh flex-col bg-background text-foreground">
            {/* ── 1. Sticky top bar ─────────────────────────────────── */}
            <header className="sticky top-0 z-40 border-b border-border bg-background">
                <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
                    <BrandMark />
                    <div className="flex items-center gap-2">
                        <OidcEntryButton
                            mode="login"
                            variant="ghost"
                        >
                            Log in
                        </OidcEntryButton>
                        <OidcEntryButton mode="register">
                            Create account
                        </OidcEntryButton>
                    </div>
                </div>
            </header>

            <main className="mx-auto w-full max-w-6xl flex-1 px-4 sm:px-6">
                {/* ── 2. Hero ────────────────────────────────────────── */}
                <section
                    aria-labelledby="landing-hero-heading"
                    className="grid items-center gap-10 py-12 sm:py-16 lg:grid-cols-2 lg:gap-14 lg:py-20"
                >
                    <div className="space-y-6">
                        <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                            OpenLearn AI — more organized, more interactive
                            learning
                        </p>
                        <h1
                            id="landing-hero-heading"
                            className="text-4xl font-bold tracking-tight text-balance sm:text-5xl"
                        >
                            Bring your learning together. Make it more
                            personal over time.
                        </h1>
                        <p className="max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
                            One organized home for your courses — for students
                            and instructors — with a learner profile that keeps
                            the basics in one place. OpenLearn AI is being
                            built to make learning more personal over time;
                            today it keeps your courses and study setup
                            organized.
                        </p>
                    </div>

                    {/* The original Product Identity Visual (Q1). The
                        composition is token-drawn SVG; it re-themes with
                        Light/Dark automatically and carries no text, so
                        RTL needs no mirroring. */}
                    <div className="mx-auto w-full max-w-[320px] sm:max-w-[400px] lg:max-w-[460px]">
                        <ProductIdentityVisual className="h-auto w-full" />
                    </div>
                </section>

                {/* ── 3. How it works ───────────────────────────────── */}
                <section
                    aria-labelledby="landing-how-heading"
                    className="border-t border-border py-12 sm:py-14"
                >
                    <div className="space-y-8">
                        <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                                How it works
                            </p>
                            <h2
                                id="landing-how-heading"
                                className="text-2xl font-bold tracking-tight sm:text-3xl"
                            >
                                Three steps to an organized start
                            </h2>
                        </div>
                        <ol className="grid gap-4 sm:grid-cols-3">
                            {STEPS.map((step, index) => (
                                <li
                                    key={step.title}
                                    className="rounded-2xl border border-border bg-card p-5 shadow-xs"
                                >
                                    <p
                                        aria-hidden="true"
                                        className="text-sm font-bold text-primary"
                                    >
                                        {index + 1}
                                    </p>
                                    <h3 className="pt-1 text-base font-semibold text-card-foreground">
                                        {step.title}
                                    </h3>
                                    <p className="pt-1 text-sm leading-relaxed text-muted-foreground">
                                        {step.body}
                                    </p>
                                </li>
                            ))}
                        </ol>
                    </div>
                </section>

                {/* ── 4. What you can do today ──────────────────────── */}
                <section
                    aria-labelledby="landing-today-heading"
                    className="border-t border-border py-12 sm:py-14"
                >
                    <div className="space-y-8">
                        <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                                What you can do today
                            </p>
                            <h2
                                id="landing-today-heading"
                                className="text-2xl font-bold tracking-tight sm:text-3xl"
                            >
                                Current capabilities, honestly stated
                            </h2>
                            <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground sm:text-base">
                                Everything below is part of the product right
                                now. Features that are still on the way are
                                listed separately, and clearly labeled.
                            </p>
                        </div>
                        <div className="grid gap-4 md:grid-cols-3">
                            {CAPABILITIES.map((capability) => (
                                <div
                                    key={capability.title}
                                    className="rounded-2xl border border-border bg-card p-5 shadow-xs"
                                >
                                    <h3 className="text-base font-semibold text-card-foreground">
                                        {capability.title}
                                    </h3>
                                    <p className="pt-1.5 text-sm leading-relaxed text-muted-foreground">
                                        {capability.body}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── 5. For students / for instructors ─────────────── */}
                <section
                    aria-labelledby="landing-audience-heading"
                    className="border-t border-border py-12 sm:py-14"
                >
                    <div className="space-y-8">
                        <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                                Who it serves
                            </p>
                            <h2
                                id="landing-audience-heading"
                                className="text-2xl font-bold tracking-tight sm:text-3xl"
                            >
                                Built for students and instructors
                            </h2>
                        </div>
                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="rounded-2xl border border-border bg-card p-6 shadow-xs">
                                <h3 className="text-lg font-semibold text-card-foreground">
                                    For students
                                </h3>
                                <p className="pt-2 text-sm leading-relaxed text-muted-foreground">
                                    Keep every course you&apos;re following in
                                    one place and set your study preferences —
                                    your language, and the time you actually
                                    have each day.
                                </p>
                            </div>
                            <div className="rounded-2xl border border-border bg-card p-6 shadow-xs">
                                <h3 className="text-lg font-semibold text-card-foreground">
                                    For instructors
                                </h3>
                                <p className="pt-2 text-sm leading-relaxed text-muted-foreground">
                                    Set up and organize the courses you teach,
                                    with a workspace that grows with your
                                    materials.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* ── 6. Where we're headed ─────────────────────────── */}
                <section
                    aria-labelledby="landing-future-heading"
                    className="border-t border-border py-12 sm:py-14"
                >
                    <div className="space-y-6 rounded-2xl border border-border bg-card p-6 shadow-xs sm:p-8">
                        <div className="space-y-2">
                            <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                                Where we&apos;re headed
                            </p>
                            <h2
                                id="landing-future-heading"
                                className="text-2xl font-bold tracking-tight"
                            >
                                What&apos;s next — clearly labeled
                            </h2>
                            <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground">
                                These capabilities are not part of the product
                                yet. We list them so the direction is
                                transparent, not to suggest they are available
                                today.
                            </p>
                        </div>
                        <ul className="space-y-2.5">
                            {FUTURE_ITEMS.map((item) => (
                                <li
                                    key={item.label}
                                    className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border bg-secondary/50 px-3.5 py-2.5"
                                >
                                    <span className="text-sm text-card-foreground">
                                        {item.label}
                                    </span>
                                    <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded-md font-semibold">
                                        {item.status}
                                    </span>
                                </li>
                            ))}
                        </ul>
                        <p className="border-t border-border pt-5 text-sm italic leading-relaxed text-muted-foreground">
                            Our long-term vision: &ldquo;Your learning journey
                            should remember you&rdquo; — a platform that grows
                            more personal the longer you use it. Personalization
                            at that level is not part of the product today.
                        </p>
                    </div>
                </section>

                {/* ── 7. Closing statement ──────────────────────────── */}
                <section
                    aria-labelledby="landing-cta-heading"
                    className="py-12 sm:py-14"
                >
                    <div className="flex flex-col items-start gap-1.5 rounded-2xl border border-border bg-card p-6 shadow-xs sm:p-8">
                        <h2
                            id="landing-cta-heading"
                            className="text-xl font-bold tracking-tight sm:text-2xl"
                        >
                            Start with your courses. Grow from there.
                        </h2>
                        <p className="max-w-2xl text-sm leading-relaxed text-muted-foreground">
                            Create an account, set up your profile, and bring
                            your learning together — the account and log-in
                            actions are in the bar above, wherever you are on
                            this page.
                        </p>
                    </div>
                </section>
            </main>

            {/* ── Footer ─────────────────────────────────────────────── */}
            <footer className="border-t border-border bg-background">
                <div className="mx-auto w-full max-w-6xl px-4 py-6 text-sm text-muted-foreground sm:px-6">
                    <p>OpenLearn AI — Adaptive Learning Platform</p>
                </div>
            </footer>
        </div>
    );
}
