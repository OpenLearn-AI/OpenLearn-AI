# OpenLearn AI — Design Tokens

## 1. Overview

This document defines the shared design tokens for the OpenLearn AI frontend.

The design system is implemented using:

* Tailwind CSS 4
* CSS custom properties
* The shadcn component conventions (base-nova style on Base UI), with the
  shadcn stylesheet **vendored** at `frontend/styles/shadcn.css` (Batch 3.2,
  W5) — the `shadcn` CLI is no longer a runtime dependency
* Light and dark themes
* OKLCH color values

These tokens are the shared UI contract for all future frontend work.

The token layer was reviewed and ratified by **Batch 3.1 — Design direction and tokens**
(2026-10-20). The binding decisions, their rationale, and the reserved hub-slot record
are captured in [ADR-0010](./adr/0010-frontend-design-direction-and-tokens.md).
**ADR-0010 was amended on 2026-10-23 (owner decision): the visual direction is now
Light Steel — Steel Blue accent on the Light Steel neutral ramp — with a minimalist,
text-first semantic-feedback policy and advisory borders with a strict focus ring;
Arabic typography is explicitly deferred to a separately scoped sub-batch.** The
amendment migrated token VALUES only: every token name below is unchanged.
Downstream batches reference tokens, never raw values: token names are stable, and
every literal color value lives only in `frontend/app/globals.css`.

---

## 2. Color System

### Core Colors

| Token                | Purpose                                 |
| -------------------- | --------------------------------------- |
| `background`         | Main application background             |
| `foreground`         | Main application text                   |
| `card`               | Card and elevated surface background    |
| `card-foreground`    | Text displayed on cards                 |
| `popover`            | Popover and floating surface background |
| `popover-foreground` | Text displayed in popovers              |

### Brand Colors

| Token                  | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `primary`              | Main brand and primary actions             |
| `primary-foreground`   | Content displayed on primary backgrounds   |
| `secondary`            | Secondary actions and surfaces             |
| `secondary-foreground` | Content displayed on secondary backgrounds |
| `accent`               | Highlighted or emphasized UI               |
| `accent-foreground`    | Content displayed on accent backgrounds    |

### Semantic Colors

| Token                | Purpose                                   |
| -------------------- | ----------------------------------------- |
| `success`            | Successful operations and positive states |
| `success-foreground` | Content displayed on success backgrounds  |
| `warning`            | Warnings and attention states             |
| `warning-foreground` | Content displayed on warning backgrounds  |
| `error`              | Errors and destructive states             |
| `error-foreground`   | Content displayed on error backgrounds    |
| `info`               | Informational states                      |
| `info-foreground`    | Content displayed on info backgrounds     |

The existing shadcn `destructive` tokens map to the `error` semantic tokens.

```css
--destructive: var(--error);
--destructive-foreground: var(--error-foreground);
```

(The `--destructive-foreground` alias and its `@theme inline` mapping were
added in Batch 3.2: the `text-destructive-foreground` utility previously
generated no CSS — the variable and mapping did not exist — so consumers of
that utility silently had no hover text color. The alias completes the
committed `destructive → error` alias chain.)

#### Minimalist semantic-feedback policy (ADR-0010 §2.7, 2026-10-23)

Semantic feedback is **text-first**. Routine success, warning, error, and
informational feedback does **not** use persistent tinted background panels:
the default treatment is a neutral surface with a compact semantic icon, a short
label, an inline message, or a status indicator. Semantic colors appear sparingly
— icons, labels, inline validation, compact indicators — and color never carries
state alone. Stronger treatment is reserved for genuinely destructive, blocking,
or high-severity states, as a justified exception. Component visual migration to
this policy belongs to the later batches that restyle those components.

Implemented values (both themes, text-grade on their own surfaces — every pair
AA-verified in the ledger validation matrix):

| Token | Light | Dark (owner-specified) |
| ------- | --------- | --------- |
| `--success` | `#2F7D46` | `#69DB7C` |
| `--warning` | `#B45309` (derived — see note) | `#FFC078` |
| `--error` | `#BE3B2E` | `#FF8787` |
| `--info` | `#2A7A9B` | `#74C0FC` |

