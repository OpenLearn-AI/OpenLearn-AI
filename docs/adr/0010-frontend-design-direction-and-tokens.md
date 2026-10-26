# ADR-0010: Frontend Design Direction and Token Layer Ratification

* **Status:** Accepted (2026-10-20) — Batch 3.1 design-decision record; implementation delivered as a patch for owner review. **Amended (2026-10-23) — the visual direction is superseded from indigo to Light Steel (Steel Blue accent) by owner decision (§2.1, §2.7–§2.9); the amended token layer is delivered as a patch for owner review.** **Re-amended (2026-10-24) — Batch 4.2 reline: the public experience is fixed dark and the accent identity is brass (§2.1.1); token names and the structural rules of this ADR are unchanged.**
* **Date:** 2026-10-20; amended 2026-10-23; re-amended 2026-10-24
* **Decision Owners:** Muhammad Seyam (Product Owner); the original decisions were derived by Batch 3.1 from already-accepted decisions (D9, D10), the Integrated Frontend Execution Roadmap v2.0 (§9, §14, §16, §17), and repository evidence. The 2026-10-23 amendment (Light Steel palette with Steel Blue accent, advisory borders with a strict focus ring, minimalist text-first semantic feedback, Arabic-typography deferral) was decided by the owner in the Light Steel review cycle and authorized for implementation by the owner's task directive.
* **Scope:** Phase 3 / Batch 3.1 — design direction, token layer, design documentation, RTL logical-properties discipline, hub-slot reservation record; **amendment scope (2026-10-23): token VALUE migration in `frontend/app/globals.css` plus the design documentation and progress ledger — token names, the Tailwind 4 CSS-first model, the next-themes class strategy, and all component/page code unchanged. Re-amendment scope (2026-10-24, Batch 4.2): the same VALUE-migration discipline, plus the fixed-dark public experience and the public motion vocabulary — this batch's deliverable surface; token names, the Tailwind 4 CSS-first model, and the next-themes class strategy remain unchanged**
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

### 1.1 Amendment context (2026-10-23)

The original decision ratified the indigo token foundation unchanged, on the
repository evidence available at Batch 3.1 time. The owner subsequently commissioned
a dedicated design review of that direction. The review produced the Light Steel
proposal artifacts (design proposal, semantic token specification, migration plan,
evidence/validation report, and an interactive review prototype) and packaged three
blocking decisions for the owner with computed comparisons: accent strategy (Steel
Blue vs Muted Teal vs Academic Claret), border policy (advisory vs strict 3:1), and
Arabic typography (candidates and fallback behavior). The owner decided on
2026-10-23: **Steel Blue** as the accent, **advisory borders with a strict focus
ring**, **Arabic typography deferred** to a separately scoped sub-batch, and a
**minimalist, text-first semantic-feedback system** that replaces the proposal's
per-status tinted surface tiers. This ADR records that decision in place: the
indigo direction is superseded, not deleted — the original reasoning is preserved
in §2.2's KEEP-to-MIGRATED history and §4 for the record. The repository documents
that were amended: this ADR, `docs/design-tokens.md`, the execution ledger, and the
token layer itself.

## 2. Decision

### 2.1 Visual direction (amended 2026-10-23)

The ratified direction for OpenLearn-AI is **Light Steel**: a restrained steel-blue
interface on neutral, calm surfaces. The brand accent is **Steel Blue** — `#3B6EA5`
(light theme) / `#6E9CC9` (dark theme) — carried by the existing `--primary` token.
All structural colors sit on the Light Steel cool-grey ramp (page `#F8F9FA`, white
content surfaces, hue ≈ 248–256, chroma ≤ 0.016); the ramp's steps are the neutral
vocabulary for surfaces, borders, and muted text. The dark theme is a deliberate
ladder (`#171A1E` page → `#1F2328` card → `#262B31` popover) with text capped at
`#E9ECEF` — built from the same undertone, not an inversion of the light theme.
Semantic state colors stay visually distinct from the brand accent and are used
sparingly under the minimalist semantic-feedback policy (§2.7). Decorative effects
the direction deliberately keeps absent: gradients, glassmorphism/backdrop-blur
surfaces, ambient or looping animation, routine tinted status panels, and any
motion that does not communicate state.

