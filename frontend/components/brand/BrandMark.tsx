import Image from "next/image";
import Link from "next/link";

import { cn } from "@/lib/utils";

/**
 * The shared product identity mark (Batch 4.1): the logo plus the
 * product name, linked to the public landing.
 *
 * One component, three consumers — the landing top bar, the `(auth)`
 * entry layout (login + register), and formerly the onboarding layout —
 * so the identity block stays identical everywhere instead of drifting
 * between pages (the previous login/register pages each hand-rolled
 * an "OPENLEARN" wordmark).
 *
 * SIDE-02: the mark is the owner-supplied `public/logo.svg` — the
 * authoritative asset for the sidebar and the public/authentication
 * surfaces (the previous `/logo.png` reference had been broken since
 * the asset's removal in the owner's `f433002` commit). `unoptimized`
 * serves the SVG as-is (the image optimizer is not SVG-permitted by
 * the project's `next.config`), and `object-contain` preserves the
 * asset's intrinsic 249×220 aspect ratio inside the 36px box with no
 * crop, distortion, or painted background. `alt` stays empty: the
 * mark is decorative-plus-text, and the accessible name comes from
 * the visible product name.
 */
export function BrandMark({ className }: { className?: string }) {
    return (
        <Link
            href="/"
            className={cn(
                "flex items-center gap-2.5 rounded-lg outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
                className,
            )}
        >
            <Image
                src="/logo.svg"
                alt=""
                width={36}
                height={36}
                className="size-9 object-contain"
                unoptimized
            />
            <span className="text-lg font-bold tracking-tight text-foreground">
                OpenLearn AI
            </span>
        </Link>
    );
}