The light `--warning` is the one derived value: with tinted panels rejected, one
value must serve both text-on-neutral (AA 4.5:1) and fill-with-light-ink roles;
`#B45309` is the lightest amber satisfying both (4.76:1 on the page surface,
5.02:1 on cards, 4.76:1 with `#F8F9FA` ink on fill) while keeping amber identity.
Darker candidates were pre-computed and rejected as unnecessary; brighter ambers
fail AA as text. The dark values are the owner-approved pastels used as text/
icon-grade colors on dark surfaces (≥ 6.4:1 on every dark surface), with the
committed dark `*-foreground` inks kept (all ≥ 8.5:1 on the new fills).

Token audit (2026-10-23): no `--success-bg`/`--warning-bg`/`--error-bg`/`--info-bg`
or `*-text` tokens exist in the repository — there was nothing to remove or
consolidate. The two-tier `--*` / `--*-foreground` set is the complete state API;
`--success` is consumed as text (`ProfileForm`), `--error` through the
`destructive` alias across primitives and the async-state kit, and
`text-destructive-foreground` by LogoutButton's solid hover. All are retained.

### Utility Colors

| Token              | Purpose                   |
| ------------------ | ------------------------- |
| `muted`            | Subtle backgrounds        |
| `muted-foreground` | Secondary or subdued text |
| `border`           | Default borders           |
| `input`            | Input borders             |
| `ring`             | Focus indicators          |

### Chart Colors

`chart-1` … `chart-5` are defined in both themes and map to the brand and
semantic hues (steel blue, green, amber, violet, terracotta). They currently have
**no consumers**: no charts ship today, and analytics surfaces are scheduled well
beyond the current roadmap horizon (plan W34+). The tokens exist so that the
first real chart consumes the palette instead of inventing hex values. They
are reserved, not deprecated — do not repurpose them for non-chart UI. The set
was realigned to the Light Steel series in the 2026-10-23 amendment (zero
consumers, zero render change); the amber step (`#D69E2E` light / `#E5B85C` dark)
sits below 3:1 on light surfaces and is recorded as advisory — per WCAG 1.4.1
charts must pair color with labels or shapes regardless.

### Sidebar Colors

The `sidebar-*` group (background, foreground, primary, accent, border, ring)
follows the shadcn scaffold convention and is defined in both themes. No
sidebar component exists in the application today; the application shell is
a top navbar. The group is kept for scaffold compatibility. If a future
redesign batch does not adopt a sidebar surface, removing the unused group is
a candidate for that batch's scope — not a decision made here.

---

## 3. Typography

The primary font is Geist Sans.

The monospace font is Geist Mono.

### Arabic / Latin fallback (D10 rail)

The sans stack is declared once, in `frontend/app/globals.css`:

```css
--font-sans: var(--font-geist-sans), var(--font-arabic), sans-serif;
```

* `--font-geist-sans` is loaded by `app/layout.tsx` (next/font, `latin` subset)
  and remains the LTR/English baseline.
* `--font-arabic` is **Noto Sans Arabic** (next/font, `arabic` subset,
  `display: swap`), loaded in the same layout. It activates automatically when
  Arabic glyphs or `dir="rtl"` content are present, so Arabic text never falls
  back to an arbitrary system font.
* This is the **D10 preparation rail**: LTR/English stays the default
  (`<html lang="en" dir="ltr">`); nothing is translated and no i18n framework
  is introduced. The rail only guarantees that Arabic content renders correctly
  when it arrives.

Components never reference font files or families directly — they consume the
stack through `font-sans` (applied to `html`) and inherit it.

### Typography Scale

| Token       |     Size | Line Height |
| ----------- | -------: | ----------: |
| `text-xs`   |  0.75rem |        1rem |
| `text-sm`   | 0.875rem |     1.25rem |
| `text-base` |     1rem |      1.5rem |
| `text-lg`   | 1.125rem |     1.75rem |
| `text-xl`   |  1.25rem |     1.75rem |
| `text-2xl`  |   1.5rem |        2rem |
| `text-3xl`  | 1.875rem |     2.25rem |
| `text-4xl`  |  2.25rem |      2.5rem |
| `text-5xl`  |     3rem |           1 |

