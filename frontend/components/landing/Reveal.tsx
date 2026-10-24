"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/**
 * Scroll-reveal wrapper for the fixed-dark public experience.
 *
 * A restrained, one-time reveal: when the element first enters the
 * viewport it rises a few pixels into place (translate only). Content
 * is NEVER hidden at any point:
 *   - Without JavaScript (no hydration, crawler, JS disabled) the
 *     element renders fully visible — the animation only exists
 *     when JS mounts.
 *   - With reduced-motion preferred, nothing is armed and content
 *     is immediately visible (the globals.css reduced-motion guard
 *     also collapses any residual transition to zero).
 *   - The reveal crosses a tiny threshold once and then disconnects
 *     the observer, so nothing loops or re-fires.
 *
 * Only transform changes — no opacity manipulation and no layout
 * shift, so the content is NEVER visually hidden at any point in the
 * reveal (important for screen-reader/snapping contexts and for tests
 * that query text synchronously mid-reveal).
 */
export function Reveal({
    children,
    className,
    /**
     * Stagger delay in ms (used to make a section's first row settle
     * slightly after the previous section's reveal).
     */
    delay = 0,
}: {
    children: React.ReactNode;
    className?: string;
    delay?: number;
}) {
    const ref = React.useRef<HTMLDivElement | null>(null);
    const [armed, setArmed] = React.useState(false);
    const [visible, setVisible] = React.useState(false);

    React.useEffect(() => {
        const el = ref.current;
        if (!el) {
            return;
        }

        const reduced = window.matchMedia(
            "(prefers-reduced-motion: reduce)",
        ).matches;
        if (
            reduced ||
            typeof IntersectionObserver === "undefined" ||
            // Already (partially) in view on mount: do not arm a hidden
            // delay for it — it is immediately readable content.
            el.getBoundingClientRect().top < window.innerHeight * 0.9
        ) {
            setVisible(true);
            return;
        }

        setArmed(true);
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries.some((entry) => entry.isIntersecting)) {
                    setVisible(true);
                    observer.disconnect();
                }
            },
            { rootMargin: "0px 0px -8% 0px", threshold: 0.05 },
        );
        observer.observe(el);
        return () => observer.disconnect();
    }, []);

    return (
        <div
            ref={ref}
            style={delay ? { transitionDelay: `${delay}ms` } : undefined}
            className={cn(
                "transition-transform duration-700 ease-out",
                armed && !visible ? "translate-y-4" : "translate-y-0",
                className,
            )}
        >
            {children}
        </div>
    );
}
