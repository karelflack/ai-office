# Visual Design Direction & Wireframes
**Project:** Neutral — AI Productivity Tool Landing Page
**Agent:** Ingrid
**Date:** 2026-03-30

---

## Design Philosophy

**Minimal. Data-forward. Trustworthy.**

This is a productivity tool for people who value clarity and speed. The visual language should feel like the tool itself: distraction-free, efficient, and quietly confident. No visual noise. No decorative gradients "just because". Every element earns its place.

Design references: Linear, Vercel dashboard, Raycast marketing site.

---

## Color Palette

### Primary Palette (Dark Mode First)

| Token                  | Hex       | Usage                                           |
|------------------------|-----------|-------------------------------------------------|
| `--bg-base`            | `#0A0A0B` | Page background                                 |
| `--bg-surface`         | `#111113` | Cards, panels, elevated surfaces                |
| `--bg-border`          | `#1E1E22` | Subtle borders, dividers                        |
| `--text-primary`       | `#F2F2F3` | Headlines, primary body text                    |
| `--text-secondary`     | `#8A8A96` | Labels, captions, metadata                      |
| `--text-muted`         | `#4A4A56` | Placeholder text, disabled states               |
| `--accent`             | `#7C6FFF` | Primary CTA, active states, brand accent        |
| `--accent-hover`       | `#9589FF` | Hover state on accent elements                  |
| `--accent-subtle`      | `#7C6FFF1A` | Accent backgrounds (badges, highlights)        |
| `--success`            | `#22C55E` | Positive states, confirmation                   |
| `--warning`            | `#F59E0B` | Alerts, nudges                                  |
| `--destructive`        | `#EF4444` | Errors, delete actions                          |

### Light Mode Overrides

| Token              | Hex       |
|--------------------|-----------|
| `--bg-base`        | `#FAFAFA` |
| `--bg-surface`     | `#FFFFFF` |
| `--bg-border`      | `#E4E4E7` |
| `--text-primary`   | `#0A0A0B` |
| `--text-secondary` | `#52525B` |
| `--text-muted`     | `#A1A1AA` |

Accent, success, warning, and destructive remain the same across modes.

---

## Typography

### Font Stack

- **Display / Headlines:** `Inter` (variable, 300–800 weight range)
- **Body:** `Inter` (400–500)
- **Monospace / Code:** `JetBrains Mono` (for any code snippets, terminal-style UI text)

All fonts loaded via Google Fonts or self-hosted. No system-ui fallback on marketing pages — brand consistency matters here.

### Type Scale (Tailwind-compatible)

| Role             | Size      | Weight | Line Height | Usage                          |
|------------------|-----------|--------|-------------|-------------------------------|
| `display`        | 60–72px   | 700    | 1.1         | Hero headline                  |
| `headline-lg`    | 40px      | 700    | 1.2         | Section headlines              |
| `headline-md`    | 28px      | 600    | 1.3         | Feature card titles            |
| `body-lg`        | 18px      | 400    | 1.6         | Hero subtext, key paragraphs   |
| `body`           | 16px      | 400    | 1.7         | Standard body copy             |
| `label`          | 14px      | 500    | 1.4         | Buttons, nav, UI labels        |
| `caption`        | 12px      | 400    | 1.5         | Fine print, metadata           |

Tracking: Headlines use `-0.02em` letter-spacing for tightness. Body uses `normal`.

---

## Spacing Philosophy

Based on an **8px base unit**. All spacing, padding, and gap values are multiples of 8.

| Token    | Value | Common use                             |
|----------|-------|----------------------------------------|
| `xs`     | 4px   | Tight inline gaps (icon + label)       |
| `sm`     | 8px   | Component internal padding             |
| `md`     | 16px  | Default card padding                   |
| `lg`     | 24px  | Section internal spacing               |
| `xl`     | 40px  | Between major components               |
| `2xl`    | 64px  | Section vertical padding               |
| `3xl`    | 96px  | Hero vertical breathing room           |

Sections breathe. Marketing pages should not feel cramped. Prefer generous padding over tight layouts.

---

## Component Style Guide

### Buttons

**Primary CTA:**
- Background: `--accent`
- Text: white, `label` size, 500 weight
- Padding: `12px 24px`
- Border-radius: `8px`
- No border, no shadow — flat but purposeful
- Hover: background shifts to `--accent-hover`, subtle scale(1.01)