Token **names** are unchanged by this amendment; only **values** migrated
(`frontend/app/globals.css` `:root`/`.dark` blocks — the complete literal layer).
The migration was authorized by the owner as the Batch 3.1 amendment; the original
§2.1 (indigo retained with no palette replacement) is superseded and preserved in
§4 for the historical record.

### 2.1.1 Re-amendment: fixed dark + brass (Batch 4.2 reline, 2026-10-24)

The Batch 4.2 owner directive retunes the ratified composition and resolves its
one structural tension: a public marketing/auth experience whose character
(read: click-through pulse) conflicts with Light Steel's page-and-workspace
calm. The reline operates entirely under §2.3's rules — names frozen, values
migrated:

* **Accent identity: brass.** The steel-blue accent is replaced by brass —
  `#E1B66C` as the dark-theme fill with warm ink `#17130E` on it, a
  lighter step for hovers, and deep brass `#815C0A` for light-theme sidebar
  emphasis; the light theme's `--primary` returns to warm ink (`#232019`,
  fills read as print) with `--ring` brass on the warm paper ramp
  (`#FAF9F5` page / white surfaces, border `#E5E1D8`, input `#B3AA9C`).
  The dark ladder is unchanged from Batch 3.1's composition
  (`#171A1E` → `#1F2328` → `#262B31`): the charcoal base was the amber
  decision the reline keeps.
* **The public experience is fixed dark.** The landing, onboarding, and
  auth shells (and the Keycloak hosted pages, whose theme mirrors the dark
  ladder statically) wrap themselves in `.dark` and ignore stored
  preference; `defaultTheme="dark"` at the root; only `(app)` routes keep
  the user-facing Light/Dark toggle (toggle content unchanged — §2.2 row 3
  stands).
* **A public motion vocabulary is sanctioned.** `ol-enter` (translation-only
  entrances, staggered), `ol-draw` (SVG stroke drawing), and `ol-breathe`
  (a slow non-content loop, decorative `aria-hidden` only) join the token
  layer's behavioral CSS; the Batch 3.1 reduced-motion guard (§2.4) covers
  them without restatement. Translation-only entrances are required: public
  content may never be hidden pre-entry.
* Semantic-feedback policy (§2.7), border hierarchy (§2.8), RTL discipline
  (§2.5), typography (§2.9), spacing/radius/shadows/breakpoints, naming
  rules, and the hub-slot reservation are all untouched. Charts realign to
  the warm series (still zero consumers).

### 2.2 Token-group decisions

