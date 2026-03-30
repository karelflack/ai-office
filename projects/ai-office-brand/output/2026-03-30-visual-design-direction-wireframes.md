# AI Office — Visual Design Direction & Wireframes

**Agent:** ingrid
**Date:** 2026-03-30
**Project:** AI Office marketing landing page

---

## 1. Design Direction Brief

### Philosophy

Minimal, data-forward, and confident. The design should feel like the product: intelligent and precise without being cold. Inspired by Linear, Vercel dashboard, and Stripe — built on dark mode first, with space for the product to breathe.

No glassmorphism. No gradients for the sake of it. Earn every visual element.

---

### Color Palette

| Role | Token | Hex | Usage |
|------|-------|-----|-------|
| Background | `bg-base` | `#0A0A0F` | Page background |
| Surface | `bg-surface` | `#111118` | Cards, panels |
| Surface raised | `bg-surface-raised` | `#16161F` | Hover states, elevated cards |
| Border | `border-subtle` | `#1E1E2E` | Dividers, card outlines |
| Border active | `border-active` | `#2D2D42` | Focused/hover borders |
| Primary | `indigo-500` | `#6366F1` | CTAs, links, active states |
| Primary hover | `indigo-400` | `#818CF8` | Button hover |
| Primary glow | — | `rgba(99,102,241,0.15)` | Subtle glow on hero badge, buttons |
| Text primary | `text-primary` | `#F1F1FA` | Headlines, strong body |
| Text secondary | `text-secondary` | `#94A3B8` | Body copy, captions |
| Text muted | `text-muted` | `#4B5563` | Metadata, footnotes |
| Accent green | `emerald-500` | `#10B981` | Success states, "live" indicators |

**Light mode:** Invert base (`#FFFFFF`), surface (`#F9FAFB`), border (`#E5E7EB`). Primary remains `#6366F1`. Text primary becomes `#0A0A0F`.

---

### Typography

All fonts are Google Fonts. Tailwind-compatible via `font-sans` / `font-mono`.

| Role | Font | Weight(s) | Size scale |
|------|------|-----------|------------|
| Display / Hero | **Geist** (or Inter fallback) | 700, 800 | `text-5xl` → `text-7xl` |
| Headings | **Inter** | 600, 700 | `text-2xl` → `text-4xl` |
| Body | **Inter** | 400, 500 | `text-base` (`16px`), `text-lg` (`18px`) |
| Labels / Badges | **Inter** | 500, 600 | `text-xs` → `text-sm` |
| Code / Mono | **JetBrains Mono** | 400 | `text-sm` |

**Line height:** `leading-tight` (1.2) for display; `leading-relaxed` (1.625) for body.
**Letter spacing:** `-0.02em` for display headings (feels tight and deliberate); normal for body.

---

### Spacing Scale (Tailwind-compatible)

Base unit: `4px`

| Token | px | Tailwind |
|-------|----|----------|
| xs | 4 | `p-1` |
| sm | 8 | `p-2` |
| md | 16 | `p-4` |
| lg | 24 | `p-6` |
| xl | 32 | `p-8` |
| 2xl | 48 | `p-12` |
| 3xl | 64 | `p-16` |
| 4xl | 96 | `p-24` |
| 5xl | 128 | `p-32` |

Section padding: `py-24` desktop, `py-16` mobile.
Container max-width: `max-w-6xl` with `px-6`.

---

### Component Style

**Style:** Minimal dark with fine borders and selective indigo glow accents. No gradients on surfaces. No shadows — use borders instead. Occasional radial glow behind the hero dashboard mockup.

