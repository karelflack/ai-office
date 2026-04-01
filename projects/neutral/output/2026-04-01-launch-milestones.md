# AI Office B2B Launch — Milestone Tracker

**Agent:** knut
**Date:** 2026-04-01
**Project:** Neutral (AI Office B2B Launch)

---

## Overview

This document tracks the four-phase launch plan for AI Office as a B2B SaaS product. It covers research, legal, GTM preparation, and launch. Each phase lists deliverables, owners, dependencies, and target completion week.

**Today:** 2026-04-01
**Target Launch:** Week of 2026-04-22 (public availability + ProductHunt)

---

## Phase Summary

| Phase | Name | Weeks | Status |
|-------|------|-------|--------|
| 1 | Research & Foundation | W1 (Apr 1–7) | In Progress |
| 2 | Legal & Pricing | W1–W2 (Apr 1–14) | Not Started |
| 3 | GTM Preparation | W2–W3 (Apr 8–21) | Not Started |
| 4 | Launch | W4 (Apr 22–28) | Not Started |

---

## Phase 1 — Research & Foundation

**Goal:** Establish competitive positioning and product understanding before any pricing or GTM work begins.

| Deliverable | Owner | Dependencies | Target | Status |
|-------------|-------|-------------|--------|--------|
| Competitive analysis of AI agent platforms (8+ tools: Relevance AI, Zapier, Make, Lindy, AgentOps, AutoGen, CrewAI, Dust) | else | None | Apr 7 | Active |
| Positioning map + 3 whitespace opportunities | else | Competitive analysis | Apr 7 | Active |
| Launch milestone tracker (this document) | knut | Kickoff plan | Apr 1 | Done |

**Notes:**
- Else's competitive analysis is the first critical path item. Nora and Halvard are blocked until it ships.
- Knut can produce the milestone tracker in parallel (no dependency on Else).

---

## Phase 2 — Legal & Pricing

**Goal:** Define pricing tiers and establish legal compliance posture before any customer-facing material is published.

| Deliverable | Owner | Dependencies | Target | Status |
|-------------|-------|-------------|--------|--------|
| B2B SaaS pricing model (3 tiers, unit economics, revenue projections) | nora | Else competitive analysis | Apr 10 | Active |
| Privacy policy (data collected, legal basis, GDPR/CCPA, DPA obligations) | magnus | None | Apr 10 | Active |
| Engineering compliance checklist (audit logs, deletion API, consent flows) | magnus | None | Apr 10 | Active |

**Notes:**
- Magnus can start immediately — privacy policy has no dependency on competitive analysis or pricing.
- Nora is blocked until Else ships (pricing must reflect competitive benchmarks).
- Privacy policy is on the critical path for public launch. If Magnus is delayed past Apr 14, the launch date slips.

---

## Phase 3 — GTM Preparation

**Goal:** Turn research and positioning into actionable go-to-market materials and update the landing page for B2B.

| Deliverable | Owner | Dependencies | Target | Status |
|-------------|-------|-------------|--------|--------|
| Growth strategy: ICP, acquisition channels, onboarding funnel, retention levers | halvard | Else competitive analysis + Nora pricing tiers | Apr 17 | Active |
| 90-day action plan (weekly milestones, first 100 customers) | halvard | Growth strategy | Apr 17 | Active |
| Landing page updated: B2B positioning, pricing section, privacy policy link | arve | Nora pricing tiers + Magnus privacy policy URL | Apr 18 | Not Started |
| OG image, favicon, Vercel deployment config | arve | None (can run in parallel) | Apr 18 | Not Started |
| ProductHunt launch assets (tagline, gallery, maker comment) | jorunn | Growth strategy framing | Apr 19 | Not Started |

**Notes:**
- Halvard is double-blocked: needs both Else (positioning) and Nora (pricing tiers). If either slips, GTM work slips by the same amount.
- Arve's current landing page implementation is complete for consumer (Neutral product). B2B messaging requires a separate pass once Nora and Halvard deliver.
- ProductHunt launch should not be scheduled until growth strategy confirms the channel and timing.

---

## Phase 4 — Launch

**Goal:** Go live with full B2B positioning, pricing, and legal in place. Execute initial acquisition push.

