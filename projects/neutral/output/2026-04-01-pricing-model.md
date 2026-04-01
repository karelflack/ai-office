# B2B SaaS Pricing Model — AI Office (Neutral)
**Agent:** Nora (Financial Strategy)
**Date:** 2026-04-01
**Project:** Neutral — AI Productivity Platform for B2B

---

## Executive Summary

Neutral is a pre-launch AI productivity platform for knowledge workers and B2B teams. This document defines the three-tier pricing structure, models unit economics for each tier, evaluates two pricing scenarios, and projects revenue at 100, 500, and 1,000 customer milestones.

**Recommended model:** Subscription-based with a monthly cap on AI agent runs — flat-rate tiers for predictability, with usage guardrails that make enterprise procurement straightforward.

**First 10 customers strategy:** The Free tier plus a 14-day Pro trial with no credit card required makes early adoption frictionless. The Pro tier at $12/month annual ($144/year) is a low-commitment yes for an individual professional — well below the cognitive friction threshold for a single-person buying decision.

---

## Inputs from Competitive Analysis (Else, 2026-03-30)

The following market benchmarks from Else's research inform pricing anchors:

| Competitor | Paid Entry Price | Model |
|---|---|---|
| Notion AI | ~$10–16/user/mo (credits after May 2026) | Freemium + credit-based AI |
| Otter.ai | $19.99/user/mo | Freemium |
| Reclaim.ai | ~$8–12/user/mo | Freemium |
| Motion | $19/user/mo (annual) | Paid only |
| Superhuman | $25/user/mo | Paid only |
| Mem.ai | Unknown (implied $8–15/user/mo) | Freemium |
| Reflect | Unknown (implied $10–15/user/mo) | Trial + paid |
| Granola | Unknown (implied $12–18/user/mo) | Freemium |

**Market consensus anchor:** Individual paid tiers cluster around $10–25/user/month. Team/business tiers range from $19–49/user/month. Neutral's pricing at $12/mo (Pro, annual) sits in the lower third of the paid tier range — defensible given pre-launch status and intended to minimize friction for early adopters.

**Key gap from competitive analysis:** There is meaningful open space for a premium single-professional tier in the $10–18/month range that does not compromise on quality. Notion AI and Otter serve this segment but with tool-bloat and generic positioning. Neutral can win here with calm UX and privacy-first architecture.

---

## Scenario Modeling

Before recommending a model, I modeled two viable structures.

---

### Scenario A: Pure Subscription (Flat Rate)

**Structure:** Three flat monthly tiers. No usage metering. All core features fully included within each tier. AI agent runs are included up to a generous monthly limit that 95%+ of users will never hit.

**Tiers:**

| Tier | Monthly (billed monthly) | Monthly (billed annually) | Seats | AI Runs/mo | Storage |
|---|---|---|---|---|---|
| Free | $0 | $0 | 1 | 50 | 500 notes / 1 GB |
| Pro | $16 | $12 | 1 | 1,000 | Unlimited notes / 10 GB |
| Team | $29/seat | $24/seat | 3–50 | 5,000/seat | Unlimited / 50 GB shared |

**Strengths:**
- Completely predictable bills — no surprise invoices
- Passes enterprise procurement easily (fixed monthly/annual commitment)
- Simple to communicate, simple to buy
- Annual plan creates cash-flow buffer pre-revenue

**Weaknesses:**
- Does not capture upside from power users who use far more than average
- Risk of free-tier abuse from individual users who never convert
- No signal from usage data on which features drive upgrade intent

**Assessment:** Viable and safe. Best option for first 10–50 customers where procurement friction is the primary enemy. Leaves some revenue on the table at scale.

---

### Scenario B: Usage-Based with Monthly Cap (Hybrid)

**Structure:** A base subscription fee covers access. AI agent runs are metered against a monthly cap. Customers can purchase additional run bundles at a predictable per-unit price. Cap prevents runaway costs for customers.

**Tiers:**