| Component | Style notes |
|-----------|-------------|
| Buttons (primary) | `bg-indigo-500`, `rounded-lg`, `px-5 py-2.5`, `text-white font-medium`, hover: `bg-indigo-400` |
| Buttons (secondary/ghost) | `border border-[#1E1E2E]`, `bg-transparent`, hover: `bg-surface-raised` |
| Cards / Feature tiles | `bg-surface`, `border border-[#1E1E2E]`, `rounded-xl`, `p-6` |
| Badge / Pill | `bg-[rgba(99,102,241,0.1)] border border-[rgba(99,102,241,0.3)]`, `text-indigo-400`, `rounded-full`, `text-xs font-medium px-3 py-1` |
| Nav | Sticky, `bg-[rgba(10,10,15,0.8)] backdrop-blur`, `border-b border-[#1E1E2E]` |
| Divider | `border-t border-[#1E1E2E]` |
| Input | `bg-surface`, `border border-[#1E1E2E]`, `rounded-lg`, focus: `border-indigo-500 ring-1 ring-indigo-500/20` |

**Icons:** Lucide React — stroke weight `1.5`, size `20px` inline / `24px` feature icons.

---

## 2. Wireframes

Notation key:
- `[TEXT]` = copy placeholder
- `[IMG]` = image or illustration asset
- `[BTN]` = interactive button
- `···` = implied repetition
- Columns separated by `|`

---