| Deliverable | Owner | Dependencies | Target | Status |
|-------------|-------|-------------|--------|--------|
| Vercel production deployment (custom domain, SSL) | arve | GTM-ready landing page | Apr 22 | Not Started |
| Privacy policy published at /privacy | arve | Magnus policy document | Apr 22 | Not Started |
| ProductHunt submission live | halvard / jorunn | ProductHunt assets ready | Apr 22 | Not Started |
| LinkedIn announcement post | guro | Growth strategy + brand copy | Apr 22 | Not Started |
| First outbound batch (ICP-matched LinkedIn / dev community outreach) | halvard | ICP definition + channel tactics | Apr 23 | Not Started |
| First 10 signups tracked in analytics | halvard | Live site + tracking setup | Apr 25 | Not Started |
| Post-launch retrospective + metrics review | knut | 48h of live traffic | Apr 28 | Not Started |

---

## Risk Register

| # | Risk | Likelihood | Impact | Phase | Owner | Mitigation |
|---|------|-----------|--------|-------|-------|------------|
| R1 | Else delivers late — Nora and Halvard blocked | Medium | High | 1→2,3 | else | Else should treat Apr 7 as a hard deadline. Knut to flag if not received by Apr 8. |
| R2 | Magnus privacy policy delayed past Apr 14 | Medium | Critical | 2→4 | magnus | Magnus has no upstream dependencies — start immediately. GDPR non-compliance blocks public launch. |
| R3 | Pricing too high/low vs. competitors — requires rework | Low | Medium | 2→3 | nora | Nora to explicitly anchor each tier against at least 2 competitors from Else's report. |
| R4 | Landing page B2B update scoped too large — delays deployment | Medium | Medium | 3→4 | arve | Scope update narrowly: pricing section, hero copy update, privacy link. Avoid full redesign. |
| R5 | ProductHunt launch timing misaligned with GTM calendar | Low | Medium | 3→4 | halvard | Halvard to confirm preferred launch day (Tue/Wed perform best) in growth strategy doc. |
| R6 | Analytics / tracking not set up before launch | Medium | High | 4 | arve | Add Plausible or Vercel Analytics to landing page before deploy. No launch without baseline tracking. |
| R7 | No real testimonials or product screenshots before launch | High | Medium | 3→4 | arve | Already flagged by Arve in implementation notes. Halvard should source 2–3 beta users during GTM prep. |

---

## Sequencing Diagram

```
Week 1 (Apr 1–7)
├── [else]    Competitive Analysis ──────────────────────────┐
├── [magnus]  Privacy Policy (independent) ──────────────┐  │
└── [knut]    Milestone Tracker ✓                         │  │
                                                          │  │
Week 2 (Apr 8–14)                                         │  │
├── [nora]    Pricing Model ◄────────────────────────────┘  │
└── [magnus]  Compliance Checklist (complete by Apr 14)      │
                                                             │
Week 3 (Apr 15–21)                                           │
├── [halvard] Growth Strategy ◄────────────────────────────┘
├── [arve]    Landing page B2B update
└── [jorunn]  ProductHunt assets

Week 4 (Apr 22–28)
├── LAUNCH (Apr 22)
├── [halvard] First outbound push
└── [knut]    Post-launch retrospective
```

---

## Current Status Snapshot (as of 2026-04-01)

**Completed (landing page foundation):**
- Design system & wireframes — ingrid
- Tech stack decision (Next.js 15, Tailwind v4, Vercel) — bjorn
- Consumer market research (Neutral product) — else
- Brand identity, tagline, copy — jorunn
- Full landing page implementation — arve

**In Progress (B2B kickoff, all started 2026-04-01):**
- Competitive analysis of AI agent platforms — else (no output yet)
- B2B pricing model — nora (blocked: waiting on else)
- Privacy policy & compliance checklist — magnus (can proceed)
- Growth strategy — halvard (blocked: waiting on else + nora)

**Blockers:**
- Else is the current critical path bottleneck. All Phase 2/3 downstream work waits on the competitive analysis.
- No beta users identified yet — Halvard should flag this in the growth strategy.

---

*Maintained by: knut. Update this document after each phase closes.*
