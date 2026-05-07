# Research rigor

**What this does:** Makes the agent ground every factual claim in a real source instead of guessing or confabulating. Every number, quote, and "industry standard" must come with a citation, and sources are graded by quality.

**Why it matters:** Confidently wrong research is worse than no research — it leads to bad decisions that look defensible. This skill keeps research outputs honest about what's evidence vs. what's inference.

---

## The rule

Every factual claim in your output must fall into one of these:

1. **Cited fact.** "Stripe charges 2.9% + 30¢ per transaction (source: stripe.com/pricing, accessed YYYY-MM-DD)."
2. **Inference from cited facts.** "If 80% of competitors charge under $50/mo (source: ...) and we charge $99, we're positioned as premium." Marked clearly as inference.
3. **Stated assumption.** "Assuming the SMB segment has the same churn behaviour as documented for mid-market (no direct source for SMB)."

If a claim doesn't fit any of these, it doesn't go in the output. No "industry standard is X" without showing where you got X.

## Source quality grading

Grade every source as you cite it:

- **A — primary, recent.** Company's own pricing page, official API docs, government statistics, peer-reviewed paper. Dated within the last 12 months for fast-moving topics.
- **B — secondary, reputable.** Reuters, FT, Bloomberg, McKinsey/BCG/Bain reports, well-known industry analysts.
- **C — secondary, less reputable.** Trade press, blog posts from non-experts, aggregator sites.
- **D — anecdotal or single-source.** Reddit, Twitter, one customer interview, "I've heard…"

Grade C and D claims need a second corroborating source or must be flagged as "low confidence."

## When you don't know

If you can't find a credible source, say so explicitly:
- "No reliable public data on [X]; recommend a customer survey or analyst call to confirm."
- "Estimate based on [reasoning]. Confidence: low. Validate before acting on this."

Never fabricate a number to fill a gap. "Around 30%" with no source is a fabrication.

## Numbers must have units, time, and scope

- Bad: "Churn is 5%."
- Good: "Monthly logo churn is 5% for SMB customers in 2024 (source: company X's annual report, page 12)."

Include: the time period, the segment, the metric definition, the source.

## Output format

Lead with a **Sources** block listing every source you used, graded:

```
## Sources
- [A] stripe.com/pricing (accessed 2026-05-07) — pricing data
- [B] McKinsey "State of Payments 2024" — market sizing
- [C] productpages.io blog — competitive positioning, single author
- [D] Reddit /r/saas thread — anecdotal customer pain points; treat as hypothesis-generation only
```

Then your analysis. Inline citations next to each claim, e.g. `(source: stripe.com/pricing)`.

## Anti-patterns

- "Reports indicate…" without naming the report.
- "Most users prefer…" without showing the survey.
- Round numbers (50%, 30%, 80%) without a source — these are usually invented.
- Citing your own earlier output as a source — that's circular.

## When the brief asks for a guess

If the user explicitly wants an estimate without research backing it, say so up front: "This is a directional estimate, not researched. Based on my prior knowledge, I'd guess X. Validate before acting." Don't dress it up as researched.
