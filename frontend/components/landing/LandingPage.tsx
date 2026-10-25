import Image from "next/image";

import { OidcEntryButton } from "@/components/auth/OidcEntryButton";
import { BrandMark } from "@/components/brand/BrandMark";
import { Reveal } from "@/components/landing/Reveal";

/**
 * The public landing page (visual-direction redesign).
 *
 * Deliberately short. It answers four questions and nothing else:
 * what OpenLearn AI is, why it is useful, what the product actually
 * looks like today, and how to enter. There are no feature grids,
 * no testimonials, no invented metrics, and no long marketing copy;
 * the single product screenshot does that storytelling.
 *
 * Content rules (continuing the Batch 4.1 honesty decisions):
 *   - Only verified capabilities are presented as available; the
 *     development/planned items are listed separately with their
 *     honest status labels, in one compact place.
 *   - The screenshot is captured from the real rendered
 *     `/courses` page (how it was captured and refreshed is
 *     recorded next to the asset, `frontend/public/CAPTURE.md`,
 *     and in the file's own component comment below).
 *   - No fabricated metrics, testimonials, logos, ratings, pricing,
 *     or policy claims. Nothing invented.
 *
 * Auth-CTA placement: "Log in" and "Create account" exist ONLY in
 * the navbar (same rule the corrective follow-up fixed). The hero
 * and the status panel carry no authentication buttons. The former
 * footer ("OpenLearn AI · Adaptive Learning Platform") was removed
 * entirely in Batch 4.2 correction C — the owner does not want a
 * persistent branding bar anywhere in the application — and it was
 * not replaced with another one.
 *
 * Visual rules: the fixed-dark public palette only. Background depth
 * comes from the documented dark-ambient token mixes (a restrained
 * brass radial at the very top, a warm light wash at the bottom), a
 * raised navbar "notch", and one elevated panel for the status list.
 * Motion is limited to a one-shot hero entrance and a one-time
 * scroll reveal, both suppressed under reduced motion.
 */

const STATUS_TODAY =
    "Today: your courses, guided profile setup, and secure sign in.";

const STATUS_IN_DEVELOPMENT =
    "In development: course material upload with automatic processing.";

const STATUS_PLANNED =
    "Planned: AI assisted search and chat over your course materials; knowledge graphs, quizzes, and flashcards come later.";

export function LandingPage() {
    return (
        <div className="dark relative flex min-h-svh flex-col bg-background text-foreground">
            {/* Ambient depth (dark ladder only): a restrained brass
                radial at the very top of the page and a warm wash in
                the lower register. Decorative only. */}
            <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-x-0 top-0 h-[560px] bg-[radial-gradient(64%_58%_at_50%_0%,var(--ambient-brass-subtle),transparent_72%)]"
            />
            <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-x-0 bottom-0 h-[420px] bg-[radial-gradient(80%_60%_at_50%_100%,var(--ambient-paper),transparent_74%)]"
            />

            {/* ── Notch navbar ─────────────────────────────────────
                Notch-inspired top bar: an inset surface attached to
                the top edge of the page with rounded lower corners,
                so it reads as part of the viewport, not a generic
                full-width SaaS header. The interpretation is kept
                restrained: one clean island, no morphing, no glow.
                The reference design ("Notch", notch.page) is used as
                a composition reference for the shape and placement
                only; branding is OpenLearn AI's own. */}
            <header className="sticky top-0 z-40 w-full">
                <div className="mx-auto w-full max-w-5xl px-2 sm:px-4">
                    <div className="flex items-center justify-between gap-3 rounded-b-3xl border-x border-b border-border bg-card/95 px-3 py-2.5 shadow-xs sm:px-5">
                        <BrandMark />
                        <div className="flex items-center gap-1.5">
                            <OidcEntryButton mode="login" variant="ghost">
                                Log in
                            </OidcEntryButton>
                            <OidcEntryButton mode="register">
                                Create account
                            </OidcEntryButton>
                        </div>
                    </div>
                </div>
            </header>

            <main className="relative w-full flex-1">
                <div className="mx-auto w-full max-w-6xl px-4 sm:px-6">
                    {/* ── Hero + product preview ─────────────────────── */}
                    <section
                        aria-labelledby="landing-hero-heading"
                        className="pt-14 sm:pt-20"
                    >
                        <div className="max-w-2xl">
                            <p className="ol-enter text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                                Adaptive learning platform
                            </p>
                            <h1
                                id="landing-hero-heading"
                                className="ol-enter ol-enter-delay-1 mt-4 text-4xl font-bold tracking-tight text-balance sm:text-5xl"
                            >
                                Bring your learning together.
                            </h1>
                            <p className="ol-enter ol-enter-delay-2 mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
                                OpenLearn AI keeps your courses in one
                                organized place and sets up a profile that
                                fits how you study. Sign in once with secure
                                single sign on.
                            </p>
                        </div>

                        <Reveal className="ol-enter-delay-3 mt-12 sm:mt-16">
                            <figure className="mx-auto max-w-5xl">
                                <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-lg">
                                    <Image
                                        src="/courses-preview.png"
                                        alt="The OpenLearn AI courses workspace as it renders today, with the current course list"
                                        width={2880}
                                        height={1800}
                                        sizes="(max-width: 640px) 100vw, 1024px"
                                        className="h-auto w-full"
                                    />
                                </div>
                                <figcaption className="mt-3 text-center text-xs text-muted-foreground/80">
                                    The courses workspace, exactly as the app
                                    renders it today.
                                </figcaption>
                            </figure>
                        </Reveal>
                    </section>

                    {/* ── Honest status list ──────────────────────────
                        The whole product status, in three lines. The
                        labels (Today / In development / Planned) are the
                        Batch 4.1 honesty vocabulary, condensed. */}
                    <section
                        aria-labelledby="landing-status-heading"
                        className="pb-20 pt-14 sm:pt-16"
                    >
                        <Reveal>
                            <div className="mx-auto max-w-3xl rounded-3xl border border-border bg-card p-6 shadow-xs sm:p-8">
                                <h2
                                    id="landing-status-heading"
                                    className="text-sm font-semibold uppercase tracking-wider text-muted-foreground"
                                >
                                    Where the product stands
                                </h2>
                                <ul className="mt-5 space-y-4">
                                    <li className="flex items-start gap-3 text-sm leading-relaxed sm:text-base">
                                        <span
                                            aria-hidden="true"
                                            className="mt-2 size-2 shrink-0 rounded-full bg-primary"
                                        />
                                        <span className="text-foreground">
                                            {STATUS_TODAY}
                                        </span>
                                    </li>
                                    <li className="flex items-start gap-3 text-sm leading-relaxed text-muted-foreground sm:text-base">
                                        <span
                                            aria-hidden="true"
                                            className="mt-2 size-2 shrink-0 rounded-full bg-muted-foreground/70"
                                        />
                                        <span>{STATUS_IN_DEVELOPMENT}</span>
                                    </li>
                                    <li className="flex items-start gap-3 text-sm leading-relaxed text-muted-foreground sm:text-base">
                                        <span
                                            aria-hidden="true"
                                            className="mt-2 size-2 shrink-0 rounded-full bg-muted-foreground/40"
                                        />
                                        <span>{STATUS_PLANNED}</span>
                                    </li>
                                </ul>
                            </div>
                        </Reveal>
                    </section>
                </div>
            </main>
        </div>
    );
}