| # | Group | Action | Basis |
|---|-------|--------|-------|
| 1 | Core, brand, muted, border/input/ring colors | **MIGRATED (values; names unchanged) — 2026-10-23 amendment** | Light Steel ramp + Steel Blue accent per the owner decision (§2.1); every migrated pair re-validated (ledger validation matrix); consumed across all primitives and pages |
| 2 | Semantic state colors + `destructive`→`error` alias | **MIGRATED (values; names unchanged) — 2026-10-23 amendment** | Minimalist text-first policy (§2.7): light values derived text-grade, dark values owner-specified pastels; alias preserved; consumed by primitives (`aria-invalid`), the async-state kit, and ProfileForm's success message |
| 3 | Light/dark parity + next-themes class strategy | **KEEP** | `.dark` class + `@custom-variant dark`; Storybook dark sync depends on it; parity re-verified after migration |
| 4 | Typography (Geist Sans/Mono + Noto Sans Arabic, scale) | **KEEP** tokens; **font-face decision explicitly DEFERRED** (§2.9, 2026-10-23) | D10 rail is correct as implemented; any font change (e.g. IBM Plex Sans Arabic, Cairo) goes to a separately scoped, explicitly authorized sub-batch — none of it in this batch |
| 5 | Spacing (4px grid, steps 0–24) | **KEEP**; **EXTEND** documentation | Used consistently; direction-neutrality rule now stated (§4 in design-tokens) |
| 6 | Radius (base 0.625rem + derived scale) | **KEEP** | Consistent consumers (`rounded-lg` … `rounded-4xl`) |
| 7 | Shadows | **KEEP** scale; **formalize `--shadow-xs`** | `shadow-xs` is already consumed by Select, Textarea, LoadingBlock, ErrorState but was only riding Tailwind's default; it is now declared explicitly in the token layer with the identical value (additive, zero render change) |
| 8 | Breakpoints (sm…2xl) | **KEEP** | Tailwind defaults, documented |
| 9 | Charts (`chart-1…5`) | **KEEP as reserved**; values realigned to the Light Steel series (zero consumers) | Zero consumers today (analytics is plan W34+); reserved, not deprecated — realignment keeps the reserved set on the approved palette; the amber step is recorded as advisory under WCAG 1.4.1 (charts pair color with labels/shapes) |
| 10 | Sidebar (`sidebar-*`) | **KEEP** as scaffold compatibility; values realigned (zero consumers) | Zero consumers (shell is a top navbar); potential removal is flagged for a future batch's scope, not decided here |
| 11 | Interaction states | **EXTEND** — codified, no new CSS tokens | The primitives already implement one uniform vocabulary (focus-visible `ring-3 ring-ring/50`; hover alpha tints; `active:translate-y-px`; `disabled:opacity-50`; `aria-invalid` destructive states; `aria-expanded`/Base UI `data-*` for selected/open). Codified in `docs/design-tokens.md` §8 as the convention for Batch 3.2 and Phase 4. Adding CSS state tokens now would be unused invention |
| 12 | Motion | **EXTEND** — one code change + codification | Genuine deficiency: zero `prefers-reduced-motion` handling existed. A base-layer reduced-motion guard is added to `globals.css` (see §2.4). Duration/easing conventions are documented (Tailwind defaults; `tw-animate-css` for popups) rather than invented as tokens |
| 13 | Border hierarchy | **EXTEND** — documentation only; policy amended 2026-10-23 (§2.8) | 1px hairline discipline + card `ring-1 ring-foreground/10` outline + focus ring geometry codified in `docs/design-tokens.md` §10; borders are advisory, the focus ring is the strict signal; no width tokens exist or are needed |
| 14 | RTL logical properties | **EXTEND** — codified discipline | Codified in `docs/design-tokens.md` §11 and §2.5 of this ADR. Two known primitive violations (Button/Badge icon-slot physical `pl-*`/`pr-*`) are recorded and **routed to Batch 3.2** (primitive restyle scope); the full RTL audit is Batch 4.4's |
| 15 | Semantic-feedback treatment | **NEW POLICY** — minimalist, text-first (§2.7, 2026-10-23) | Owner modification: no routine tinted status panels; neutral surfaces + compact icons/labels/inline messages; the proposal's per-status soft tiers were NOT implemented |
| 16 | Borders and focus | **NEW POLICY** — advisory borders + strict focus ring (§2.8, 2026-10-23) | Owner decision: quiet neutral borders; keyboard focus is the strict, non-negotiable signal, validated in both themes |

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

The 2026-10-23 amendment operated strictly under these rules: **token names are
unchanged and no new tokens were created**. The reviewed proposal's additional
tokens (per-status `-soft`/`-on-soft`/`-border` tiers, `--selected`, `--link`,
`--placeholder`, `--overlay`, `--tooltip-*`, `--border-subtle`, `--border-strong`,
`--primary-hover`/`--primary-active`) were **not** implemented because none has a
current consumer; under rule 3 they remain decisions for the batches that build
those consumers (Batch 3.2 onward). The two-tier `--*` / `--*-foreground` semantic
set is the complete state API today.

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

### 2.7 Minimalist semantic feedback (owner modification, 2026-10-23)

Semantic state colors provide meaning without dominating the interface. This is a
binding design-system rule for all component work from Batch 3.2 onward (this
batch changed tokens and documentation only — component visual migration belongs
to the relevant later batches):

1. Routine success, warning, error, and informational feedback does **not** use
   persistent tinted background panels by default. The default treatment is a
   neutral surface with a compact semantic icon, a short label, an inline message,
   or a status indicator. The reviewed proposal's per-status tinted-surface tiers
   (`-soft`/`-on-soft`/`-border`) were therefore **not** implemented.
