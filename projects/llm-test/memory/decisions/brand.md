# Brand Decisions — Stackr

## [2026-04-11] jorunn — Brand Identity

**Decision:** 
- Brand name: "Stackr" (approved in brief)
- Primary tagline: "One dashboard. Total visibility."
- Tone: Direct, data-driven, minimal — no marketing fluff
- Primary color: Navy (#1A3A52), Secondary: Teal (#00A8A8)
- Typography: Inter (heading + body) with geometric sans-serif fallback
- Severity colors: Red (critical), Amber (high), Orange (medium), Blue (low), Green (healthy)

**Reason:** 
Stackr is a B2B developer tool serving teams that need operational clarity. The brand must convey confidence and specificity without hype. Developers distrust marketing language; the tone prioritizes directness and data. The color palette balances professional Navy with modern Teal, with clear CVE severity indicators for the product's core value (vulnerability visibility).

**Impact:** 
- All copywriting (UI, marketing, error messages) should follow the tone of voice guide
- Design system must implement the Inter font pairing and color palette
- Product team should use the "3 traits" framework (Direct, Data-driven, Minimal) for messaging decisions
- CVE/vulnerability cards must use the severity color scale to improve scannability
- This brand identity is the foundation for UI design (Ingrid's work) and marketing copy

---

## [2026-04-11] ingrid — UI/UX Wireframes & Design System

**Decision:** 
- Dashboard-first design: Stack health snapshot on home (stat cards + dependency table), not separate pages
- Severity badges use color + icon + text (never color alone) for accessibility
- Design tokens: Navy (#1A3A52) primary, Teal (#00A8A8) secondary, severity palette (Red/Amber/Orange/Blue/Green)
- Async scan status via polling (every 3s) with progress bar, not WebSocket
- Onboarding: GitHub OAuth integration upfront to reduce manual dependency entry friction
- Mobile-aware but desktop-first (responsive, not mobile-primary)
- Clean/minimal UI: no unnecessary elements, numbers are the hero

**Reason:** 
Dashboard-first reduces navigation depth and keeps developers focused on the core task (finding CVEs). Color-only severity indicators fail WCAG accessibility — adding icon + text ensures screen readers and colorblind users get the information. Polling is simpler to implement than WebSocket given the REST API architecture and Vercel + Railway stack. GitHub integration in onboarding matches developer workflows and reduces friction for the MVP. Mobile responsiveness is a constraint but desktop is the primary use case for security dashboards.

**Impact:** 
- Arve must implement all empty states, error states, loading states (not just happy path)
- Design tokens (Tailwind) must be followed for consistency across all components
- Forms must include validation (version field against OSV.dev, email verification)
- Severity filters on dashboard must work (clicking a stat card filters the table)
- Scan polling must be implemented correctly: stop when status != running/queued, show progress bar
- Accessibility: ARIA labels, keyboard navigation, focus indicators, color + text for severity
- Dark mode support must use `prefers-color-scheme` CSS media query
- Onboarding flow should include GitHub OAuth to `auth/github/callback`, email signup fallback, team creation or join via invitation code

---