Usage should follow the semantic importance of the content rather than using large sizes purely for visual emphasis.

---

## 4. Spacing

The spacing system follows a consistent 4px base unit.

| Token        |   Value |
| ------------ | ------: |
| `spacing-0`  |       0 |
| `spacing-1`  | 0.25rem |
| `spacing-2`  |  0.5rem |
| `spacing-3`  | 0.75rem |
| `spacing-4`  |    1rem |
| `spacing-5`  | 1.25rem |
| `spacing-6`  |  1.5rem |
| `spacing-8`  |    2rem |
| `spacing-10` |  2.5rem |
| `spacing-12` |    3rem |
| `spacing-16` |    4rem |
| `spacing-20` |    5rem |
| `spacing-24` |    6rem |

Spacing should be selected from this scale whenever possible.

---

## 5. Border Radius

The base radius is:

```css
--radius: 0.625rem;
```

Derived radius tokens are:

| Token        | Value                       |
| ------------ | --------------------------- |
| `radius-sm`  | `calc(var(--radius) * 0.6)` |
| `radius-md`  | `calc(var(--radius) * 0.8)` |
| `radius-lg`  | `var(--radius)`             |
| `radius-xl`  | `calc(var(--radius) * 1.4)` |
| `radius-2xl` | `calc(var(--radius) * 1.8)` |
| `radius-3xl` | `calc(var(--radius) * 2.2)` |
| `radius-4xl` | `calc(var(--radius) * 2.6)` |

---

## 6. Shadows

The shared shadow scale is:

| Token       | Usage                                |
| ----------- | ------------------------------------ |
| `shadow-xs` | Hairline elevation on inputs, selects, textareas, and the async-state kit cards |
| `shadow-sm` | Subtle elevation                     |
| `shadow-md` | Cards and standard elevated surfaces |
| `shadow-lg` | Larger elevated components           |
| `shadow-xl` | High-emphasis floating elements      |

`shadow-xs` and `shadow-sm` currently carry the same value (the Tailwind 4
`xs` value); both names are kept so each consumer's intent stays legible and
so future tuning can move them independently. All five values are declared
explicitly in the token layer — no consumer relies on a Tailwind default.

Components should avoid arbitrary shadow values unless a specific design requirement exists.

---

## 7. Responsive Breakpoints

The frontend uses the following responsive breakpoints:

| Token |  Width |
| ----- | -----: |
| `sm`  |  640px |
| `md`  |  768px |
| `lg`  | 1024px |
| `xl`  | 1280px |
| `2xl` | 1536px |

The default approach is mobile-first responsive design.

Example:

```tsx
<div className="text-sm md:text-base lg:text-lg">
  Responsive content
</div>
```

---

## 8. Interaction States

The primitives (Button, Input, Select, Textarea — the Badge primitive was
removed in Batch 3.2, S5) implement one shared state vocabulary, keyed on the
semantic tokens above. Batch 3.1 codifies it as the convention every restyled
or new component must follow; Batch 3.2 applies it during the primitive
restyle.

| State            | Convention (as implemented in the primitives)                              |
| ---------------- | -------------------------------------------------------------------------- |
| Focus (keyboard) | `focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50` |
| Hover            | Alpha-tint of the surface token (`hover:bg-primary/80`, `hover:bg-muted`). The destructive variant is the one exception: its fixed text token caps the passing tint at the base value, so hover flips to the solid fill (`hover:bg-destructive hover:text-destructive-foreground`) — AA-verified in both themes (Batch 3.2) |
| Active / pressed | Displacement only: `active:translate-y-px` (interactive primitives)         |
| Disabled         | `disabled:opacity-50 disabled:pointer-events-none` (+ `disabled:cursor-not-allowed` on form fields) |
| Invalid          | `aria-invalid:border-destructive aria-invalid:ring-destructive/20` (with dark-theme ring variants; the dark 50%-alpha border override was removed in Batch 3.2 so the full-opacity error border carries the invalid state in both themes) |
| Selected / open  | State-reflecting utilities: `aria-expanded:bg-muted`, Base UI `data-*` variants |

