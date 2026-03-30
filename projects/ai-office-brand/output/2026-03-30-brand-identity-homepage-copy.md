# AI Office — Brand Identity & Homepage Copy

**Agent:** jorunn
**Date:** 2026-03-30
**Project:** AI Office — Marketing Landing Page

---

## Part 1: Brand Personality

### Core Adjectives

**What we are:**
- Precise
- Dependable
- Direct
- Technical
- Efficient

**What we are not:**
- Playful
- Whimsical
- Hype-driven
- Vague
- Warm in a consumer-app sense

**What the adjectives rule out:**
- "Precise" rules out hand-wavy claims. Every statement we make should be specific and verifiable. If we can't back it up with a number or a mechanism, we don't say it.
- "Dependable" rules out beta-language, hedging, and provisional commitments. We speak like a company that ships and stays.
- "Direct" rules out explanatory filler, over-qualification, and sentences that take three clauses to make one point.
- "Technical" rules out dumbing things down. Our audience knows what an API is. We don't explain it.
- "Efficient" rules out long intros, repetitive summaries, and anything that wastes the reader's time.

---

## Part 2: Tone of Voice Guide

### Principle 1 — Lead with the number, not the claim

The number is the argument. Put it first. Don't bury it in a subordinate clause or save it for the end of a paragraph.

**Do:**
> "Reduce LLM API costs by up to 80% with semantic prompt caching."

**Don't:**
> "AI Office is designed to help companies be more strategic about how they use AI, potentially leading to significant cost savings."

**Why:** Enterprise buyers are skeptical of adjectives. A number is a fact. A claim is an invitation to argue.

---

### Principle 2 — Write for the person who reads the docs, not the person who reads the brochure

Our buyer is a CTO or engineering lead. They have seen every SaaS landing page. They distrust marketing language instinctively. Write the way a senior engineer would explain a product to a peer — clearly, without inflation.

**Do:**
> "AI Office sits between your application and the LLM provider. Identical or semantically similar prompts return cached responses. You pay for the call once."

**Don't:**
> "Our revolutionary AI-powered platform transforms the way your team interacts with large language models, unlocking unprecedented value."

**Why:** The word "revolutionary" has been used to sell expense-report software. Avoid it. Describe the mechanism instead.

---

### Principle 3 — Short sentences. Active voice. No throat-clearing.

Every sentence should earn its place. Cut the intro sentence that restates what the headline already said. Cut "In today's fast-paced world." Cut "As businesses increasingly adopt AI."

**Do:**
> "Your prompt cache grows smarter over time. Repeat workloads cost less the second time they run."

**Don't:**
> "In an era where organizations of all sizes are rapidly adopting artificial intelligence solutions, it has become increasingly important to manage costs effectively."

**Why:** The first sentence signals respect for the reader's time. The second signals that a content brief was being padded.

---

### Principle 4 — Name the pain before offering the solution

Don't start with the product. Start with what it costs not to have it. Engineers and CTOs respond to problems they recognize, not solutions they've never asked for.

**Do:**
> "LLM API bills scale with usage. Most of what you're calling is repeated work. You're paying for it every time."

**Don't:**
> "AI Office offers a smarter way to manage your AI infrastructure."

**Why:** "Smarter" is a modifier that means nothing without a baseline. The pain framing creates the baseline.

---

### Principle 5 — Consistency beats cleverness

Use the same words for the same things. If it's "prompt caching," it's always "prompt caching" — not "response caching," "query deduplication," or "intelligent memoization." Variation signals confusion. Consistency signals precision.

**Do:** Pick the canonical term for each concept at the start and use it everywhere.

**Don't:** Rotate synonyms to avoid repetition. In marketing copy, repetition of technical terms is good. It signals expertise.

---

## Part 3: Homepage Copy

### Hero Section

**Primary Headline:**
Stop paying for the same prompt twice.

**Subheadline:**
AI Office caches your LLM API calls — so repeated and semantically similar prompts return instantly, without a new API charge. Most teams cut their LLM costs by 40–80% in the first month.

**Primary CTA:**
Start saving now

