# Landing Page Implementation Notes
**Agent:** Arve (Engineering)
**Date:** 2026-03-30
**Project:** Neutral — AI Productivity Tool Landing Page

---

## What Was Built

A complete, production-ready Next.js landing page codebase at `output/landing-page/`. All sections defined in Ingrid's wireframe are implemented using the tech stack selected by Bjørn and copy written verbatim from Jorunn's brand deliverable.

---

## File Structure

```
output/landing-page/
├── public/images/             # Placeholder directory — drop .webp screenshots here
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout: fonts, ThemeProvider, metadata
│   │   ├── page.tsx           # Homepage — assembles all sections
│   │   └── globals.css        # Tailwind base + CSS variable declarations
│   ├── components/
│   │   ├── nav/
│   │   │   └── Navbar.tsx     # Sticky navbar, hamburger on mobile, theme toggle
│   │   ├── sections/
│   │   │   ├── Hero.tsx       # Eyebrow, headline, CTAs, social proof, screenshot
│   │   │   ├── Features.tsx   # 6-card grid with Lucide icons
│   │   │   ├── FeatureHighlight.tsx  # 3 alternating left/right deep highlights
│   │   │   ├── Testimonials.tsx     # 3 testimonial placeholders
│   │   │   ├── Pricing.tsx    # 3-tier pricing with annual/monthly toggle
│   │   │   ├── CTA.tsx        # Final call to action
│   │   │   └── Footer.tsx     # 4-column footer with social links
│   │   └── ui/
│   │       ├── Button.tsx     # Primary + secondary variants, Framer Motion hover
│   │       ├── Card.tsx       # Base card with optional interactive hover
│   │       ├── Badge.tsx      # Eyebrow accent badge
│   │       └── ThemeToggle.tsx # Sun/moon toggle using next-themes
│   └── lib/
│       └── motion.ts          # Shared Framer Motion variants (fadeInUp, stagger, float)
├── next.config.ts             # output: 'export', unoptimized images
├── tailwind.config.ts         # Full design token config per Ingrid's spec
├── tsconfig.json
├── postcss.config.mjs
└── package.json
```

---

## Decisions Made During Implementation

### Tailwind v4 CSS import
Tailwind v4 uses `@import "tailwindcss"` in `globals.css` instead of `@tailwind base/components/utilities` directives. The `@tailwindcss/postcss` plugin handles the new import.

### CSS variable strategy
All design tokens are declared as CSS variables in `:root` (dark mode default) with `[data-theme="light"]` overrides. Tailwind color classes reference these via inline `style` props where Tailwind alone can't read CSS variables at runtime. This ensures the design token system works correctly with next-themes.

### `'use client'` directive
All components using Framer Motion, `useState`, `useEffect`, or `useTheme` are marked `'use client'`. The `Footer` component has no interactivity and is a server component by default, which is correct.

### Accent color wired as CSS variable
`--accent` is set as a single CSS variable in `globals.css` and `tailwind.config.ts`. Swapping to a new color requires changing one line in each file.

---

## What Still Needs Doing Before Launch

| Item | Owner | Notes |
|------|-------|-------|
| Product screenshots | Design / Product | Replace `[ Screenshot: ... ]` placeholders in Hero and FeatureHighlight sections. Add `.webp` files to `public/images/`. |
| Real testimonials | Marketing | Replace 3 placeholder quotes. Names, titles, and company logos needed. |
| Logo strip companies | Marketing | Replace the 5 placeholder company names in Hero with real customer logos. |
| CTA href targets | Dev | All `href="#"` on buttons need real URLs (signup, waitlist, or app URL). |
| Blog / Changelog / Roadmap pages | Dev | Nav and footer links currently point to `#`. |
| Favicon / OG image | Design | Add `/public/favicon.ico` and `/public/og-image.png` (1200×630). |
| Vercel deployment | Ops | Connect GitHub repo, set output directory to `out`. No server config needed. |
| A/B test alternate taglines | Marketing | Jorunn provided three alternates in brand-copy.md for testing. |
| "Now in Beta" badge | Product | Update to "Now in Early Access" or remove post-launch. |

---

## How to Run Locally

```bash
cd output/landing-page
npm install
npm run dev
# → http://localhost:3000
```

## How to Build

```bash
npm run build
# Output in ./out/ — deploy this directory to Vercel or any static host
```

---

## Dependencies Added

No dependencies were added beyond what Bjørn specified in `2026-03-30-tech-stack.md`. The exact package list is:

**Runtime:**
- `next@^15`
- `react@^19`, `react-dom@^19`
- `framer-motion@^11`
- `lucide-react@^0.400`
- `next-themes@^0.3`
- `@fontsource-variable/inter@^5`
- `@fontsource/jetbrains-mono@^5`

**Dev:**
- `typescript@^5`
- `tailwindcss@^4`, `@tailwindcss/postcss@^4`
- `@types/node@^22`, `@types/react@^19`, `@types/react-dom@^19`

---

## Notes for Next Agent

- All section IDs are in place: `#features`, `#pricing`, `#testimonials`
- Dark mode defaults to dark, respects system preference, manual toggle in navbar
- Testimonials are clearly marked as placeholders in both code comments and this doc
- The float animation on the hero screenshot is intentional — don't remove it