| Tier | Base Fee (monthly) | Included AI Runs | Overage | Cap |
|---|---|---|---|---|
| Free | $0 | 50 runs/mo | Not available | Hard cap at 50 |
| Pro | $12/mo (annual) | 1,000 runs/mo | $0.01/run | Cap at $20 overage/month |
| Team | $24/seat/mo (annual) | 5,000 runs/seat/mo | $0.008/run | Cap at $30/seat overage/month |
| Enterprise | Custom | Custom | Custom | Custom |

**What counts as an AI run:**
- One summarize/draft/connect operation = 1 run
- One meeting transcript (per meeting) = 5 runs
- One AI search query = 1 run

This metric is predictable (customers know how many meetings they have, how often they use AI features) and directly reflects the value delivered (token processing costs).

**Strengths:**
- Aligns price with value delivered (heavy AI users pay more, light users pay less)
- Overage cap removes the "unpredictable invoice" problem that kills enterprise deals
- Monthly cap = clear budget ceiling in any procurement conversation
- Run bundles are a natural upsell path

**Weaknesses:**
- Slightly more complex to communicate than flat rate
- Requires usage tracking infrastructure from day one
- Some customers will throttle usage to stay under limit (reduces value delivery)
- Overage pricing requires clear documentation to avoid trust issues

**Assessment:** The better long-term model. The monthly cap resolves the enterprise procurement problem. The per-run metric is controllable (customers know their meeting cadence). Recommended for post-launch-10 scaling.

---

## Recommended Model

**Scenario A for the first 10–20 customers. Transition to Scenario B at or after 50 paying customers.**

**Rationale:**
- Pre-launch, the goal is to make it easy to say yes. Flat-rate subscriptions have zero complexity friction.
- Once usage patterns are established (typically after 90–120 days of production usage across 20+ accounts), the team will have real data on median run consumption per seat — enabling confident calibration of run bundle pricing.
- The monthly cap in Scenario B is non-negotiable if enterprise customers are a target: an uncapped usage bill is a deal-killer at the procurement layer.

**For the CachEx prompt caching proxy context:** The same principle applies — usage-based pricing works well when the metric (tokens cached, requests proxied) is something the customer controls and can predict from their existing API usage patterns. The monthly cap is the key design element that makes this enterprise-safe.

---

## Pricing Tiers — Final Recommended Structure

These are the tiers to launch with (Scenario A, flat subscription). Tier names align with Jorunn's brand copy.

### Tier 1: Free

| Attribute | Value |
|---|---|
| Price | $0/month |
| Seats | 1 |
| AI runs/month | 50 |
| Notes | Up to 500 |
| Meeting transcripts | 5/month |
| Storage | 1 GB |
| Sync | Local device only |
| Encryption | Standard |
| Support | Community |
| CTA label | "Get Started" |

**Purpose:** Reduce friction to zero for individual professionals. Generates top-of-funnel organic signups, email list, and word-of-mouth. Free tier users who hit the 500-note or 50-run limits are natural Pro upgrade candidates.

**Conversion trigger:** Notes limit (500) or transcript limit (5/mo) — both hit quickly by active users.

---

### Tier 2: Pro

| Attribute | Value |
|---|---|
| Price | $12/month (annual) · $16/month (monthly) |
| Seats | 1 |
| AI runs/month | 1,000 |
| Notes | Unlimited |
| Meeting transcripts | Unlimited |
| Storage | 10 GB |
| Sync | Cross-device |
| Encryption | End-to-end |
| Support | Priority email |
| Trial | 14-day free trial, no credit card |
| CTA label | "Start Free Trial" |

**Purpose:** Primary revenue-generating tier. Priced to be a frictionless individual buying decision. Annual billing at $144/year is below the cognitive threshold that typically triggers procurement review at most SMBs — a single professional can approve this on their own card.

**Annual/monthly spread:** The $4/month gap (25% discount for annual) is the standard SaaS incentive. Annual creates positive cash flow before infrastructure costs compound.

---

### Tier 3: Team

