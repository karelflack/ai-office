# AI Office — Visual Design Direction & Wireframes

**Agent:** ingrid
**Date:** 2026-03-30
**Project:** AI Office marketing landing page

---

## Context Note

AI Office is an **LLM API proxy with semantic prompt caching**. It sits between your application and the LLM provider, caches identical and semantically similar prompts, and returns stored responses without making new API calls. The primary value prop is cost reduction (40–80% in month one). The audience is CTOs and engineering leads. Copy is from Jorunn; tech stack (Astro + Tailwind + Vercel + Motion One) is from Bjorn.

---

## 1. Design Direction Brief

### Philosophy

Minimal, data-forward, and precise. The design signals trust to a technical buyer who has seen every SaaS landing page and distrusts anything decorative. Inspired by Linear, Vercel dashboard, and Stripe — built dark-mode first. Space and type do the heavy lifting. The numbers are the hero.

No glassmorphism. No illustration. Earn every visual element.

---

### Color Palette

| Role | Token | Hex | Usage |
|------|-------|-----|-------|
| Background | `bg-base` | `#0A0A0F` | Page background |
| Surface | `bg-surface` | `#111118` | Cards, panels |
| Surface raised | `bg-surface-raised` | `#16161F` | Hover states, elevated cards |
| Border subtle | `border-subtle` | `#1E1E2E` | Dividers, card outlines |
| Border active | `border-active` | `#2D2D42` | Focused/hover borders |
| Primary | `indigo-500` | `#6366F1` | CTAs, links, active states |
| Primary hover | `indigo-400` | `#818CF8` | Button hover |
| Primary glow | — | `rgba(99,102,241,0.12)` | Radial glow behind hero mockup |
| Text primary | `text-primary` | `#F1F1FA` | Headlines, strong body |
| Text secondary | `text-secondary` | `#94A3B8` | Body copy, captions |
| Text muted | `text-muted` | `#4B5563` | Metadata, footnotes, stat labels |
| Accent green | `emerald-500` | `#10B981` | Cache hit indicators, live stat dots |
| Accent amber | `amber-400` | `#FBBF24` | Savings highlight numbers in stat bar |

**Light mode:** Background → `#FFFFFF`, surface → `#F9FAFB`, border → `#E5E7EB`. Primary remains `#6366F1`. Text primary → `#0A0A0F`. Provide via CSS `prefers-color-scheme: light` or Tailwind `dark:` classes.

---

### Typography

All Google Fonts. Configured in `tailwind.config.ts` under `theme.extend.fontFamily`.

| Role | Font | Weight(s) | Tailwind |
|------|------|-----------|----------|
| Display / Hero | **Geist** (fallback: Inter) | 700, 800 | `font-display` |
| Headings | **Inter** | 600, 700 | `font-sans` |
| Body | **Inter** | 400, 500 | `font-sans` |
| Labels / Badges | **Inter** | 500, 600 | `font-sans` |
| Code / Mono | **JetBrains Mono** | 400 | `font-mono` |

**Size scale in use:**

| Context | Tailwind | px |
|---------|----------|----|
| Hero headline | `text-6xl lg:text-7xl` | 60–72px |
| Section headline | `text-3xl lg:text-4xl` | 30–36px |
| Feature card title | `text-xl` | 20px |
| Body copy | `text-base lg:text-lg` | 16–18px |
| Badge / label | `text-xs sm:text-sm` | 12–14px |
| Code snippet | `text-sm` | 14px |

**Letter spacing:** `-0.025em` on display/hero (`tracking-tight`). Normal on body.
**Line height:** `leading-tight` (1.2) for headlines. `leading-relaxed` (1.625) for body.

---

### Spacing Scale (Tailwind-compatible)

Base unit: `4px`

| Name | px | Tailwind |
|------|----|----------|
| xs | 4 | `p-1` |
| sm | 8 | `p-2` |
| md | 16 | `p-4` |
| lg | 24 | `p-6` |
| xl | 32 | `p-8` |
| 2xl | 48 | `p-12` |
| 3xl | 64 | `p-16` |
| 4xl | 96 | `p-24` |
| 5xl | 128 | `p-32` |

Section vertical padding: `py-24` desktop, `py-16` mobile.
Container: `max-w-6xl mx-auto px-6`.

---

### Component Style

**Approach:** Fine borders on dark surfaces. No drop shadows — use border and background contrast instead. Indigo reserved for primary actions and key data highlights. Motion One scroll animations only — no hover scale effects.

