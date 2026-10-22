# ADR-0010: Frontend Design Direction and Token Layer Ratification

* **Status:** Accepted (2026-10-20) — Batch 3.1 design-decision record; implementation delivered as a patch for owner review
* **Date:** 2026-10-20
* **Decision Owners:** Muhammad Seyam (Product Owner); decisions derived by Batch 3.1 from already-accepted decisions (D9, D10), the Integrated Frontend Execution Roadmap v2.0 (§9, §14, §16, §17), and repository evidence
* **Scope:** Phase 3 / Batch 3.1 — design direction, token layer, design documentation, RTL logical-properties discipline, hub-slot reservation record
* **Related:** ADR-0002 (documentation authority), the Modernization architecture baseline **D9** (token foundation, not final design) and **D10** (LTR/Arabic/RTL rails), `docs/design-tokens.md`, `frontend/app/globals.css`, the Integrated Frontend Execution Roadmap v1.1.docx (§9 hub-slot table, Batch 3.1/3.2/4.3/4.4 specifications), `GLM-batch-n-patch-lifecycle-rules.md`

## 1. Context

Batch 3.1 is the first batch of Phase 3 (UI/UX Direction and Foundations, Gate D).
The roadmap requires the direction to be defined **before any page is redesigned**,
encoded as tokens and recorded in a design-decision ADR — including the Section 9
hub-slot record. The repository already contains a complete, coherent token layer
(`frontend/app/globals.css`: Tailwind 4 CSS-first `@theme inline` mapping over
`:root`/`.dark` CSS variables, OKLCH values, next-themes class strategy) and token
documentation (`docs/design-tokens.md`), established during the modernization work.

Two accepted decisions frame what Phase 3 is:

* **D9** — the existing token system is a *stable styling/token foundation*, not the
  final visual design. The redesign happens **on top of** that foundation.
* **D10** — the product is Arabic-first; the delivered baseline is LTR/English with
  Arabic/RTL **prepared** as a first-class direction (Arabic-capable font in the
  token stack, `dir` usage, logical CSS properties, both-direction verification).
  No i18n framework and no translation work.

Batch 3.1's binding constraints (roadmap §14, Batch 3.1 row): do not change the
Tailwind 4 CSS-first model; do not change the next-themes class strategy; do not
rename tokens consumed by components unless call sites move in the same batch; and
prefer the smallest coherent extension. The anti-cliché constraints apply from
Phase 3 onward: no gradient soup, no meaningless glassmorphism, no decoration that
fights legibility or RTL.

## 2. Decision

### 2.1 Visual direction

The ratified direction for OpenLearn-AI is the **existing token foundation applied
with discipline**: a single indigo brand hue (OKLCH hue 264) on cool neutral
surfaces, a complete semantic state palette (success/warning/error/info), Geist
Sans with Noto Sans Arabic fallback, a 4px spacing rhythm, one hairline border
weight, and restrained elevation. The product is a calm, legible, purposeful
learning surface. Decorative effects the direction deliberately keeps absent:
gradients, glassmorphism/backdrop-blur surfaces, ambient or looping animation,
and any motion that does not communicate state.

No palette replacement, no token renames, and no new visual language are
introduced. Every consequential choice below is already determined by D9, D10,
the Batch 3.1 scope, and the repository evidence; none required a new owner
product decision.

### 2.2 Token-group decisions