Rules:

* State styling consumes tokens (`ring`, `destructive`, `muted`) with alpha
  modifiers — never raw color literals.
* **Focus indication is the strict, non-negotiable signal** (ADR-0010 §2.8):
  always the `ring` token at the shared geometry (3px ring, 50% alpha,
  `border-ring` edge) so keyboard focus looks identical on every interactive
  element. The full-opacity `border-ring` edge is the part that must keep passing
  WCAG 1.4.11 against adjacent surfaces in BOTH themes (Steel Blue: 5.30:1 light,
  ~3.4:1 dark against cards; the 50%-alpha ring is reinforcement). Any primitive
  restyle must preserve this result.
* `aria-invalid` is the only invalid hook: state is driven by attribute, so
  it works with plain forms and Base UI fields alike.
* Disabled controls keep their shape and label (opacity, not `hidden`),
  preserving layout stability and screen-reader context.

---

## 9. Motion

Motion exists to communicate state — never to decorate. This is the
"calm, legible, purposeful" direction of the roadmap's Phase 3, and it is a
binding constraint: no gradient soup, no meaningless glassmorphism, no
animation that competes with content readability.

What is in use:

* `transition-colors` / `transition-all` on interactive primitives (Tailwind's
  default 150ms duration and easing are the ratified defaults — no custom
  duration or easing tokens exist because no consumer needs one).
* `tw-animate-css` is available for Base UI popup enter/exit animations.
* `animate-spin` on the loading indicator.
* Theme switching disables color transitions via next-themes'
  `disableTransitionOnChange`.

Reduced motion: a global `prefers-reduced-motion: reduce` guard lives in the
base layer of `frontend/app/globals.css`. It collapses transition and
animation durations to effectively zero and stops iteration. Loading remains
legible without motion — `LoadingBlock` carries its message in text with
`role="status"`/`aria-live="polite"`, so the spinner is a redundancy, never
the only signal.

Rules for downstream batches:

* Do not add custom durations or easings without a documented, product-based
  reason; prefer the defaults.
* Any new animated pattern must degrade acceptably under the reduced-motion
  guard and must not carry information that is unavailable in static form.
* No ambient/looping decoration (pulsing backgrounds, floating gradients).

---

## 10. Border Hierarchy

Borders express structure with one weight; elevation uses rings and shadows,
not heavier borders. **Policy (ADR-0010 §2.8, 2026-10-23): borders are advisory**
— quiet, subtle, and neutral; they are decorative structure, not the primary
state carrier. Keyboard focus is the strict signal (§8). Inputs remain
understandable without colored backgrounds: label + placeholder + border +
focus ring carry the affordance.

| Layer            | Convention                                              |
| ---------------- | ------------------------------------------------------- |
| Hairline borders | `border` (1px) with `border-border` on surfaces, dividers (`border-b`), and input edges (`border-input`) — advisory ratios: light `#DEE2E6` 1.30:1 vs card, `#ADB5BD` input 2.07:1; dark keeps the alpha-over-surface convention (10% / 15% white) |
| Card outline     | `ring-1 ring-foreground/10` on the Card primitive (soft, theme-adaptive outline) |
| Focus ring       | `ring-3 ring-ring/50` — the interaction-state geometry from §8; the strict, 1.4.11-passing part is the full-opacity `border-ring` edge |
| Icon-slot padding| see §11 — direction-sensitive, uses logical properties after the 3.2 restyle |

Rules:

* 1px is the default border weight. Use a heavier border only when a pattern
  is proven to need it, and record it in this document.
* Do not stack border + ring for decoration; rings are for focus and the
  card outline.
* There are no border-width tokens: Tailwind's width utilities plus the
  conventions above are the complete contract. If a consumer genuinely needs
  a configurable width, that is a new token decision with its own rationale —
  not a local literal.

