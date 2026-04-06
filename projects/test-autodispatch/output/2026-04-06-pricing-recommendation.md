# Pricing Recommendation — Note-Taking App
**Date:** 2026-04-06 | **Author:** nora

---

## Upstream outputs read
- projects/test-autodispatch/output/2026-04-06-competitor-analysis.md (else)

---

## Summary

Recommend a **three-tier freemium model**: Free, Pro at **$7/mo** ($70/yr), and Team at **$9/user/mo** ($90/user/yr). This positions the product in the underserved $3–8/mo cross-platform gap identified in the competitor analysis, undercutting Notion on price while signaling more quality than Apple Notes.

---

## Pricing Tiers

### Tier 1 — Free

**Price:** $0

| Feature | Limit |
|---------|-------|
| Notes | Unlimited |
| Devices | 2 |
| Storage | 1 GB |
| Sync | Full, across 2 devices |
| Markdown & tags | Yes |
| Full-text search | Yes |
| Templates | 5 built-in |
| AI features | None |
| Export | Plain text / Markdown only |
| Collaboration | None |

**Rationale:** The free tier must be genuinely useful — not crippled. Obsidian personal and Apple Notes are free and fully functional. A note limit or broken sync will drive users away before they see value. The constraint is device count (2) and storage (1 GB), which are invisible to light users but create natural upgrade triggers for power users and anyone syncing across phone, tablet, and laptop.

---

### Tier 2 — Pro

**Price:** $7/month | $70/year (~17% discount)

Includes everything in Free, plus:

| Feature | Detail |
|---------|--------|
| Devices | Unlimited |
| Storage | 10 GB |
| AI assistant | Contextual summarization, smart search, note linking suggestions |
| Version history | 90 days |
| Advanced export | PDF, HTML, Docx |
| Custom templates | Unlimited |
| Priority support | Yes |
| Early access | Beta features |

**Rationale:** $7/mo is below Bear Pro ($2.99/mo but Apple-only), well below Notion Plus ($10/mo), and far below Evernote Personal ($14.99/mo). The AI features are the core upgrade driver — but unlike Notion's bolt-on AI add-on ($10/mo extra), AI is included in the base Pro price. This is a deliberate signal: AI is a first-class feature, not a tax. The $70/yr annual plan is important for reducing churn and improving cash flow predictability.

**Primary upgrade trigger:** Third device + AI (e.g., phone + laptop + tablet user who wants smart search).

---

### Tier 3 — Team

**Price:** $9/user/month | $90/user/year (~17% discount)

Minimum: 2 users. Includes everything in Pro, plus:

| Feature | Detail |
|---------|--------|
| Shared workspaces | Yes |
| Collaborative editing | Real-time co-editing on shared notes |
| Comments & mentions | Yes |
| Admin dashboard | User management, usage stats |
| Centralized billing | One invoice for the team |
| SSO (SAML/OAuth) | Yes |
| Shared AI context | AI understands shared notes, not just personal |
| Priority support | Dedicated channel (Slack or email) |

**Rationale:** $9/user/mo undercuts Notion Business ($15/user/mo) by 40% and is cleaner than Obsidian's confusing per-seat commercial licensing. The team AI feature — where the AI can surface connections across the team's shared notes — is a meaningful differentiator unavailable at this price point. SSO is included (not an enterprise add-on) because removing procurement friction is critical for B2B sales at this tier.

**Primary upgrade trigger:** Two or more people sharing notes or a manager wanting visibility across a team knowledge base.

---

## Scenario Modeling

### Revenue at 1,000 paying customers

Assume a plausible conversion mix at early traction:

| Tier | Users | MRR | ARR |
|------|-------|-----|-----|
| Pro (monthly) | 600 | $4,200 | $50,400 |
| Pro (annual, amortized) | 250 | $1,458 | $17,500 |
| Team (10 teams × 5 users avg) | 150 users | $1,350 | $16,200 |
| **Total** | **1,000** | **~$7,000** | **~$84,100** |

This is a conservative mix weighted toward individual Pro. Even with 60% monthly (higher churn risk), the business reaches ~$84K ARR before optimizing for annual or enterprise. Gross margins on SaaS note-taking are typically 70–80% at scale; AI inference costs will compress margins early, but at $7/mo per Pro user the unit economics work if AI calls per user stay under ~$0.50/mo (achievable with caching and summarization-on-demand rather than always-on).

### Break-even signal

At $7/mo Pro, the product needs ~143 paying users to cover $12K/mo in hosting and AI inference costs at early scale. That is a reachable milestone for a product with a working free tier and any distribution.

---

## Freemium vs. Paid-Only

| | Freemium (recommended) | Paid-only |
|--|------------------------|-----------|
| **First 10 customers** | Easy — no credit card friction | Hard — cold outreach or strong brand needed |
| **Word of mouth** | Free tier users share and refer | Limited organic spread |
| **Revenue predictability** | Lower early; grows with conversion | Higher day-1, but slower user growth |
| **Competitive positioning** | Matches Notion, Obsidian — expected in category | Roam Research tried this; lost to free alternatives |
| **AI cost risk** | Free users generate inference costs with no revenue | Eliminates AI cost exposure on non-paying users |

**Recommendation: freemium.** The note-taking category has trained users to try before buying. A paid-only launch requires significantly more marketing spend to acquire the same number of evaluators. The AI cost risk on free users is manageable if free tier users get no AI features — which is already the design above.

The one case to revisit paid-only: if the product is targeting enterprise from day one (team seats as the primary motion), a 14-day trial instead of a permanent free tier reduces support overhead and signals enterprise positioning. Revisit this at 50+ team customers.

---

## Pricing Design Notes

- **Annual discount at 17%** (2 months free) — standard in the category; deep enough to move users but not so deep it signals desperation
- **No per-feature add-ons** — Evernote and Notion AI both damaged trust with add-on pricing; keep it clean
- **No seat minimums above 2 for Team** — removing minimums makes it easy for a two-person startup to sign up without a procurement conversation
- **Free trial for Team tier: 14 days** — teams need to see collaboration features working before committing; a permanent free team tier is operationally complex and hard to monetize

---

## What to Watch

1. **AI cost per free user** — if usage is higher than expected, add a "3 AI queries/mo" limit on Free before cutting the feature entirely
2. **Annual conversion rate** — target 40%+ of Pro subscribers on annual within 6 months; if below 30%, the annual discount may need to go to 20% (3 months free)
3. **Team average seat count** — if teams average under 3 seats, consider a flat "small team" plan at $25/mo for up to 3 users to simplify procurement