**Secondary / Ghost:**
- Background: transparent
- Border: `1px solid --bg-border`
- Text: `--text-secondary`
- Hover: border shifts to `--text-muted`, text lifts to `--text-primary`

**No rounded-full pill buttons** — this is a productivity tool, not a consumer app.

### Cards

- Background: `--bg-surface`
- Border: `1px solid --bg-border`
- Border-radius: `12px`
- Padding: `24px`
- No drop shadows — use border contrast instead
- On hover (if interactive): border color shifts from `--bg-border` to `--text-muted`

### Feature Icons

- Use Lucide icons — consistent stroke width, no fills
- Size: 20px in context, 24px in feature cards
- Color: `--accent` for primary features, `--text-secondary` for supporting elements

### Badge / Label Pill

- Background: `--accent-subtle`
- Text: `--accent`, 12px, 500 weight
- Border-radius: `6px`
- Padding: `4px 10px`
- Used for "New", "Beta", section eyebrows above headlines

---

## Homepage Layout — Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│                            NAVIGATION                               │
│  [Logo]          Home  Features  Pricing  Blog        [Get Started] │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                          HERO SECTION                               │
│                                                                     │
│              [Eyebrow badge: "Now in Beta" or similar]              │
│                                                                     │
│           ╔═══════════════════════════════════════╗                 │
│           ║  The AI workspace that gets           ║                 │
│           ║  out of your way.                     ║                 │
│           ╚═══════════════════════════════════════╝                 │
│                                                                     │
│         One sentence subheadline. Clear value prop.                 │
│         No jargon. No buzzwords. Just what it does.                 │
│                                                                     │
│              [Get Started — Free]   [See how it works →]           │
│                                                                     │
│                    ─── Social proof line ───                        │
│           "Trusted by 4,000+ teams" · [logos row: 5 logos]         │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                                                             │   │
│   │         PRODUCT SCREENSHOT / UI PREVIEW                     │   │
│   │         (dark mode dashboard, framed in browser chrome)     │   │
│   │                                                             │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         FEATURES SECTION                            │
│                                                                     │
│             [Eyebrow: "What it does"]                               │
│             Everything you need. Nothing you don't.                 │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│   │  [Icon]          │  │  [Icon]          │  │  [Icon]          │  │
│   │  Feature Title   │  │  Feature Title   │  │  Feature Title   │  │
│   │                  │  │                  │  │                  │  │
│   │  Short desc.     │  │  Short desc.     │  │  Short desc.     │  │
│   │  2-3 sentences.  │  │  2-3 sentences.  │  │  2-3 sentences.  │  │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                     │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│   │  [Icon]          │  │  [Icon]          │  │  [Icon]          │  │
│   │  Feature Title   │  │  Feature Title   │  │  Feature Title   │  │
│   │                  │  │                  │  │                  │  │
│   │  Short desc.     │  │  Short desc.     │  │  Short desc.     │  │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DEEP FEATURE HIGHLIGHT                         │
│                   (alternating left/right layout)                   │
│                                                                     │
│   ┌──────────────────────────────┐  ┌────────────────────────────┐  │
│   │                              │  │  [Eyebrow label]           │  │
│   │   PRODUCT SCREENSHOT         │  │  Feature Headline          │  │
│   │   or ANIMATED DEMO           │  │                            │  │
│   │                              │  │  Paragraph explaining the  │  │
│   │                              │  │  value in concrete terms.  │  │
│   │                              │  │                            │  │
│   │                              │  │  ✓ Bullet one              │  │
│   │                              │  │  ✓ Bullet two              │  │
│   │                              │  │  ✓ Bullet three            │  │
│   └──────────────────────────────┘  └────────────────────────────┘  │
│                                                                     │
│   ┌────────────────────────────┐  ┌──────────────────────────────┐  │
│   │  [Eyebrow label]           │  │                              │  │
│   │  Feature Headline          │  │   PRODUCT SCREENSHOT         │  │
│   │                            │  │   or ANIMATED DEMO           │  │
│   │  Paragraph explaining the  │  │                              │  │
│   │  value in concrete terms.  │  │                              │  │
│   │                            │  │                              │  │
│   │  ✓ Bullet one              │  │                              │  │
│   │  ✓ Bullet two              │  └──────────────────────────────┘  │
│   └────────────────────────────┘                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       SOCIAL PROOF / TESTIMONIALS                   │
│                                                                     │
│             [Eyebrow: "What people are saying"]                     │
│                                                                     │
│   ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────┐  │
│   │  "Quote text here.  │  │  "Quote text here.  │  │  "Quote   │  │
│   │   Short and punchy  │  │   Short and punchy  │  │   text."  │  │
│   │   — no fluff."      │  │   — no fluff."      │  │           │  │
│   │                     │  │                     │  │  — Name   │  │
│   │  — Name, Title      │  │  — Name, Title      │  │  Title    │  │
│   │  [Avatar] [Company] │  │  [Avatar] [Company] │  │  [Avatar] │  │
│   └─────────────────────┘  └─────────────────────┘  └───────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          PRICING SECTION                            │
│                                                                     │
│             Simple, transparent pricing.                            │
│             [Monthly / Annual toggle]                               │
│                                                                     │
│   ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────┐  │
│   │  Free               │  │  Pro         ★       │  │  Team     │  │
│   │  $0/mo              │  │  $12/mo              │  │  $29/mo   │  │
│   │                     │  │  [Most popular]      │  │  per seat │  │
│   │  ✓ Feature          │  │                      │  │           │  │
│   │  ✓ Feature          │  │  ✓ Everything in     │  │  ✓ All    │  │
│   │  ✓ Feature          │  │    Free              │  │    Pro    │  │
│   │                     │  │  ✓ Feature           │  │  + Team   │  │
│   │  [Get Started]      │  │  ✓ Feature           │  │  features │  │
│   │                     │  │                      │  │           │  │
│   │                     │  │  [Start Free Trial]  │  │  [Contact]│  │
│   └─────────────────────┘  └─────────────────────┘  └───────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       FINAL CTA SECTION                             │
│                                                                     │
│              Start building today.                                  │
│              No credit card. No setup. Just focus.                  │
│                                                                     │
│                   [Get Started — It's Free]                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                             FOOTER                                  │
│                                                                     │
│  [Logo]    Product    Company    Legal    Social icons              │
│            Features   About      Privacy  [X] [LinkedIn] [GitHub]  │
│            Pricing    Blog       Terms                              │
│            Changelog  Careers                                       │
│                                                                     │
│  © 2026 [Product Name]. All rights reserved.                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Responsive Notes

### Mobile (< 768px)
- Navigation collapses to hamburger menu
- Hero headline scales to 36–42px
- 3-column feature grid → single column
- Alternating feature highlights → stack vertically (image on top, text below)
- Testimonials → horizontal scroll carousel or single column
- Pricing → single column, most popular plan shown first
- CTA buttons go full-width

### Tablet (768–1024px)
- Feature cards → 2-column grid
- Testimonials → 2-column grid
- Pricing → 3-column (same as desktop, tighter)

---

## Animation & Motion

Keep it minimal and purposeful:
- Fade-in on scroll (opacity 0 → 1, translateY 12px → 0), duration 0.4s, ease-out
- CTA button: scale(1.01) on hover, 0.15s ease
- No parallax. No auto-playing video. No heavy lottie animations.
- Product screenshot: subtle floating animation (translateY ±6px, 4s infinite ease-in-out) to give life without distraction

---

## Dark Mode Implementation

- Default: dark mode
- Toggle: system preference via `prefers-color-scheme`, with manual override stored in localStorage
- CSS variables swap at `:root[data-theme="light"]`
- No flash of unstyled content — inline script sets theme before paint

---

## Open Questions for Jorunn

The following require brand decisions that Ingrid cannot resolve alone:

1. **Product name** — affects logo treatment and wordmark placement in nav
2. **Tagline** — hero headline will be written to complement it
3. **Brand voice** — does the product skew "serious enterprise" or "indie maker-friendly"? Affects copy tone in feature descriptions and CTA text
4. **Accent color confirmation** — `#7C6FFF` (violet) is a placeholder; final accent should align with Jorunn's palette decision
5. **Logo format** — wordmark only, icon only, or lockup? Needed for nav and footer

---

## Implementation Notes for Arve

- Use Tailwind CSS — all spacing, color tokens above map directly to Tailwind config
- Dark mode: class-based strategy (`dark:` prefix) with `data-theme` on `<html>`
- Fonts: load Inter via `@next/font` or `fontsource` — avoid Google Fonts CDN for privacy/performance
- Product screenshots: use `<picture>` with `.webp` + `.png` fallback, lazy-load below the fold
- Use `framer-motion` for scroll animations — keep variants simple (fadeInUp)
- All section IDs should map to nav anchors: `#features`, `#pricing`, `#testimonials`
- Lucide React for all icons — do not mix icon libraries
