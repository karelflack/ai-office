# ADR: Tech Stack for AI Office Marketing Landing Page

**Date:** 2026-03-30
**Author:** Bjørn
**Status:** Accepted

---

## Context

We need a marketing landing page for AI Office — an AI productivity tool. The page must be fast, SEO-friendly, visually polished, and maintainable by a small team. It is a static site: no user auth, no server-side data fetching, no backend. The primary goals are conversion and first impressions.

---

## Decision 1: Framework

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Astro** | Purpose-built for content/marketing sites. Zero JS shipped by default. Islands architecture lets you opt into interactivity only where needed. Excellent performance scores. Native Tailwind and React support via integrations. | Smaller ecosystem than Next.js; some team members may be less familiar. |
| **Next.js (static export)** | Mature, large ecosystem, React-native DX. `next export` produces a static build. | Overkill for a pure marketing page. Larger baseline bundle. Static export loses some Next.js features. The framework is optimized for apps, not content sites. |
| **Plain HTML + Vite** | Minimal. No framework overhead. Fast builds. | No component model. Harder to maintain as the page grows. Inline templating gets messy beyond a few sections. |

### Tradeoffs

Next.js is the right default for an *application*, but this is a *marketing site*. Astro was designed exactly for this: it produces zero-JS HTML by default, integrates Tailwind natively, and supports React components in islands where interactivity is needed. Performance is critical for conversion — a faster LCP directly improves bounce rate. Plain HTML is fine for a prototype but becomes painful to maintain once the page has 8+ sections with reusable components.

### Decision

**Astro** with the `@astrojs/react` and `@astrojs/tailwind` integrations.

---

## Decision 2: CSS Approach

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Tailwind CSS** | Utility-first. Fast to iterate. Consistent spacing/color system. No naming overhead. Ships only used classes. Pairs natively with Astro. | Verbose class lists in markup. Learning curve for devs new to it. |
| **CSS Modules** | Scoped styles. Clean separation of concerns. Standard CSS syntax. | Slower iteration — requires naming everything. No built-in design system. More files to manage. |
| **Vanilla CSS** | Zero overhead. Full control. | No design system. Easy to diverge from brand tokens. Poor DX for rapid iteration. |

### Tradeoffs

For a marketing page, iteration speed and visual consistency matter most. Tailwind eliminates naming decisions and enforces a consistent scale for spacing, typography, and color — which directly supports the brand work done by Jorunn. CSS Modules are better suited to component libraries where style encapsulation matters more than speed. This project has one landing page; the encapsulation benefit of CSS Modules is marginal.

### Decision

**Tailwind CSS v3** with a `tailwind.config.ts` that maps AI Office brand tokens (colors, fonts, spacing) to Tailwind's theme extension.

---

## Decision 3: Hosting

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Vercel** | Zero-config deploys from GitHub. Automatic preview URLs on every PR. Edge CDN. Excellent Astro support. Generous free tier. | Vendor lock-in (mild — static files are portable). |
| **Netlify** | Similar to Vercel. Built-in form handling. Good Astro adapter. | Slightly fewer Edge locations than Vercel. UI is less polished. |
| **GitHub Pages** | Free. Simple. No third-party vendor. | No preview deploys. Manual configuration. Limited CDN. No serverless functions if needed later. |

### Tradeoffs

Vercel and Netlify are nearly equivalent for a static Astro site. The tiebreaker is developer experience: Vercel's preview deploy URLs on every PR are genuinely useful for getting sign-off on copy or design changes without needing to run the project locally. GitHub Pages is appropriate for open source projects or extremely simple sites — the lack of preview deploys is a real cost for a team workflow.

### Decision

**Vercel** with GitHub integration. Static Astro export; no serverless functions needed at launch.

---

## Decision 4: Animation Library

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Motion One** | Tiny (~3kb). Built on the Web Animations API. Framework-agnostic — works natively in Astro without React. Declarative scroll animations. | Less documentation than GSAP. |
| **GSAP** | Industry standard. Powerful timeline control. Great scroll trigger plugin. | Commercial license required for some plugins at scale. Larger bundle (~40kb+). |
| **Framer Motion** | Excellent React DX. Declarative. | React-only — requires hydrating components as islands just to animate them. Adds weight. |
| **CSS scroll-driven animations** | Zero JS. No bundle cost. Native browser support improving rapidly. | Limited browser support (Chrome 115+). Complex keyframe syntax. Not all effects are achievable. |

### Tradeoffs

Framer Motion is eliminated immediately — requiring React islands just for entrance animations is the wrong tradeoff for an Astro site. GSAP is powerful but heavyweight for a simple marketing page; GSAP ScrollTrigger is approximately 50kb gzipped. Motion One is the right fit: it is designed for exactly this use case (scroll-triggered entrance animations), ships essentially nothing, and works without a framework. For anything beyond basic fade/slide effects, we can reach for GSAP on a per-section basis.

### Decision

**Motion One** for scroll-triggered entrance animations (fade-in, slide-up on section entry). No animation library for hover states — those use Tailwind's `transition` utilities.

---

## Recommended Folder Structure

```
ai-office-landing/
├── public/
│   ├── fonts/               # Self-hosted web fonts
│   └── images/              # Static images, OG image
├── src/
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Hero.astro
│   │   ├── FeatureGrid.astro
│   │   ├── SocialProof.astro
│   │   ├── Pricing.astro
│   │   ├── CTA.astro
│   │   └── Footer.astro
│   ├── layouts/
│   │   └── Base.astro       # <html>, <head>, meta tags, fonts
│   ├── pages/
│   │   └── index.astro      # Assembles sections
│   ├── scripts/
│   │   └── animations.ts    # Motion One scroll init
│   └── styles/
│       └── global.css       # Tailwind base + brand overrides
├── astro.config.mjs
├── tailwind.config.ts       # Brand token extensions
├── tsconfig.json
└── package.json
```

### Key conventions

- All page sections are `.astro` components — no React unless a section needs client-side interactivity (e.g., an email signup form with validation).
- Brand tokens (colors, type scale, spacing) live in `tailwind.config.ts` under `theme.extend` — a single source of truth that both Tailwind classes and any inline styles reference.
- `Base.astro` sets the `<title>`, OG meta, and canonical URL — easy to extend for future pages.
- `animations.ts` is a plain script imported at the bottom of `Base.astro` — it initializes scroll observers after the DOM loads. Keeps animation logic out of component files.

---

## Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Astro | Purpose-built for static marketing sites; zero JS by default |
| CSS | Tailwind CSS v3 | Fast iteration; native design token support |
| Hosting | Vercel | Zero-config deploys; preview URLs; edge CDN |
| Animations | Motion One | Tiny bundle; framework-agnostic; designed for scroll effects |
