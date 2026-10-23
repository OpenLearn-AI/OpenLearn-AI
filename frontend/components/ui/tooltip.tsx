import * as React from "react"
import { Tooltip as TooltipPrimitive } from "@base-ui/react/tooltip"

import { cn } from "@/lib/utils"

/**
 * Tooltip primitive (Batch 3.3).
 *
 * Composed on the Base UI tooltip parts (the repository's only
 * component library — no new dependency) with the shadcn base-nova
 * structure: `data-slot` attributes, the vendored stylesheet's
 * `data-open`/`data-closed` variants, and tw-animate-css enter/exit
 * motion at 100ms under the reduced-motion guard (§9 of
 * docs/design-tokens.md).
 *
 * Semantics (owned by Base UI): the tooltip opens on hover AND
 * keyboard focus, so a collapsed sidebar's icon-only controls get a
 * visible name on both interaction paths. Tooltips are a visual
 * reinforcement only — they must never be the sole source of an
 * accessible name (callers keep `aria-label` / visually-hidden text
 * on the trigger).
 *
 * Positioning is direction-aware: the placement `side` accepts
 * Base UI's logical values (`inline-start` / `inline-end`), which
 * flip automatically under `dir="rtl"`.
 */

function TooltipProvider({
  ...props
}: TooltipPrimitive.Provider.Props) {
  return <TooltipPrimitive.Provider data-slot="tooltip-provider" {...props} />
}

function Tooltip({ ...props }: TooltipPrimitive.Root.Props) {
  return (
    <TooltipProvider>
      <TooltipPrimitive.Root data-slot="tooltip" {...props} />
    </TooltipProvider>
  )
}

function TooltipTrigger({
  ...props
}: TooltipPrimitive.Trigger.Props) {
  return <TooltipPrimitive.Trigger data-slot="tooltip-trigger" {...props} />
}

function TooltipContent({
  className,
  side = "top",
  sideOffset = 6,
  children,
  ...props
}: TooltipPrimitive.Popup.Props &
  Pick<TooltipPrimitive.Positioner.Props, "side" | "sideOffset">) {
  return (
    <TooltipPrimitive.Portal data-slot="tooltip-portal">
      <TooltipPrimitive.Positioner
        data-slot="tooltip-positioner"
        className="z-50 outline-none"
        side={side}
        sideOffset={sideOffset}
      >
        <TooltipPrimitive.Popup
          data-slot="tooltip-content"
          className={cn(
            "z-50 w-fit rounded-md bg-popover px-3 py-1.5 text-xs text-popover-foreground shadow-md ring-1 ring-foreground/10 duration-100 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95",
            className
          )}
          {...props}
        >
          {children}
        </TooltipPrimitive.Popup>
      </TooltipPrimitive.Positioner>
    </TooltipPrimitive.Portal>
  )
}

export { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger }
