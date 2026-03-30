# Tech Stack Selection
**Project:** Neutral — AI Productivity Tool Landing Page
**Agent:** Bjørn
**Date:** 2026-03-30

---

## Decision Summary

**Next.js (App Router, static export) + Tailwind CSS + Vercel**

This is the recommended stack for a no-backend static marketing landing page. It is the simplest path to production given Ingrid's design system constraints, Arve's implementation requirements, and the need for long-term maintainability by a small team.

---

## Framework: Next.js with Static Export

### Decision: Next.js App Router (`output: 'export'`)

**Why not Astro?**

Astro is an excellent static site framework, but Ingrid's design system deliverable (`2026-03-30-design-direction.md`) already assumes a full React runtime:

- `framer-motion` for scroll animations — requires React context
- `@next/font` for self-hosted font loading — Next.js-native API
- Lucide React for all icons
- Class-based dark mode with `data-theme` on `<html>` — easiest to manage in React with `next-themes`

Adopting Astro would require either replacing these with Astro equivalents or using React islands, adding unnecessary complexity for what is a straightforward marketing page. The design system was built for React. Honour it.

**Why not plain HTML/CSS/JS?**

The page has enough interactive surface (dark/light toggle, pricing toggle, scroll animations, responsive nav) that a component model pays for itself. Plain HTML offers no DX advantage here and makes Tailwind's `dark:` class strategy harder to manage without JavaScript tooling.

**Why Next.js static export over a standard Next.js SSR deployment?**

No backend. No data fetching. No server-side rendering is needed. Setting `output: 'export'` in `next.config.ts` produces a fully static build (`/out` directory) with no Node.js server dependency. This:

- Keeps infrastructure cost at zero (Vercel free tier)
- Makes the output portable — can be deployed anywhere (S3, Netlify, GitHub Pages) if needed
- Eliminates cold starts and server errors on a page that does not need them

**Hard to reverse?** Yes, but only marginally. Migrating from Next.js static → Next.js SSR is a config change (`output: 'export'` removal). Migrating to a different framework entirely (e.g., Astro) would require component rewrites. Flag this if the product ever needs server-side personalisation or A/B testing at the edge — at that point, re-evaluate.

---

## Styling: Tailwind CSS v4

Ingrid's design system is fully Tailwind-compatible. All color tokens, spacing values, and type scale map directly to Tailwind config. No separate CSS-in-JS library needed.

**Configuration additions required:**

```ts
// tailwind.config.ts
export default {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: 'class', // class-based, driven by data-theme on <html>
  theme: {
    extend: {
      colors: {
        'bg-base': '#0A0A0B',
        'bg-surface': '#111113',
        'bg-border': '#1E1E22',
        'text-primary': '#F2F2F3',
        'text-secondary': '#8A8A96',
        'text-muted': '#4A4A56',
        accent: '#7C6FFF',
        'accent-hover': '#9589FF',
        'accent-subtle': 'rgba(124, 111, 255, 0.1)',
        success: '#22C55E',
        warning: '#F59E0B',
        destructive: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace'],
      },
      borderRadius: {
        card: '12px',
        button: '8px',
        badge: '6px',
      },
    },
  },
}
```

---

## Fonts: fontsource (self-hosted)

Do **not** use Google Fonts CDN. Ingrid specified this for privacy and performance reasons.

Use `@fontsource/inter` and `@fontsource/jetbrains-mono` — install as npm packages and import in the root layout. This avoids the `@next/font` variable font complexity while keeping fonts self-hosted and cache-friendly.

```bash
npm install @fontsource-variable/inter @fontsource/jetbrains-mono
```

```ts
// src/app/layout.tsx
import '@fontsource-variable/inter'
import '@fontsource/jetbrains-mono/400.css'
```

---

## Animations: Framer Motion

Specified by Ingrid. Keep usage minimal:

- `fadeInUp` variant: `opacity 0 → 1`, `translateY 12px → 0`, 0.4s ease-out
- Wrap sections in `<motion.section>` with `whileInView` + `once: true`
- CTA button hover: `whileHover={{ scale: 1.01 }}`
- Hero screenshot: `animate={{ y: [0, -6, 0] }}` with `transition={{ repeat: Infinity, duration: 4 }}`

No Lottie. No heavy spring physics. Framer Motion's bundle impact is acceptable for a marketing page where perceived polish matters.

---

## Dark Mode: `next-themes`

Use the `next-themes` package to manage dark/light state with:

- System preference detection via `prefers-color-scheme`
- Manual override stored in `localStorage`
- Sets `data-theme` attribute on `<html>` before first paint (no FOUC)

```bash
npm install next-themes
```

```tsx
// src/app/layout.tsx
import { ThemeProvider } from 'next-themes'

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="data-theme" defaultTheme="dark" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

`suppressHydrationWarning` is required to prevent React hydration mismatch on the `data-theme` attribute.

---

## Icons: Lucide React

Specified by Ingrid. Install once, import per icon. Tree-shakeable — no bundle bloat.

```bash
npm install lucide-react
```

Do not introduce any other icon library.

---

## Deployment: Vercel

Vercel is the natural deployment target for Next.js static export. Zero configuration required — connect the GitHub repo, set output directory to `out`, done.

**Why Vercel over alternatives?**

| Option | Cost | DX | CDN | Notes |
|--------|------|----|-----|-------|
| Vercel | Free tier | Excellent | Global | Zero config for Next.js |
| Netlify | Free tier | Good | Global | Viable fallback |
| GitHub Pages | Free | Manual | Good | Requires CI config |
| Railway | Paid | Good | Limited | Overkill — no backend needed |

Vercel is the right call. Free tier is generous for a marketing page. Preview deployments on PRs come for free. Custom domain setup is two clicks.

**Hard to reverse?** No. The build output is static HTML/CSS/JS in `/out`. Migrating to Netlify or any CDN is a 15-minute task.

---

## Folder Structure

```
neutral-landing/
├── public/
│   └── images/           # Product screenshots (.webp + .png)
├── src/
│   ├── app/
│   │   ├── layout.tsx    # Root layout: fonts, ThemeProvider, metadata
│   │   ├── page.tsx      # Homepage — assembles sections
│   │   └── globals.css   # Tailwind base + CSS variable declarations
│   ├── components/
│   │   ├── nav/
│   │   │   └── Navbar.tsx
│   │   ├── sections/
│   │   │   ├── Hero.tsx
│   │   │   ├── Features.tsx
│   │   │   ├── FeatureHighlight.tsx
│   │   │   ├── Testimonials.tsx
│   │   │   ├── Pricing.tsx
│   │   │   ├── CTA.tsx
│   │   │   └── Footer.tsx
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Badge.tsx
│   │       └── ThemeToggle.tsx
│   └── lib/
│       └── motion.ts     # Shared framer-motion variants
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

**Section IDs** must match nav anchor links as Ingrid specified: `#features`, `#pricing`, `#testimonials`.

---

## Package List

```json
{
  "dependencies": {
    "next": "^15",
    "react": "^19",
    "react-dom": "^19",
    "framer-motion": "^11",
    "lucide-react": "^0.400",
    "next-themes": "^0.3",
    "@fontsource-variable/inter": "^5",
    "@fontsource/jetbrains-mono": "^5"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^22",
    "@types/react": "^19",
    "tailwindcss": "^4",
    "@tailwindcss/postcss": "^4"
  }
}
```

---

## next.config.ts

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true, // required for static export
  },
}

export default nextConfig
```

`images.unoptimized: true` is required because `next/image` optimisation requires a server. For a marketing page with a small number of product screenshots, this is acceptable — images should be pre-optimised as `.webp` at source.

---

## Open Questions / Flags for Arve

1. **Accent color**: Ingrid marked `#7C6FFF` as a placeholder pending Jorunn's confirmation. Arve should wire this in as a CSS variable (`--accent`) so a single-line change updates all accent usage across the page.
2. **Product screenshots**: These do not exist yet. Arve should use placeholder images (solid `--bg-surface` block with a `--bg-border` frame) that can be swapped in at zero cost.
3. **Brand name / logo**: Jorunn has not yet delivered. Arve should use a text wordmark placeholder in the nav and footer — do not block implementation on this.
4. **Pricing values**: Ingrid's wireframe has placeholder prices. Jorunn or Else should confirm final pricing before launch. Arve should use the wireframe values as placeholders.

---

## Decisions That Are Hard to Reverse

| Decision | Risk | Exit path |
|----------|------|-----------|
| Next.js as framework | Low | Static export is portable; migrating to Astro = component rewrites |
| Tailwind v4 | Low | No breaking CSS changes expected at this scale |
| class-based dark mode | Low | Only hard to change if the toggle mechanism changes |
| Vercel as host | Very low | Static files, move anywhere in 15 minutes |

No decisions here are genuinely hard to reverse at this stage. The project is pre-launch, the codebase will be small, and all choices are industry-standard tools with large communities.

---

## Summary

| Concern | Decision |
|---------|----------|
| Framework | Next.js 15, App Router, `output: 'export'` |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Fonts | fontsource (self-hosted, no CDN) |
| Animations | Framer Motion (minimal variants) |
| Icons | Lucide React |
| Dark mode | next-themes, class-based, system default |
| Deployment | Vercel (free tier, static output) |
| Backend | None |