2. Semantic colors are used sparingly: icons, labels, inline validation, and
   compact indicators.
3. No oversized colored alert cards, no decorative gradients, no redundant visual
   treatments.
4. Color never carries state alone: messages stay explicit and accessible.
5. Genuinely destructive, blocking, or high-severity states may keep stronger
   treatment where the actual interaction or accessibility need justifies it
   (existing example: the destructive-action confirmation surface), as a justified
   exception — never a blanket styling pattern.
6. Token set: the two-tier `--*` / `--*-foreground` names are kept (audited:
   `--success` is consumed as text in ProfileForm; `text-destructive-foreground`
   is consumed by LogoutButton's solid-hover; no `--*-bg`/`--*-text` tokens exist
   in the repository, so there was nothing to remove or consolidate). Light-theme
   values are text-grade on neutral surfaces: success `#2F7D46`, warning `#B45309`,
   error `#BE3B2E`, info `#2A7A9B`. Dark-theme values are the owner-specified
   pastels: success `#69DB7C`, warning `#FFC078`, error `#FF8787`, info `#74C0FC`,
   with the committed dark `-foreground` inks kept (verified ≥ 8.5:1 on the new
   fills).
7. Light-theme warning derivation: with tinted panels rejected, one value must
   serve both text-on-neutral (AA 4.5:1) and fill-with-light-ink roles. `#B45309`
   is the lightest amber satisfying both (4.76:1 on `#F8F9FA`, 5.02:1 on white,
   4.76:1 light-ink-on-fill) while keeping amber identity; the derivation and
   rejected candidates are recorded in the ledger's validation matrix and
   documented in `docs/design-tokens.md` §2.
8. Compatibility rule (owner directive): tokens already consumed by components are
   preserved; no application component was edited to force the new design into
   place. Known sub-threshold states that live in committed component classes
   (destructive hover tints; the dark 50%-alpha invalid border) are recorded in
   the ledger validation matrix and routed to Batch 3.2's primitive restyle.

### 2.8 Borders and focus (owner decision, 2026-10-23)

Default card and container borders are quiet, subtle, and neutral — borders are
**advisory** (decorative structure), not the primary state carrier. Keyboard focus
is the **strict**, non-negotiable signal.

- Light `--border` (`#DEE2E6`, 1.30:1 vs card) and `--input` (`#ADB5BD`, 2.07:1 vs
  card) stay below the 3:1 non-text threshold and are classified advisory. Inputs
  remain understandable without colored backgrounds: label + placeholder + border
  + focus ring carry the affordance.
- Dark `--border`/`--input` keep the committed alpha-over-surface convention
  (10% / 15% white) — quiet by construction.
- The focus indicator remains the committed geometry `focus-visible:border-ring
  focus-visible:ring-3 focus-visible:ring-ring/50`. The **full-opacity
  `border-ring` edge is the strict part**: Steel Blue at 5.30:1 (light) and ~3.4:1
  (dark `#6E9CC9` vs card) against adjacent surfaces — passing WCAG 1.4.11 in both
  themes. The 50%-alpha 3px ring is reinforcement; its halo ratios are recorded as
  advisory in the validation matrix, not relied upon.
- No heavy, high-contrast border is applied to every surface merely for visual
  consistency; there are no border-width tokens and none are added.
- Focus indicators are validated in BOTH themes (see the ledger validation
  matrix); any primitive restyle in Batch 3.2 must preserve this result.

### 2.9 Arabic typography — explicitly deferred (owner decision, 2026-10-23)

Font changes are **deferred to a separate, explicitly scoped sub-batch**. The
current Geist Sans + Geist Mono + Noto Sans Arabic setup (the D10 rail) is
unchanged in this batch: no IBM Plex Sans Arabic, no Cairo, no additional font
dependencies, and no font-loading changes. The deferral is recorded in the
progress ledger. Any future font decision requires its own authorization, a
license/delivery review, and Arabic-first readability validation on real reading
surfaces before implementation.

## 3. Consequences

* Downstream batches (3.2, 3.3, Phase 4) consume the **Light Steel** token layer —
  Steel Blue brand, neutral calm surfaces, text-grade semantics — and a documented
  state/motion/border/RTL vocabulary; tokens, never raw values.
