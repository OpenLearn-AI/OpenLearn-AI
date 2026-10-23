import Image from "next/image";
import Link from "next/link";

import { cn } from "@/lib/utils";

/**
 * The shared product identity mark (Batch 4.1): the logo plus the
 * product name, linked to the public landing.
 *
 * One component, three consumers — the landing top bar, the `(auth)`
 * entry layout, and the onboarding layout — so the identity block stays
 * identical everywhere instead of drifting between pages (the previous
 * login/register pages each hand-rolled an "OPENLEARN" wordmark).
 *
 * `sizes` keeps `next/image` from upscaling the small source asset on
 * large screens; the mark is decorative-plus-text: the logo's alt is
 * empty and the accessible name comes from the visible product name.
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
                src="/logo.png"
                alt=""
                width={36}
                height={36}
                className="size-9 rounded-lg"
                sizes="36px"
            />
            <span className="text-lg font-bold tracking-tight text-foreground">
                OpenLearn AI
            </span>
        </Link>
    );
}