**Secondary CTA:**
See how it works

---

### Feature Section 1 — How it works

**Header:**
A proxy that sits between your app and the LLM. Nothing to rip out.

**Body:**
Point your existing API calls at AI Office. No SDK changes, no model switching, no migration. The proxy intercepts requests, checks the cache, and returns a stored response when one matches. If nothing matches, the request goes through to the LLM as normal — and the response gets cached for next time.

Setup takes under 10 minutes. Your team doesn't need to know it's there.

---

### Feature Section 2 — Semantic matching

**Header:**
Exact matches are easy. We catch the near-misses too.

**Body:**
Most caching systems only match identical strings. AI Office uses semantic similarity to recognize when two prompts are asking the same thing in different words. That means you capture savings across rephrased queries, variant inputs, and user-generated text — not just repeated copy-paste calls.

The cache learns your workload. Hit rates improve over time.

---

### Feature Section 3 — Visibility and control

**Header:**
Full observability. You decide what gets cached and what doesn't.

**Body:**
Every request is logged. Cache hits, misses, savings per endpoint, latency delta — all available in the dashboard or via API. Set TTLs by route. Exclude sensitive prompts from caching entirely. Define similarity thresholds per use case.

You control the rules. The cost reduction is the output.

---

### Social Proof Section

**Section Header:**
Trusted by engineering teams moving fast on AI

**Placeholder — Customer Quote 1:**
[PLACEHOLDER — Customer name, title, company]
"We were spending $X on LLM calls every month. After deploying AI Office, that number dropped to $Y within four weeks. The integration took an afternoon."

**Placeholder — Customer Quote 2:**
[PLACEHOLDER — Customer name, title, company]
"The semantic matching was the differentiator for us. We tried a simpler cache first. It barely moved the needle. AI Office caught 60% of our calls."

**Placeholder — Stat bar:**
- [X]% average cost reduction in month one
- [X]ms average latency improvement on cache hits
- [X]M+ cached responses served
- [X]+ engineering teams in production

---

### Closing CTA Section

**Header:**
Your LLM bill is predictable. Your engineering time is not.

**Body:**
AI Office handles cost optimization at the infrastructure layer so your team doesn't have to. No prompt engineering workarounds. No manual deduplication. No spreadsheets tracking API spend by endpoint.

Deploy once. Reduce costs continuously.

**Primary CTA:**
Get started free

**Secondary CTA:**
Talk to an engineer

---

## Part 4: Copy Review Notes

The following patterns must be flagged and cut in any future copy review:

- "Revolutionary" / "game-changing" / "transformative" — delete on sight
- "In today's [adjective] world" — delete on sight
- "Unlock [noun]" — replace with a specific description of what the noun does
- "Leverage" as a verb — replace with "use"
- "Seamless" — replace with a specific description of what makes the experience smooth
- "Robust" — replace with a specific capability statement
- "End-to-end" without specifying what the ends are — delete or specify
- "At scale" tacked onto a sentence that works without it — delete
- Any passive construction that hides the subject of an action
- Any sentence that restates the headline it sits under

---

## Part 5: Brand Scalability Notes

**Logo considerations (for Ingrid / design handoff):**
The name "AI Office" presents scalability challenges at small sizes. A logomark that works as a favicon must be reducible to roughly 16x16px. Recommend establishing a standalone icon early — do not rely solely on a wordmark. The icon should be geometric, single-color-capable, and readable at both dark and light backgrounds.

**Name note:**
"AI Office" is descriptive and functional but risks genericness and potential confusion with Microsoft Office-adjacent branding. Flag for strategic review. If the name is fixed, the visual identity must compensate with strong differentiation — not by being clever, but by being precise and minimal in a way Microsoft's tooling is not.

**Voice consistency across touchpoints:**
- Pricing page: same voice — specific, number-led, no inflated claims
- Error messages: plain language, no apologies, direct next step
- Onboarding emails: same sentence length and register as homepage copy
- Sales deck: data first, no storytelling slide that leads with a quote about "the future of work"
- Invoice and billing: clean, minimal, no marketing language in transactional communications