| Attribute | Value |
|---|---|
| Price | $29/seat/month (monthly) · $24/seat/month (annual) |
| Minimum seats | 3 |
| AI runs/month | 5,000/seat |
| Notes | Unlimited (shared workspace) |
| Meeting transcripts | Unlimited |
| Storage | 50 GB shared |
| Sync | Cross-device + shared workspace |
| Encryption | End-to-end + workspace-level keys |
| Admin controls | Yes — user management, audit logs |
| SSO/SAML | Yes |
| Onboarding | Dedicated session included |
| Support | Dedicated Slack channel |
| CTA label | "Talk to Us" |

**Purpose:** Team deals are 3–10x the revenue of individual Pro seats and generate enterprise referrals. The "Talk to Us" CTA triggers a sales-assisted close — no self-serve for Team, which protects deal quality and pricing discipline.

**Minimum seat floor (3 seats):** Prevents solo-pro customers from misusing Team tier features while maintaining a minimum ARR of $864/year per account (3 seats x $24/mo x 12mo).

---

## Unit Economics Model

### Assumptions

| Assumption | Value | Basis |
|---|---|---|
| Blended cloud infrastructure cost per user/month | $1.20 | Hosting (Vercel), LLM API pass-through (GPT-4o/Claude Sonnet), storage (S3/Supabase) |
| LLM API cost per 1,000 AI runs | $0.80 | ~$0.0008/run average across summarize/search/draft at current API rates |
| Support cost per paying customer/month | $0.60 | Prorated across Pro tier — email-first support, no dedicated CSM |
| Sales & marketing cost per acquired customer (CAC) | $120 (Pro), $800 (Team) | PLG-driven (low CAC for Pro), sales-assisted (higher CAC for Team) |
| Average contract duration before churn | 18 months (Pro), 24 months (Team) | Conservative estimate; SaaS benchmarks for SMB productivity tools |
| Annual billing adoption rate | 60% of paying customers | Incentivized by 25% discount |

---

### Cost Per Tier

| Tier | Monthly Revenue/Seat | Infra + LLM cost | Support cost | Gross Margin/Seat/Month |
|---|---|---|---|---|
| Free | $0 | $0.40 | $0 | -$0.40 (subsidized) |
| Pro (annual) | $12.00 | $1.20 | $0.60 | $10.20 (85%) |
| Pro (monthly) | $16.00 | $1.20 | $0.60 | $14.20 (89%) |
| Team (annual) | $24.00 | $1.80 | $0.40 | $21.80 (91%) |
| Team (monthly) | $29.00 | $1.80 | $0.40 | $26.80 (92%) |

**Gross margin is strong across paid tiers.** AI productivity SaaS with PLG distribution should target 75–85% gross margin. Neutral sits above that range at launch because LLM API costs are already declining rapidly (Claude Sonnet, GPT-4o mini pricing), and local transcription (a key Neutral feature) offloads a significant portion of inference to customer hardware.

**Free tier cost:** Each free user costs approximately $0.40/month in infrastructure. At 1,000 free users, that is $400/month — manageable. Monitor free-to-paid conversion rate; if it falls below 8%, revisit free tier generosity.

---

### CAC, LTV, Payback Period

#### Pro Tier

| Metric | Calculation | Value |
|---|---|---|
| CAC | PLG + content marketing blended | $120 |
| Monthly revenue | $12 (annual) blended with $16 (monthly), 60/40 split | ~$13.60/month |
| Monthly gross margin | $13.60 x 85% | $11.56 |
| LTV (18-month retention) | $13.60 x 18 x 85% | $207.96 |
| LTV:CAC ratio | $207.96 / $120 | 1.73x |
| Payback period | $120 / $11.56 | 10.4 months |

**Flag:** LTV:CAC of 1.73x is acceptable at pre-launch but below the 3x benchmark typically targeted for Series A SaaS. This is addressable by: (1) reducing CAC through organic PLG and referral loops, (2) extending retention beyond 18 months with product stickiness (knowledge graph depth), or (3) upselling Pro users to Team. Target LTV:CAC of 3x within 12 months of launch.

#### Team Tier (per seat, 5-seat average deal)