---

## 11. RTL and Logical Properties (codified discipline)

The product is Arabic-first, and the D10 baseline is LTR/English with RTL as
a first-class prepared direction. The codified discipline:

1. **Direction-sensitive spacing and positioning use logical CSS properties**:
   `ms-*`/`me-*` (margin-inline-start/end), `ps-*`/`pe-*` (padding-inline),
   `start-*`/`end-*` (inset), and `text-start`/`text-end` (alignment). These
   flip automatically under `dir="rtl"`.
2. **Direction-neutral physical utilities remain fine**: `px-*`, `py-*`,
   `pt-*`, `pb-*`, and centered layouts are symmetric and RTL-safe — use them
   without hesitation.
3. **Physical left/right utilities (`pl-*`, `pr-*`, `ml-*`, `mr-*`,
   `text-left`, `text-right`, `left-*`, `right-*`) are allowed only for
   genuinely physical concerns** — e.g., positioning relative to the viewport
   edge regardless of reading direction, or a decoration that must not flip.
   Any other use is a defect.
4. **Directional icons** (arrows, chevrons) that encode reading direction
   must flip in RTL (`rtl:rotate-180` or a logical-position swap); icons that
   represent a physical object (a printer, a download tray) do not flip.
5. **Status (updated 2026-10-23, Batch 3.2):** the Navbar and UserInfo
   already used logical utilities (`border-s ps-3`, `ms-4`). The Button and
   Badge primitives paired their icon slots with physical padding
   (`has-data-[icon=inline-start]:pl-*` / `inline-end]:pr-*`) — recorded as a
   violation and routed to Batch 3.2, which **resolved it**: the Button icon
   slots now use logical `ps-*`/`pe-*`, and the unused Badge primitive was
   removed entirely (finding S5). The full RTL audit runs in Batch 4.4 with
   the Storybook direction toolbar.
6. **Verification**: `.storybook/preview.tsx` provides the Direction (LTR/RTL)
   toolbar that sets `dir` on the story iframe; both directions must be
   exercised when a component's layout is direction-sensitive.

---

## 12. Reserved Token Groups (no consumers today)

Two groups exist in the token layer without application consumers:

* **Charts** (`chart-1`…`chart-5`) — reserved for future analytics surfaces;
  see §2.
* **Sidebar** (`sidebar-*`) — shadcn scaffold compatibility; see §2.

Both are defined with full light/dark parity. They are documented so that
"unused" is a recorded fact with a reason, not a trap for later cleanup.

---

## 13. Light Theme

The default theme is the light theme.

Light mode uses:

* A near-white application background (`#F8F9FA`, the Light Steel ramp top)
* White surfaces
* **Steel Blue** as the primary brand color (`#3B6EA5`)
* Neutral secondary and muted surfaces (the Light Steel cool-grey ramp)
* Semantic success, warning, error, and info colors as text-grade values

The primary color is Steel Blue (ADR-0010 as amended 2026-10-23).

---

## 14. Dark Theme

Dark mode is activated using the `.dark` class.

Dark mode provides:

* Dark application backgrounds — a deliberate surface ladder (`#171A1E` page →
  `#1F2328` card → `#262B31` popover), not an inversion of the light theme