| Component | Style |
|-----------|-------|
| **Button — primary** | `bg-indigo-500 hover:bg-indigo-400 text-white font-medium rounded-lg px-5 py-2.5 transition-colors duration-150` |
| **Button — ghost** | `border border-[#1E1E2E] hover:border-[#2D2D42] hover:bg-[#16161F] text-primary rounded-lg px-5 py-2.5 transition-colors duration-150` |
| **Feature card** | `bg-[#111118] border border-[#1E1E2E] rounded-xl p-6 hover:border-[#2D2D42] transition-colors duration-150` |
| **Badge / pill** | `bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 rounded-full text-xs font-medium px-3 py-1` |
| **Nav bar** | `sticky top-0 h-14 backdrop-blur-md bg-[#0A0A0F]/80 border-b border-[#1E1E2E]` |
| **Stat number** | `text-amber-400 font-bold text-3xl` + `text-muted text-sm` label below |
| **Code block** | `bg-[#16161F] border border-[#1E1E2E] rounded-lg font-mono text-sm text-emerald-400 px-4 py-3` |
| **Logo favicon mark** | Geometric, single-color-capable, readable at 16×16px — no wordmark at small sizes |

**Icons:** Lucide — stroke `1.5`, inline `20px`, feature `24px`.

---

## 2. Wireframes

Notation:
- `[COPY: ...]` = exact copy from Jorunn's deliverable
- `[IMG]` = image or screenshot asset
- `[BTN]` = interactive button
- `···` = repeated pattern

---