* The indigo direction is retired. Everything that consumes `--primary` (buttons,
  badges, links, focus rings) and `--destructive`→`--error` (invalid states,
  destructive variants) moves with the token values; no component edits were made
  or needed for the migration itself.
* The minimalist semantic-feedback policy (§2.7) is binding from Batch 3.2 onward:
  no routine tinted status panels; text-first treatments; justified exceptions
  only for genuinely destructive/blocking states.
* Advisory borders + strict focus ring (§2.8) is binding: borders stay quiet in
  both themes; the focus ring must keep passing WCAG 1.4.11 as primitives are
  restyled in Batch 3.2.
* Known sub-threshold states in committed component classes (destructive hover
  tints 4.04:1 light / 3.84:1 dark; the dark 50%-alpha invalid border) are
  recorded in the ledger validation matrix and routed to Batch 3.2 — this batch
  could not and did not edit component classes.
* Typography is intentionally unchanged; the Arabic-font decision is deferred
  (§2.9) and owned by a future explicitly authorized sub-batch.
* `prefers-reduced-motion` users keep the still, fully legible interface (§2.4
  unchanged by the amendment).
* The Button/Badge icon-slot RTL defect remains explicitly assigned to Batch 3.2
  (§2.5 unchanged).
* The Section 9 hub-slot record (§2.6) is retained unchanged by the amendment:
  reservations are documentation, never rendered UI; no tokens are created for
  the slots.
* Token renames remain locked behind a new ADR; raw color literals in components
  are reviewable violations of this record.

## 4. Alternatives considered

* **Introducing dedicated interaction-state, duration, easing, and border-width
  CSS tokens now** — rejected: no consumer divergence exists to encode; the
  primitives already share one vocabulary keyed on semantic tokens, and unused
  tokens would be inventory decoration, violating the smallest-coherent-extension
  rule. Revisit only when a real consumer need appears.
* **A new palette / visual language in 3.1** — rejected at the time: D9 explicitly
  stages the intentional visual redesign on top of the stable foundation, and the
  binding batch constraints forbid inventing a palette without product-based
  evidence. **[Superseded 2026-10-23]** — the owner later commissioned exactly
  that product-based review (the Light Steel cycle) and authorized the migration;
  see §1.1, §2.1 and the amendment alternatives below.
* **Fixing the Button/Badge physical icon-slot padding in this batch** —
  rejected: it is a primitive class-string change, which is Batch 3.2's scope
  ("restyle primitives"); Batch 3.1 must not begin 3.2. Recorded instead.
* **Removing the unused `sidebar-*` tokens** — deferred: zero consumers today,
  but removal is a code-surface decision that belongs to a batch authorized to
  touch the token layer's consumers; flagged in `docs/design-tokens.md` §2.

**Amendment alternatives (2026-10-23):**

* **Keeping indigo** — superseded by the owner's explicit product decision after
  the Light Steel review cycle (the steel-blue/neutral system reads calmer and
  more content-first; the original rejection was a baseline-time stance and
  remained reversible by the owner, who has now exercised that authority).
* **The reviewed proposal's per-status tinted surface tiers
  (`-soft`/`-on-soft`/`-border`)** — rejected by the owner: routine tinted panels
  are precisely the heavy semantic styling the minimalist policy removes; the
  two-tier `--*`/`--*-foreground` set is retained instead.
* **Strict 3:1 borders on inputs** — rejected in favor of advisory borders:
  WCAG 1.4.11 covers *essential* boundaries; inputs carry label + placeholder +
  focus, and the strict signal is the focus ring. Pre-computed strict
  alternatives (`#7E8892` light) remain documented in the review artifacts if the
  owner revisits.
* **Immediate Arabic font migration (IBM Plex Sans Arabic / Cairo)** — deferred
  by the owner to a separately scoped sub-batch (§2.9) instead of bundling it
  into this token migration.
* **Implementing the proposal's convenience tokens (`--selected`, `--link`,
  `--placeholder`, `--overlay`, `--tooltip-*`, hover steps)** — not created:
  zero consumers today; §2.3 rule 3 requires a demonstrated consumer need. The
  batches that build those consumers decide them with documentation and parity.