* Dark elevated surfaces
* Adjusted primary colors for visibility (the lighter steel tone `#6E9CC9` with
  dark ink — mirroring the light theme's filled-primary pattern)
* Softer borders (alpha-over-surface)
* High-contrast foreground colors (capped at `#E9ECEF`, never pure white)
* Semantic colors as the owner-approved text-grade pastels for dark backgrounds

The same semantic token names are used in both themes.

For example:

```css
--primary
--success
--warning
--error
--info
```

Components should therefore never need to know whether the application is currently using light or dark mode.

---

## 15. Tailwind CSS 4 Integration

The design tokens are exposed to Tailwind CSS 4 through the `@theme inline` block in:

```text
frontend/app/globals.css
```

Example:

```css
@theme inline {
  --color-primary: var(--primary);
  --color-success: var(--success);
  --color-warning: var(--warning);
  --color-error: var(--error);
  --color-info: var(--info);
}
```

This allows components to use semantic utility classes such as:

```tsx
bg-primary
text-primary-foreground
bg-success
text-success-foreground
bg-warning
text-warning-foreground
bg-error
text-error-foreground
bg-info
text-info-foreground
```

---

## 16. Theme Usage Rules

### Do

* Use semantic design tokens.
* Use Tailwind utility classes connected to the tokens.
* Use the same token names across light and dark themes.
* Prefer existing spacing, radius, and shadow values.
* Use shadcn/ui components where applicable.
* Keep component styling consistent with the design system.

### Don't

* Hard-code brand colors inside components.
* Introduce arbitrary spacing values without a clear reason.
* Create separate component colors for light and dark mode.
* Override shadcn semantic tokens unnecessarily.
* Introduce new design tokens without documenting them.
* Use physical left/right utilities (`pl-*`, `pr-*`, `ml-*`, `mr-*`,
  `text-left/right`) for direction-sensitive layout — use the logical
  properties from §11 instead.
* Add motion that decorates rather than communicates (see §9).
* Build routine success/warning/error/info feedback as persistent tinted
  background panels or oversized colored alert cards — use the minimalist,
  text-first treatments from §2 (ADR-0010 §2.7); color never carries state
  alone.

---

## 17. Source of Truth

The primary implementation is:

```text
frontend/app/globals.css
```

The shadcn stylesheet (custom `data-*` variants and popup utilities consumed
by the primitives) is vendored at:

```text
frontend/styles/shadcn.css
```

It is a verbatim copy of the `shadcn` package's `dist/tailwind.css`
(v4.18.0, MIT — attribution header and license copy included in the same
directory). Batch 3.2 (W5) vendored it and removed the `shadcn` CLI from the
runtime dependencies; the stylesheet is now repository-owned. If a future
batch upgrades the vendored stylesheet, it must re-verify the attribution
header and this document in the same change.

The documentation is:

```text
docs/design-tokens.md
```

Any future changes to the design system should update both the implementation and this documentation.

---

## 18. Review Status

Status: **Batch 3.1 — Design direction and tokens (ratified 2026-10-20); AMENDED
2026-10-23 — Light Steel design-token migration (owner-authorized); Batch 3.2 —
Design system foundations in code applied to the primitives (2026-10-23).**

The original review ratified the then-existing token layer group-by-group. The
2026-10-23 amendment (recorded in [ADR-0010](./adr/0010-frontend-design-direction-and-tokens.md)
§1.1, §2.1, §2.7–§2.9) superseded the visual direction to **Light Steel** and
migrated the color VALUES in `frontend/app/globals.css` — token names, the
Tailwind 4 CSS-first model, the next-themes class strategy, typography,
spacing, radius, shadow, and breakpoint decisions are all unchanged. The
semantic-feedback policy is now minimalist and text-first (§2), borders are
advisory with a strict focus ring (§8/§10), and the Arabic-font decision is
explicitly deferred to a separately scoped sub-batch. Every foreground/background
pair created or affected by the migration was contrast-verified in both themes
(see the Batch 3.1-amendment ledger entry for the validation matrix, including
the four recorded sub-threshold states that live in committed component classes
and are routed to Batch 3.2). The frontend production build and the full check
chain were re-verified after the migration (see the ledger entry for the exact
results).

Batch 3.2 (2026-10-23) applied the interaction-state vocabulary across the
primitive set: the five routed sub-threshold states were fixed (destructive
hover now flips to the solid fill with `text-destructive-foreground`; the dark
50%-alpha invalid-border override was removed in favor of the full-opacity
error border), the Button/Badge icon-slot RTL violation was resolved (logical
padding on Button; Badge removed with S5), the destructive-foreground alias
was completed, and the alert-dialog primitive was added
(`components/ui/dialog.tsx`). See the Batch 3.2 ledger entry for the full
validation matrix.