### 2.1 Navigation Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [icon mark]  AI Office        [Docs]   [Pricing]   [GitHub]   [Sign in]   │
│                                                         [→ Start saving now]│
└─────────────────────────────────────────────────────────────────────────────┘
```

- Full-width sticky, `h-14`
- Left: logo mark (geometric icon, 20px) + wordmark `font-medium`
- Center: nav links `text-sm text-secondary hover:text-primary`
- Right: ghost "Sign in" + primary CTA "Start saving now"
- Frosted blur on scroll

**Mobile:** Logo left. Hamburger right. Drawer with stacked links + primary CTA at bottom.

---

### 2.2 Hero Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                  ┌──────────────────────────────────┐                      │
│                  │  ✦  Now in public beta            │  ← indigo pill badge │
│                  └──────────────────────────────────┘                      │
│                                                                             │
│                 Stop paying for the                                         │
│                 same prompt twice.                                          │
│                                                                             │
│      AI Office caches your LLM API calls — so repeated and                  │
│      semantically similar prompts return instantly, without                 │
│      a new API charge. Most teams cut their LLM costs                       │
│      by 40–80% in the first month.                                          │
│                                                                             │
│              [→ Start saving now]      [See how it works]                   │
│                                                                             │
│       ─────────────────────────────────────────────────                    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                                                                 │      │
│   │   ┌────────────────────────────────────────────────────────┐   │      │
│   │   │  $ curl https://api.aioffice.dev/v1/chat/completions  │   │      │
│   │   │    -H "Authorization: Bearer $API_KEY"                 │   │      │
│   │   │    ...                                                  │   │      │
│   │   │                                                         │   │      │
│   │   │  ← 200 OK  ● Cache hit  ↩ 4ms  Saved: $0.024          │   │      │
│   │   └────────────────────────────────────────────────────────┘   │      │
│   │                                                                 │      │
│   │   [Dashboard chart: cost over time, showing drop after deploy] │      │
│   │                                                                 │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** Single column, center-aligned, `max-w-3xl` for text, `max-w-5xl` for mockup.
**Headline:** `text-6xl lg:text-7xl font-bold tracking-tight`; desktop 2 lines, mobile wraps to 3.
**Subheadline:** `text-lg lg:text-xl text-secondary max-w-2xl mx-auto leading-relaxed`.
**Buttons:** `flex gap-4 justify-center` desktop; `flex-col items-center` mobile.
**Mockup:** Terminal/dashboard preview image. `rounded-2xl border border-[#1E1E2E]`. Radial indigo glow behind: `bg-[radial-gradient(ellipse_at_center,_rgba(99,102,241,0.12)_0%,_transparent_70%)]`.
**Animation (Motion One):** Badge fades in first; headline fades + translates up 6px (150ms delay); subheadline (250ms); buttons (350ms); mockup (500ms).

---

### 2.3 Stats Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    40–80%           4ms            200M+             500+                  │
│  avg cost         cache hit     cached responses   engineering teams       │
│  reduction        latency          served           in production          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `grid-cols-4` desktop; `grid-cols-2` mobile.
**Numbers:** `text-3xl font-bold text-amber-400`.
**Labels:** `text-sm text-muted mt-1`.
**Dividers:** `border-t border-b border-[#1E1E2E]`.
**Note:** Use `[X]` placeholders per Jorunn's copy — real numbers from the product team fill these at launch.

---

### 2.4 Features Section — Card Grid

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│               How AI Office works                                           │
│                                                                             │
│  ┌───────────────────────────┐  ┌──────────────────────────┐  ┌──────────┐ │
│  │                           │  │                          │  │          │ │
│  │  [icon: git-merge]        │  │  [icon: brain]           │  │ [icon:   │ │
│  │                           │  │                          │  │  eye]    │ │
│  │  A proxy that sits        │  │  Exact matches are easy. │  │          │ │
│  │  between your app and     │  │  We catch the near-      │  │  Full    │ │
│  │  the LLM. Nothing to      │  │  misses too.             │  │  observa-│ │
│  │  rip out.                 │  │                          │  │  bility. │ │
│  │                           │  │                          │  │  You     │ │
│  │  Point your existing API  │  │  Most caching systems    │  │  decide  │ │
│  │  calls at AI Office. No   │  │  only match identical    │  │  what    │ │
│  │  SDK changes, no model    │  │  strings. AI Office uses │  │  gets    │ │
│  │  switching...             │  │  semantic similarity...  │  │  cached. │ │
│  │                           │  │                          │  │          │ │
│  └───────────────────────────┘  └──────────────────────────┘  └──────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6`.
**Cards:** `bg-[#111118] border border-[#1E1E2E] rounded-xl p-6 hover:border-[#2D2D42] transition-colors`.
**Icon container:** `w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-4`.
**Title:** `text-xl font-semibold text-primary mb-3`.
**Body:** `text-base text-secondary leading-relaxed`.
**Section intro:** `text-sm font-medium text-indigo-400 uppercase tracking-wide mb-3` label above heading.

**Animation (Motion One):** Cards fade-in + slide-up 8px on scroll entry, staggered 80ms per card.

---

### 2.5 Feature Deep Dive — Alternating Rows

Used to expand each of the 3 features with more detail, a screenshot or diagram, and bullet proof-points.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────────────────────────┐  ┌───────────────────────────────┐   │
│  │                                  │  │                               │   │
│  │  [PROXY DIAGRAM: app → AI Office │  │  A proxy that sits between    │   │
│  │   → LLM, with cache hit path     │  │  your app and the LLM.        │   │
│  │   shown as bypass arrow]         │  │  Nothing to rip out.          │   │
│  │                                  │  │                               │   │
│  │                                  │  │  Point your existing API      │   │
│  │                                  │  │  calls at AI Office. No SDK   │   │
│  │                                  │  │  changes, no model switching, │   │
│  │                                  │  │  no migration...              │   │
│  │                                  │  │                               │   │
│  │                                  │  │  ✓ Setup in under 10 minutes  │   │
│  │                                  │  │  ✓ Works with any LLM provider│   │
│  │                                  │  │  ✓ Your team doesn't need to  │   │
│  │                                  │  │    know it's there            │   │
│  │                                  │  │                               │   │
│  └──────────────────────────────────┘  └───────────────────────────────┘   │
│                                                                             │
│  ┌───────────────────────────────┐  ┌──────────────────────────────────┐   │
│  │                               │  │                                  │   │
│  │  Exact matches are easy.      │  │  [SIMILARITY DIAGRAM: prompt     │   │
│  │  We catch the near-misses too.│  │   variants → embedding space →   │   │
│  │                               │  │   cache hit]                     │   │
│  │  Most caching systems only    │  │                                  │   │
│  │  match identical strings...   │  │                                  │   │
│  │                               │  │                                  │   │
│  │  ✓ Rephrased queries          │  │                                  │   │
│  │  ✓ Variant inputs             │  │                                  │   │
│  │  ✓ User-generated text        │  │                                  │   │
│  │                               │  │                                  │   │
│  └───────────────────────────────┘  └──────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌───────────────────────────────┐   │
│  │                                  │  │                               │   │
│  │  [DASHBOARD SCREENSHOT: cache    │  │  Full observability.          │   │
│  │   hit rate chart, cost savings   │  │  You decide what gets cached  │   │
│  │   graph, per-endpoint table]     │  │  and what doesn't.            │   │
│  │                                  │  │                               │   │
│  │                                  │  │  Every request is logged...   │   │
│  │                                  │  │                               │   │
│  │                                  │  │  ✓ Cache hits/misses/savings  │   │
│  │                                  │  │  ✓ TTL controls per route     │   │
│  │                                  │  │  ✓ Similarity thresholds      │   │
│  │                                  │  │  ✓ Exclude sensitive prompts  │   │
│  │                                  │  │                               │   │
│  └──────────────────────────────────┘  └───────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `grid grid-cols-1 lg:grid-cols-2 gap-16 items-center`. Row 1 + Row 3: image left, text right. Row 2: text left, image right.
**Mobile:** Always `grid-cols-1`; image above text regardless of desktop order. Use `order-first lg:order-none` on image for rows where desktop shows text first.
**Checkmarks:** `text-emerald-500` Lucide `check` icon inline before list items.
**Diagrams / screenshots:** `rounded-2xl border border-[#1E1E2E]` asset containers.

---

### 2.6 Social Proof — Logos Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    border-t border-[#1E1E2E]                                │
│                                                                             │
│            Trusted by engineering teams moving fast on AI                   │
│                                                                             │
│   [Logo 1]    [Logo 2]    [Logo 3]    [Logo 4]    [Logo 5]    [Logo 6]     │
│                                                                             │
│                    border-b border-[#1E1E2E]                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `flex flex-wrap justify-center items-center gap-10 lg:gap-16`.
**Logos:** SVG, `opacity-40 hover:opacity-65 transition-opacity grayscale`. White/light treatment on dark background.
**Label:** `text-sm text-muted text-center mb-10`.

---

### 2.7 Testimonials

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────────────────────────┐  ┌───────────────────────────┐   │
│  │                                     │  │                           │   │
│  │  "We were spending $X on LLM calls  │  │  "The semantic matching   │   │
│  │   every month. After deploying      │  │   was the differentiator  │   │
│  │   AI Office, that dropped to $Y     │  │   for us. AI Office       │   │
│  │   within four weeks."               │  │   caught 60% of our       │   │
│  │                                     │  │   calls."                 │   │
│  │  [avatar]  Name                     │  │                           │   │
│  │            Title, Company           │  │  [avatar]  Name           │   │
│  │                                     │  │            Title, Company │   │
│  └─────────────────────────────────────┘  └───────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `grid grid-cols-1 md:grid-cols-2 gap-6`.
**Card:** `bg-[#111118] border border-[#1E1E2E] rounded-xl p-6`.
**Quote:** `text-base text-primary leading-relaxed mb-6` — no italic (too informal for this tone).
**Avatar:** `w-8 h-8 rounded-full bg-[#1E1E2E]` placeholder; `text-sm font-medium text-primary`, `text-xs text-muted` role.

---

### 2.8 Closing CTA Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │           Your LLM bill is predictable.                               │ │
│  │           Your engineering time is not.                               │ │
│  │                                                                       │ │
│  │     AI Office handles cost optimization at the infrastructure         │ │
│  │     layer so your team doesn't have to. Deploy once.                  │ │
│  │     Reduce costs continuously.                                        │ │
│  │                                                                       │ │
│  │              [→ Get started free]      [Talk to an engineer]          │ │
│  │                                                                       │ │
│  │         No credit card required  ·  Works with any LLM provider       │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** Full container width. Panel: `bg-[#111118] border border-[#1E1E2E] rounded-2xl p-12 lg:p-16`. Center-aligned content.
**Headline:** `text-4xl lg:text-5xl font-bold tracking-tight`.
**Body:** `text-lg text-secondary max-w-2xl mx-auto mt-4 mb-8 leading-relaxed`.
**Buttons:** `flex flex-col sm:flex-row justify-center gap-4`.
**Fine print:** `text-xs text-muted mt-4`.
**Optional glow:** Faint indigo radial glow behind panel for final visual emphasis — use sparingly.

---

### 2.9 Footer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    border-t border-[#1E1E2E]                                │
│                                                                             │
│  [icon] AI Office          Product        Company       Legal              │
│                                                                             │
│  © 2026 AI Office          Docs           About         Privacy policy     │
│  All rights reserved.      Pricing        Blog          Terms of service   │
│                            Changelog      Careers       Security           │
│  [x/twitter] [github]      Status         Contact                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `grid grid-cols-2 lg:grid-cols-4 gap-10` — logo column + 3 link columns.
**Links:** `text-sm text-secondary hover:text-primary transition-colors`.
**Brand column:** Logo mark + wordmark. Copyright + social icons below.
**Social:** `text-muted hover:text-secondary` Lucide icons, `20px`.
**Mobile:** `grid-cols-1` — brand block full width, then 3 link columns in `grid-cols-2` sub-grid.

---

## 3. Responsive Behavior Reference

### Breakpoints

| Breakpoint | Width | Notes |
|------------|-------|-------|
| Base (mobile) | < 640px | Single column, reduced font sizes, stacked CTAs |
| `sm` | 640px+ | 2-col grids begin, buttons side-by-side |
| `md` | 768px+ | Testimonials 2-col, nav fully visible |
| `lg` | 1024px+ | Full desktop layouts, 3-col features, alternating rows |

### Key responsive rules per section

**Hero headline:**
`text-5xl sm:text-6xl lg:text-7xl` — reduce to 3 lines on mobile.

**Dashboard mockup:**
`w-full max-w-5xl mx-auto` — full width on mobile, capped on desktop. Ensure border-radius matches at all sizes.

**Stats bar:**
`grid-cols-2 lg:grid-cols-4` — 4 stats wrap to 2×2 on mobile.

**Feature card grid:**
`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` — single column on mobile to give each card room to breathe.

**Alternating rows:**
`grid-cols-1 lg:grid-cols-2` — always stack on mobile, image always first. Use `order-first lg:order-none` for rows that are image-right on desktop.

**Logo bar:**
`flex-wrap gap-8 sm:gap-12` — logos wrap freely; never clip.

**CTA panel:**
`rounded-none sm:rounded-2xl` — full bleed on mobile for visual impact, rounded only on tablet+.

**Footer:**
`grid-cols-1` brand block, then `grid-cols-2` for link columns on mobile. Full `grid-cols-4` on `lg`.

---

## 4. Animation Notes (Motion One)

All animations respect `prefers-reduced-motion: reduce`.

| Element | Animation | Delay |
|---------|-----------|-------|
| Hero badge | `opacity: [0, 1]` + `y: [4, 0]` | 0ms |
| Hero headline | `opacity: [0, 1]` + `y: [8, 0]` | 100ms |
| Hero subheadline | `opacity: [0, 1]` + `y: [8, 0]` | 200ms |
| Hero buttons | `opacity: [0, 1]` | 300ms |
| Dashboard mockup | `opacity: [0, 1]` on scroll enter | 0ms (scroll trigger) |
| Stats bar numbers | Count-up from 0 on scroll enter | staggered 80ms |
| Feature cards | `opacity: [0, 1]` + `y: [12, 0]` on scroll enter | staggered 80ms |
| Alternating row blocks | `opacity: [0, 1]` + `y: [8, 0]` on scroll enter | 0ms |
| CTA panel | `opacity: [0, 1]` + `y: [8, 0]` on scroll enter | 0ms |

**Durations:** 300ms for UI element fades; 500ms for larger sections. Easing: `ease-out`.
**No scale effects.** No parallax. No continuous animations (no spinners, no looping).

---

## 5. Logo / Favicon Mark Notes

Per Jorunn's brand notes: the name "AI Office" must not rely solely on the wordmark. A standalone geometric icon is required that works at 16×16px.

**Recommendation:** A single glyph — e.g., a stylised `[/]` or `{◦}` or a simple grid-of-dots mark — that reads as "structured intelligence." Single-color capable. Works white-on-dark and dark-on-white.

**What to avoid:** Anything that looks like the Microsoft Office grid of squares. Any organic shape. Any multi-color treatment at small sizes.

The icon should be designed as an SVG with a single path, optimisable to ~200 bytes. Arve will need it as an `.svg` file in `public/` for the Astro build.

---

## 6. Copy → Wireframe Mapping

| Wireframe section | Jorunn's copy |
|-------------------|---------------|
| Hero badge | "Now in public beta" (or launch label TBD) |
| Hero headline | "Stop paying for the same prompt twice." |
| Hero subheadline | Full paragraph from hero section |
| Hero CTA primary | "Start saving now" |
| Hero CTA secondary | "See how it works" |
| Stats bar | `[X]%`, `[X]ms`, `[X]M+`, `[X]+` placeholders |
| Feature 1 card title | "A proxy that sits between your app and the LLM. Nothing to rip out." |
| Feature 2 card title | "Exact matches are easy. We catch the near-misses too." |
| Feature 3 card title | "Full observability. You decide what gets cached and what doesn't." |
| Social proof label | "Trusted by engineering teams moving fast on AI" |
| Testimonial 1 | Placeholder quote 1 (cost reduction) |
| Testimonial 2 | Placeholder quote 2 (semantic matching) |
| CTA headline | "Your LLM bill is predictable. Your engineering time is not." |
| CTA body | "AI Office handles cost optimization..." + "Deploy once. Reduce costs continuously." |
| CTA primary | "Get started free" |
| CTA secondary | "Talk to an engineer" |

---

*Deliverable by Ingrid — visual design direction and wireframes for AI Office landing page.*
*Aligns with: Jorunn's brand/copy (2026-03-30), Bjorn's tech stack ADR (2026-03-30).*