| # | Group | Action | Basis |
|---|-------|--------|-------|
| 1 | Core, brand, muted, border/input/ring colors | **KEEP** | Complete both-theme parity (verified programmatically: 39/39 `@theme` color tokens resolve in `:root` and `.dark`); consumed across all primitives and pages; D9 foundation |
| 2 | Semantic state colors + `destructive`→`error` alias | **KEEP** | Consumed by primitives (`aria-invalid`) and the async-state kit; parity complete |
| 3 | Light/dark parity + next-themes class strategy | **KEEP** | `.dark` class + `@custom-variant dark`; Storybook dark sync depends on it |
| 4 | Typography (Geist Sans/Mono + Noto Sans Arabic, scale) | **KEEP** tokens; **EXTEND** documentation | D10 rail is correct as implemented; documentation previously omitted the Arabic fallback rationale entirely — now codified in `docs/design-tokens.md` §3 |
| 5 | Spacing (4px grid, steps 0–24) | **KEEP**; **EXTEND** documentation | Used consistently; direction-neutrality rule now stated (§4 in design-tokens) |
| 6 | Radius (base 0.625rem + derived scale) | **KEEP** | Consistent consumers (`rounded-lg` … `rounded-4xl`) |
| 7 | Shadows | **KEEP** scale; **formalize `--shadow-xs`** | `shadow-xs` is already consumed by Select, Textarea, LoadingBlock, ErrorState but was only riding Tailwind's default; it is now declared explicitly in the token layer with the identical value (additive, zero render change) |
| 8 | Breakpoints (sm…2xl) | **KEEP** | Tailwind defaults, documented |
| 9 | Charts (`chart-1…5`) | **KEEP** as reserved | Zero consumers today (analytics is plan W34+); documented as reserved, not deprecated |
| 10 | Sidebar (`sidebar-*`) | **KEEP** as scaffold compatibility | Zero consumers (shell is a top navbar); potential removal is flagged for a future batch's scope, not decided here |
| 11 | Interaction states | **EXTEND** — codified, no new CSS tokens | The primitives already implement one uniform vocabulary (focus-visible `ring-3 ring-ring/50`; hover alpha tints; `active:translate-y-px`; `disabled:opacity-50`; `aria-invalid` destructive states; `aria-expanded`/Base UI `data-*` for selected/open). Codified in `docs/design-tokens.md` §8 as the convention for Batch 3.2 and Phase 4. Adding CSS state tokens now would be unused invention |
| 12 | Motion | **EXTEND** — one code change + codification | Genuine deficiency: zero `prefers-reduced-motion` handling existed. A base-layer reduced-motion guard is added to `globals.css` (see §2.4). Duration/easing conventions are documented (Tailwind defaults; `tw-animate-css` for popups) rather than invented as tokens |
| 13 | Border hierarchy | **EXTEND** — documentation only | 1px hairline discipline + card `ring-1 ring-foreground/10` outline + focus ring geometry codified in `docs/design-tokens.md` §10; no width tokens exist or are needed |
| 14 | RTL logical properties | **EXTEND** — codified discipline | Codified in `docs/design-tokens.md` §11 and §4 of this ADR. Two known primitive violations (Button/Badge icon-slot physical `pl-*`/`pr-*`) are recorded and **routed to Batch 3.2** (primitive restyle scope); the full RTL audit is Batch 4.4's |

### 2.3 Token naming and consumption rules (stable for downstream batches)

1. Existing token names are **frozen** as the public contract: `background`,
   `foreground`, `card`, `popover`, `primary`, `secondary`, `accent`, `muted`,
   `destructive`, `border`, `input`, `ring`, `success`, `warning`, `error`,
   `info`, `chart-*`, `sidebar-*`, plus the font/spacing/radius/shadow/breakpoint
   namespaces. No renames in any later batch without a new ADR.
2. Literal color values live **only** in `frontend/app/globals.css`. Components
   consume tokens through Tailwind utilities (`bg-primary`, `text-muted-foreground`,
   `ring-ring/50`) — never raw hex/oklch literals.
3. New tokens require: a demonstrated consumer need, documentation in
   `docs/design-tokens.md`, and light/dark parity at birth.
4. Tailwind 4's CSS-first model is unchanged: `@theme inline` maps semantic
   utilities to the variable layer; `shadcn/tailwind.css` remains imported until
   Batch 3.2 removes the shadcn runtime dependency (W5).

### 2.4 Reduced-motion guard (the batch's only behavioral CSS)

Added to the base layer of `globals.css`:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Rationale: the product previously had no reduced-motion handling while shipping
transitions and an infinite loading spinner — an accessibility gap (WCAG 2.3.3)
in a product whose direction is calm, sustained learning. Loading remains fully
legible without motion: `LoadingBlock` carries its message as text with
`role="status"`/`aria-live="polite"`, so the spinner is redundant, not the only
signal. Theme switching already suppresses color transitions via next-themes'
`disableTransitionOnChange`.

### 2.5 RTL logical-properties discipline (codified)

1. Direction-sensitive spacing/positioning uses logical properties
   (`ms-*`/`me-*`, `ps-*`/`pe-*`, `start-*`/`end-*`, `text-start`/`text-end`).