| Metric | Calculation | Value |
|---|---|---|
| CAC | Sales-assisted, demo + onboarding | $800 (per account) |
| Average seats | 5 | — |
| Monthly revenue | $24/seat x 5 seats | $120/month |
| Monthly gross margin | $120 x 91% | $109.20 |
| LTV (24-month retention) | $120 x 24 x 91% | $2,620.80 |
| LTV:CAC ratio | $2,620.80 / $800 | 3.28x |
| Payback period | $800 / $109.20 | 7.3 months |

**Team tier unit economics are solid.** At 3.28x LTV:CAC and a 7.3-month payback, this tier justifies sales-assisted acquisition. Priority: qualify Team leads carefully — 3-seat minimum, annual contract preferred.

---

## Revenue Projections

### Customer Mix Assumptions

For projection purposes, I model a realistic mix across tiers at each milestone.

| Tier | % of paying customers at 100 | % at 500 | % at 1,000 |
|---|---|---|---|
| Pro (annual) | 70% | 65% | 60% |
| Pro (monthly) | 20% | 20% | 20% |
| Team (annual, avg 5 seats) | 10% | 15% | 20% |

*Free users are not counted as "customers" in this model. Assume 10x free-to-paid ratio — at 1,000 paying customers, approximately 10,000 registered free users.*

---

### Projection at 100 Paying Customers

| Tier | Count | Monthly Revenue | Annual Revenue |
|---|---|---|---|
| Pro (annual) | 70 | $840 | $10,080 |
| Pro (monthly) | 20 | $320 | $3,840 |
| Team (annual, 5 seats avg) | 10 accounts (50 seats) | $1,200 | $14,400 |
| **Total** | **100 customers** | **$2,360/mo** | **$28,320 ARR** |

*Gross margin: ~$2,005/mo (85% blended). Monthly infra + support cost: ~$355.*

---

### Projection at 500 Paying Customers

| Tier | Count | Monthly Revenue | Annual Revenue |
|---|---|---|---|
| Pro (annual) | 325 | $3,900 | $46,800 |
| Pro (monthly) | 100 | $1,600 | $19,200 |
| Team (annual, 5 seats avg) | 75 accounts (375 seats) | $9,000 | $108,000 |
| **Total** | **500 customers** | **$14,500/mo** | **$174,000 ARR** |

*Gross margin: ~$12,325/mo (85% blended). Monthly infra + support cost: ~$2,175.*

---

### Projection at 1,000 Paying Customers

| Tier | Count | Monthly Revenue | Annual Revenue |
|---|---|---|---|
| Pro (annual) | 600 | $7,200 | $86,400 |
| Pro (monthly) | 200 | $3,200 | $38,400 |
| Team (annual, 5 seats avg) | 200 accounts (1,000 seats) | $24,000 | $288,000 |
| **Total** | **1,000 customers** | **$34,400/mo** | **$412,800 ARR** |

*Gross margin: ~$29,240/mo (85% blended). Monthly infra + support cost: ~$5,160.*
*Annual recurring revenue at this milestone: approximately $413K ARR.*

---

## Freemium / Trial Strategy

### Free Tier (Permanent)
The Free tier serves as the primary PLG acquisition channel. Recommendations:
- **Do not gate core AI features entirely.** 50 runs/month is enough to demonstrate real value (3–4 meeting transcripts + a few AI queries = an "aha" moment).
- **Gate by volume, not feature.** Allow free users to experience every feature at low volume — this is more honest marketing and produces higher conversion intent than feature-gating.
- **Email onboarding sequence:** Trigger at signup, day 3, day 7, day 14 — focused on one use case per email (meeting notes, connected notes, AI search). Stop at day 14 unless re-engaged.
- **Conversion trigger:** Surface a contextual upgrade prompt when a free user hits 80% of their note or run limit — not at 100%. Earlier = less friction.

### Pro Trial (14 Days, No Credit Card)
- 14-day trial of the full Pro tier. No credit card required at trial start.
- Trial users should be treated as Pro users in all product respects — no feature degradation to "encourage" upgrade.
- Day 12 email: "Your trial ends in 2 days. Here's what you've built in Neutral." (Show their actual notes, run count, meetings captured.) This is a personalized summary of value delivered — not a generic "upgrade now" push.
- At trial end: downgrade gracefully to Free tier, preserving all data. User can upgrade at any time.
- Card collection: only at the point of upgrade intent (when user clicks "Upgrade"), never earlier.