### 2.1 Navigation Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [logo icon] AI Office          [Features]  [Pricing]  [Docs]  [Sign in]   │
│                                                              [→ Get started] │
└─────────────────────────────────────────────────────────────────────────────┘
```

- Sticky, full-width, `h-14`
- Logo left-aligned; nav links centered (desktop) or hidden behind hamburger (mobile)
- Primary CTA button right-aligned, always visible
- Background: frosted blur on scroll — `backdrop-blur-md bg-[#0A0A0F]/80`

**Mobile:** Hamburger menu reveals full-screen drawer with stacked nav links + CTA.

---

### 2.2 Hero Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    ┌─────────────────────────┐                             │
│                    │ ✦ Now in public beta     │  ← indigo pill badge        │
│                    └─────────────────────────┘                             │
│                                                                             │
│              Your entire office,                                            │
│              run by AI.                                                     │
│                                                                             │
│         AI agents for every role. One platform.                             │
│         No headcount required.                                              │
│                                                                             │
│              [→ Start for free]    [Watch the demo  ▶]                     │
│                                                                             │
│         ─────────────────────────────────────────────                      │
│                                                                             │
│    ┌────────────────────────────────────────────────────────────────┐      │
│    │                                                                │      │
│    │          [PRODUCT DASHBOARD MOCKUP / SCREENSHOT]               │      │
│    │                                                                │      │
│    │   ┌──────────────┐  ┌─────────────────┐  ┌───────────────┐   │      │
│    │   │  Agent: Arve │  │  Agent: Ingrid  │  │  Agent: Else  │   │      │
│    │   │  ● Working   │  │  ● Reviewing    │  │  ● Standby    │   │      │
│    │   └──────────────┘  └─────────────────┘  └───────────────┘   │      │
│    │                                                                │      │
│    └────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** Single column, center-aligned text, max-width `max-w-3xl` for headline, `max-w-5xl` for mockup.
**Headline:** `text-6xl font-bold tracking-tight` (desktop); `text-4xl` (mobile).
**Subheadline:** `text-xl text-secondary` (desktop); `text-lg` (mobile).
**Mockup:** Rounded corners (`rounded-2xl`), `border border-[#1E1E2E]`, subtle radial glow behind in indigo (`bg-radial-gradient(indigo-500/5)`).
**Button gap:** `gap-4`, buttons side-by-side (desktop), stacked (mobile).

---

### 2.3 Features Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                  How AI Office works                                        │
│              [One platform. Every role. Always on.]                         │
│                                                                             │
│  ┌────────────────────────┐  ┌────────────────────────┐  ┌───────────────┐ │
│  │                        │  │                        │  │               │ │
│  │  [icon: cpu]           │  │  [icon: users]         │  │  [icon: bolt] │ │
│  │                        │  │                        │  │               │ │
│  │  Agents for every role │  │  Works as a team       │  │  Always on    │ │
│  │                        │  │                        │  │               │ │
│  │  [body copy: 2-3 lines │  │  [body copy: 2-3 lines │  │  [body copy:  │ │
│  │   describing the feat] │  │   describing the feat] │  │   2-3 lines]  │ │
│  │                        │  │                        │  │               │ │
│  │  [→ Learn more]        │  │  [→ Learn more]        │  │  [→ Learn more│ │
│  └────────────────────────┘  └────────────────────────┘  └───────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** 3-column grid (`grid-cols-3`) desktop; `grid-cols-1` mobile.
**Cards:** `bg-surface border border-[#1E1E2E] rounded-xl p-6`; hover: `border-[#2D2D42]` with subtle transition.
**Icon:** `24px` Lucide icon in indigo `text-indigo-400`, inside a `rounded-lg bg-indigo-500/10 w-10 h-10 flex items-center justify-center` container.
**Card link:** Ghost text link `text-sm text-indigo-400 hover:text-indigo-300`.

---

### 2.4 Deep Feature — Alternating Row Layout (optional expansion)

If 3 features need more breathing room, use an alternating text/image layout below the card grid:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌──────────────────────────────┐     ┌────────────────────────────────┐  │
│   │                              │     │                                │  │
│   │  [FEATURE SCREENSHOT / GIF] │     │  Feature title                 │  │
│   │                              │     │                                │  │
│   │                              │     │  [Body copy — 3-4 sentences]   │  │
│   │                              │     │                                │  │
│   └──────────────────────────────┘     │  ✓ Bullet point 1              │  │
│                                        │  ✓ Bullet point 2              │  │
│                                        │  ✓ Bullet point 3              │  │
│                                        │                                │  │
│                                        │  [→ See how it works]          │  │
│                                        └────────────────────────────────┘  │
│                                                                             │
│   ┌────────────────────────────────┐   ┌──────────────────────────────┐    │
│   │  Feature title (reversed)      │   │                              │    │
│   │  ...                           │   │  [FEATURE SCREENSHOT / GIF]  │    │
│   └────────────────────────────────┘   └──────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `grid-cols-2 gap-16 items-center` — alternates image left/right per row.
**Mobile:** Stack vertically, image always above text.

---

### 2.5 Social Proof — Logos Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              Trusted by teams building what's next                          │
│                                                                             │
│   [Logo 1]    [Logo 2]    [Logo 3]    [Logo 4]    [Logo 5]    [Logo 6]     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** Single row, `flex justify-center items-center gap-12 flex-wrap`.
**Logos:** Rendered in `opacity-40`, hover: `opacity-70`. Monochrome white treatment.
**Label:** `text-sm text-muted text-center mb-8`.
**Divider:** `border-t border-[#1E1E2E]` above and below this section.

---

### 2.6 Testimonials (optional — placeholder block)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│              What teams say                                                 │
│                                                                             │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │ "Quote from user. Short,        │  │ "Quote from user. Short,        │  │
│  │  punchy, specific."             │  │  punchy, specific."             │  │
│  │                                 │  │                                 │  │
│  │  [avatar]  Name, Role @ Co.     │  │  [avatar]  Name, Role @ Co.     │  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** 2-column grid desktop; single column mobile.
**Card:** `bg-surface border border-[#1E1E2E] rounded-xl p-6`.
**Quote text:** `text-base text-primary italic leading-relaxed`.
**Attribution:** `flex items-center gap-3 mt-4` — avatar `w-8 h-8 rounded-full`, name `text-sm font-medium`, role `text-xs text-muted`.

---

### 2.7 CTA Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │              Your team is waiting.                                  │  │
│   │                                                                     │  │
│   │       Hire your first AI agent today — free to start.              │  │
│   │                                                                     │  │
│   │              [→ Get started free]    [Talk to us]                  │  │
│   │                                                                     │  │
│   │         No credit card required · Cancel any time                  │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** Full-width `bg-surface` panel with `rounded-2xl border border-[#1E1E2E]`, inside standard container. Center-aligned.
**Headline:** `text-4xl font-bold` (desktop); `text-3xl` (mobile).
**Sub-copy:** `text-lg text-secondary`.
**Buttons:** Side-by-side, primary + ghost. Stack on mobile.
**Fine print:** `text-xs text-muted mt-3`.
**Optional:** Faint indigo radial glow behind the panel for visual emphasis.

---

### 2.8 Footer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  [logo] AI Office              Product      Company      Legal             │
│  © 2026 AI Office                                                           │
│  All rights reserved.         [Features]   [About]      [Privacy]          │
│                               [Pricing]    [Blog]       [Terms]            │
│  [twitter] [github]           [Docs]       [Careers]    [Security]         │
│                               [Changelog]  [Contact]                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layout:** `grid-cols-4` desktop — logo/legal left, 3 link columns right. `grid-cols-2` tablet. `grid-cols-1` mobile (stacked).
**Links:** `text-sm text-secondary hover:text-primary`.
**Social icons:** Lucide icons, `20px`, `text-muted hover:text-secondary`.
**Divider:** `border-t border-[#1E1E2E] mb-12` above footer content.

---

## 3. Responsive Behavior Notes

### Breakpoints (Tailwind standard)

| Breakpoint | Width | Behavior |
|------------|-------|----------|
| Mobile | < 640px (`sm`) | Single column. Buttons stacked. Nav collapses to hamburger. Reduced font sizes. |
| Tablet | 640–1024px (`md`) | 2-column grids. Nav visible but compact. |
| Desktop | > 1024px (`lg`) | Full layouts as wireframed above. |

### Key responsive rules

**Hero:**
- Headline: `text-5xl md:text-6xl lg:text-7xl`
- Buttons: `flex-col sm:flex-row`
- Dashboard mockup: full width on mobile, `max-w-5xl` centered on desktop

**Features (3-column card grid):**
- `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
- Cards maintain consistent padding at all breakpoints (`p-6`)

**Alternating feature rows:**
- `grid-cols-1 lg:grid-cols-2`
- On mobile: image first, then text (regardless of desktop order)
- Use `order-first lg:order-none` to control image position per row

**Logo bar:**
- `flex-wrap justify-center` — logos wrap to 2–3 rows on small screens
- Reduce gap: `gap-8 sm:gap-12`

**CTA panel:**
- Full viewport width on mobile (no horizontal margin)
- `rounded-none sm:rounded-2xl`

**Footer:**
- `grid-cols-2 lg:grid-cols-4`
- Logo and copyright span full width on mobile above link columns

---

## 4. Animation & Motion Notes

Keep motion minimal and purposeful. No auto-play animations. Respect `prefers-reduced-motion`.

| Element | Animation |
|---------|-----------|
| Hero badge | Fade in + subtle upward translate on load (`opacity-0 → opacity-100`, `translateY(4px) → 0`) |
| Hero headline | Staggered fade-in, 100ms delay after badge |
| Dashboard mockup | Fade in on scroll enter (Intersection Observer, 200ms delay) |
| Feature cards | Fade up on scroll into view, staggered 80ms per card |
| CTA panel | Fade in on scroll |
| Buttons | `transition-colors duration-150` only — no scale effects |

**Library:** CSS transitions + minimal JS Intersection Observer. No heavy animation library unless Bjorn selects Framer Motion in the tech stack ADR.

---

## 5. Copy Section Mapping

The wireframes above map to Jorunn's expected homepage copy sections:

| Wireframe section | Expected copy |
|-------------------|---------------|
| Hero badge | Short launch / beta label |
| Hero headline + subheadline | Primary value proposition |
| Features (3 cards) | Feature 1, 2, 3 headers + body |
| Alternating rows | Expanded feature details (if used) |
| Logo bar label | Social proof intro text |
| CTA headline | Closing value statement |
| CTA sub-copy | Friction-reducing reassurance |
| CTA buttons | Primary CTA text + secondary CTA text |
| Footer | Product / company / legal link labels |

---

*Deliverable by Ingrid — visual design direction and wireframes for AI Office landing page.*