2. Direction-neutral utilities (`px-*`, `py-*`, `pt-*`, `pb-*`, centered
   layouts) are RTL-safe and remain allowed.
3. Physical left/right utilities are legitimate **only** for genuinely physical
   concerns (viewport-edge positioning that must not flip; decorations that
   must not flip). Any other use is a defect.
4. Directional icons that encode reading direction flip in RTL
   (`rtl:rotate-180` or logical swap); object-representing icons do not.
5. Known current violations are recorded, not silently patched in this batch:
   Button and Badge pair their `inline-start`/`inline-end` icon slots with
   physical `pl-*`/`pr-*` padding — the fix belongs to Batch 3.2's primitive
   restyle; the systematic audit is Batch 4.4's (with the Storybook direction
   toolbar and the 5.2 sweep).

### 2.6 Section 9 hub-slot record (reserved, documented — never rendered)

The roadmap designates the course-detail page as the **content/learning hub**
(roadmap §9). Its composition happens in Batch 4.3 with stable regions; the
future capability slots below are **IA reservations recorded here and in the
Batch 4.3 batch note**. They are documentation, never rendered UI: no placeholder
screens, no empty coming-soon panels, no fake data, no search box that searches
nothing, no chat composer, no citation chips pointing at nothing, no speculative
API clients. When a contract lands in `docs/openapi.json`, the corresponding
surface arrives as a new authorized batch against that contract.

| Region / slot | Content when implemented | Built in |
|---|---|---|
| Course header + actions | Title, description, metadata; edit/delete for the owning instructor (existing capabilities) | 4.3 (redesign of existing) |
| Materials region | Materials list; upload affordance (owning instructor only); status presentation with honest failed-state copy | 4.3 (new, scheduled scope) |
| Hub slot: extracted text | Document content viewer per page | Reserved — plan W9, no contract yet |
| Hub slot: search | Retrieval search + results with chunk→document links | Reserved — plan W10 |
| Hub slot: chunks/source | Chunk inspection panel | Reserved — plan W11 |
| Hub slot: citations | Ranked citations (W13), citation chips (W14) | Reserved — contracts pending |
| Hub slot: AI assistant | Chat on sessions API + streaming | Reserved — plan W15–16, Gate 1 |
| Hub slot: enrollment/learning entry | Student enrollment + learning entry points | Reserved — plan W17 |

Token-layer consequence: no tokens are created for these slots. Future surfaces
compose from the ratified token layer; any genuinely missing token is decided
when its consumer is built (per §2.3 rule 3), never speculatively in advance.

## 3. Consequences

* Downstream batches (3.2, 3.3, Phase 4) consume a ratified, stable token layer
  and a documented state/motion/border/RTL vocabulary — tokens, never raw values.
* The token documentation (`docs/design-tokens.md`) now answers *why each group
  exists*, including the two reserved groups, instead of only listing values.
* `prefers-reduced-motion` users get a still, fully legible interface; no
  information is carried by motion alone.
* The Button/Badge icon-slot RTL defect is explicitly assigned to Batch 3.2 —
  recorded here so it cannot be lost between batches.
* Token renames are locked behind a new ADR; raw color literals in components
  are reviewable violations of this record.

## 4. Alternatives considered

* **Introducing dedicated interaction-state, duration, easing, and border-width
  CSS tokens now** — rejected: no consumer divergence exists to encode; the
  primitives already share one vocabulary keyed on semantic tokens, and unused
  tokens would be inventory decoration, violating the smallest-coherent-extension
  rule. Revisit only when a real consumer need appears.
* **A new palette / visual language in 3.1** — rejected: D9 explicitly stages the
  intentional visual redesign on top of the stable foundation, and the binding
  batch constraints forbid inventing a palette without product-based evidence.
  The evidence shows a coherent, purposeful palette; replacing it would be
  fashionable styling, the exact anti-cliché the roadmap prohibits.
* **Fixing the Button/Badge physical icon-slot padding in this batch** —
  rejected: it is a primitive class-string change, which is Batch 3.2's scope
  ("restyle primitives"); Batch 3.1 must not begin 3.2. Recorded instead.
* **Removing the unused `sidebar-*` tokens** — deferred: zero consumers today,
  but removal is a code-surface decision that belongs to a batch authorized to
  touch the token layer's consumers; flagged in `docs/design-tokens.md` §2.