### Team Tier — Sales-Assisted Close
- No self-serve for Team. "Talk to Us" CTA goes to a Calendly or equivalent.
- First 10 Team accounts: Founder/CEO does the call personally. This is not a scalable strategy — it is the correct strategy at this stage. Every early Team conversation is a customer development session.
- Onboarding included in price. This is a feature, not a concession.

---

## Enterprise Procurement Flags

The following pricing decisions have been reviewed for enterprise procurement compatibility:

| Decision | Status | Notes |
|---|---|---|
| Flat monthly/annual pricing (no usage overage on launch model) | PASS | Predictable bills. Procurement can approve a fixed annual contract. |
| 14-day trial, no credit card | PASS | Reduces friction. No procurement involvement needed at trial stage. |
| Annual billing available for all tiers | PASS | Preferred by procurement. Generates upfront cash for Neutral. |
| Team tier minimum 3 seats | LOW RISK | Some companies may want 1–2 seat team agreements. Handle as exceptions. |
| "Talk to Us" for Team (no self-serve) | PASS | Sales-assisted deals are standard in enterprise procurement. Creates an audit trail. |
| SSO/SAML on Team tier | PASS | Required by most IT procurement checklists. Correct to include from launch. |

**No pricing decisions create material enterprise procurement risk at launch.**

If Neutral adds a Scenario B (usage-based) model in the future, the monthly overage cap must be contractually fixed to maintain procurement compatibility.

---

## Value-vs-Cost Sanity Check

**Question: Does the price reflect the value delivered, not just our costs?**

At $12/month for the Pro tier, the question is: what is Neutral worth to a professional who uses it daily?

Proxy calculation:
- A professional using Neutral for 5 meetings/week saves approximately 15–20 minutes per meeting on note cleanup and action item extraction = 75–100 minutes/week.
- At an effective hourly rate of $75 (conservative for a knowledge worker professional), that is $93–125/month in recovered time value.
- Neutral at $12/month = approximately 10–13% of the value delivered in time savings alone. That is a healthy value-to-price ratio for the customer.

**Conclusion:** $12/month is priced below value, which is correct for early traction. There is room to test price increases toward $16–18/month (annual) once the product has established retention and social proof. Do not increase the price before 200 paying customers.

---

## Decisions Made

- [DECISION] Launch pricing: Flat subscription (Scenario A) — Free/$0, Pro/$12mo annual, Team/$24/seat/mo annual (2026-04-01)
- [DECISION] No credit card required for Pro 14-day trial (2026-04-01)
- [DECISION] Team tier: sales-assisted close only, 3-seat minimum (2026-04-01)
- [DECISION] Target LTV:CAC of 3x within 12 months of launch (currently 1.73x for Pro, 3.28x for Team) (2026-04-01)
- [DECISION] Transition to Scenario B (usage-based with monthly cap) after 50 paying customers once usage data is available (2026-04-01)
- [DECISION] Do not raise Pro annual price above $12/month until 200 paying customers reached (2026-04-01)

---

## Summary Table

| Tier | Monthly Price (annual) | Seats | AI Runs/mo | Gross Margin | LTV (per account) | Payback Period |
|---|---|---|---|---|---|---|
| Free | $0 | 1 | 50 | -$0.40/user | N/A (acquisition cost) | N/A |
| Pro | $12 | 1 | 1,000 | 85% | $208 | 10.4 months |
| Team | $24/seat | 3–50 | 5,000/seat | 91% | $2,621 (5-seat avg) | 7.3 months |

| Milestone | ARR | Monthly Gross Margin | Monthly Net Infra Cost |
|---|---|---|---|
| 100 customers | $28,320 | ~$2,005 | ~$355 |
| 500 customers | $174,000 | ~$12,325 | ~$2,175 |
| 1,000 customers | $412,800 | ~$29,240 | ~$5,160 |
