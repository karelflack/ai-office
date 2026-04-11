# Vault Brand Kit — Visual QA Notes

**Agent:** ingrid  
**Date:** 2026-04-11  
**Reviewing:** `output/test-run/brand/2026-04-10-vault-brand-kit.md` (jorunn)

---

## Upstream outputs read

- `output/test-run/brand/2026-04-10-vault-brand-kit.md` (jorunn)
- `output/test-run/strategy/2026-04-10-fintech-brand-research.md` (else)

---

## Scope

This review covers:
1. WCAG 2.1 AA contrast ratios for all key text-on-background combinations
2. Palette cohesion and internal consistency
3. Typography legibility at display and body scale

Jorunn's copy, brand voice, and tagline are outside scope and have not been altered.

---

## 1. Contrast Ratio Audit

WCAG 2.1 AA thresholds:
- **Normal text** (< 18pt or < 14pt bold): 4.5:1 minimum
- **Large text** (≥ 18pt, or ≥ 14pt bold): 3.0:1 minimum
- **UI components** (icons, focus rings, borders): 3.0:1 minimum

### Results

| Text Color | Background | Ratio | Normal Text | Large Text | Notes |
|---|---|---|---|---|---|
| Bone White `#F3EEE4` | Vault Black `#171210` | **16.07:1** | PASS | PASS | Primary dark-mode body text. Excellent. |
| Bone White `#F3EEE4` | Vault Slate `#2C2520` | **13.04:1** | PASS | PASS | Card body text on dark surfaces. Excellent. |
| Burnished Gold `#B89030` | Vault Black `#171210` | **6.25:1** | PASS | PASS | Gold on darkest surface. Safe for bold headlines. |
| Burnished Gold `#B89030` | Vault Slate `#2C2520` | **5.08:1** | PASS | PASS | Gold on card surfaces. Safe. |
| Vault Black `#171210` | Burnished Gold `#B89030` | **6.25:1** | PASS | PASS | Dark text on gold CTA button. Safe. |
| Warm Stone `#8C7B6B` | Vault Black `#171210` | **4.57:1** | PASS | PASS | Marginal. Acceptable for body; see note below. |
| **Warm Stone `#8C7B6B`** | **Vault Slate `#2C2520`** | **3.71:1** | **FAIL** | PASS | **Issue 1 — see correction below.** |
| **Burnished Gold `#B89030`** | **Bone White `#F3EEE4`** | **2.57:1** | **FAIL** | **FAIL** | **Issue 2 — see constraint below.** |

---

## 2. Issues Found and Corrections

### Issue 1 — Warm Stone fails on Vault Slate for normal text

**Problem:** Warm Stone (`#8C7B6B`) is specified for "de-emphasized body copy, captions, metadata, secondary labels on dark surfaces." Card and panel backgrounds in dark mode are Vault Slate (`#2C2520`). Warm Stone on Vault Slate achieves only 3.71:1 — which passes for large text but fails for normal-sized body copy, captions (13–14px), and labels (12px).

**Correction:** Lighten Warm Stone by approximately 15% lightness.

| | Old | Corrected |
|---|---|---|
| **Hex** | `#8C7B6B` | `#9E8E7E` |
| **Contrast on Vault Black** | 4.57:1 ✓ | **5.86:1 ✓** |
| **Contrast on Vault Slate** | 3.71:1 ✗ | **4.76:1 ✓** |

`#9E8E7E` (Warm Stone Light) reads as the same warm taupe — the difference is invisible in context but resolves the contrast failure. Replace `#8C7B6B` with `#9E8E7E` throughout.

---

### Issue 2 — Burnished Gold must not be used as foreground text on light surfaces

**Problem:** Burnished Gold (`#B89030`) on Bone White (`#F3EEE4`) achieves only 2.57:1 — below the 3.0:1 threshold even for large text. If gold is rendered as text color or an inline link in a light-mode context, it fails at every scale.

**Constraint (not a palette change):** Burnished Gold is safe as a button/component background — Vault Black text on a gold surface achieves 6.25:1. It is not safe as text on any light surface.

**Light-mode gold accent rule:**  
If gold text, gold links, or gold icons must appear on Bone White, use **Deep Gold `#7A5F1A`** instead:

| | Ratio on Bone White |
|---|---|
| Burnished Gold `#B89030` | 2.57:1 ✗ |
| Deep Gold `#7A5F1A` | **5.22:1 ✓** |

Deep Gold is a darker, richer variant in the same hue family. It preserves the gold identity while meeting AA. Use it exclusively for text/icon contexts on light backgrounds; continue using Burnished Gold for button backgrounds and brand moments on dark surfaces.

---

## 3. Warm Stone on Vault Black — Marginal Note

Warm Stone on Vault Black achieves 4.57:1 — which technically passes AA for normal text, but with only 0.07 of margin. For captions at 13px and labels at 12px (both normal text), this is a fragile pass that anti-aliasing and subpixel rendering can erode on some screens. The corrected `#9E8E7E` (5.86:1 on Vault Black) removes this risk entirely.

---

## 4. Palette Cohesion Assessment

The palette is internally consistent. All five colors share a warm amber-brown undertone that prevents visual dissonance when combined. The progression from Vault Black → Vault Slate → Warm Stone → Bone White maps a clean luminance ramp with no tonal conflict. Burnished Gold operates as a genuinely singular accent — it reads differently from every other color in the set without breaking the warmth.

No cohesion issues found. The corrected Warm Stone (`#9E8E7E`) is a like-for-like lightness shift within the same hue and preserves the palette's character.

---

## 5. Typography Assessment

**DM Serif Display + DM Sans** is a sound pairing. Both come from the same design family (Colophon Foundry), which means shared optical proportions — they pair without visual tension.

| Check | Result |
|---|---|
| Display at 56–72px (DM Serif) | Legible and distinctive. High-contrast stroke variation reads well at scale. |
| H1 at 40–48px (DM Serif) | Solid. Whitespace requirement noted correctly in the kit — do not use below 32px. |
| H2 at 28–32px (DM Serif) | Acceptable. Below 28px the hairline serifs start to thin on low-DPI screens. Enforce 28px minimum. |
| H3 at 20–22px, 700 weight (DM Sans) | Legible and strong. This is technically "large text" per WCAG, so 3:1 applies — all combinations pass. |
| Body at 16px, 400 weight (DM Sans) | Standard and legible. |
| Caption at 13–14px, 400 weight (DM Sans) | Acceptable at 14px. At 13px on Vault Slate with corrected Warm Stone, margin is thinner — prefer 14px for all secondary metadata. |
| Label at 12px, 500 weight (DM Sans) | Minimum viable size. Weight 500 compensates for scale. Do not drop below 12px. |

No changes to the type system required. Minor guidance: treat 13px as a soft floor, not a target; default to 14px for captions.

---

## 6. Summary

| Item | Status | Action |
|---|---|---|
| Bone White on dark surfaces | ✓ Passes | No change |
| Burnished Gold on dark surfaces | ✓ Passes | No change |
| Vault Black on Burnished Gold (CTA) | ✓ Passes | No change |
| Warm Stone on Vault Black | ✓ Passes (marginal) | Update to `#9E8E7E` |
| **Warm Stone on Vault Slate** | **✗ Fails** | **Update to `#9E8E7E`** |
| **Burnished Gold as text on Bone White** | **✗ Fails** | **Add constraint: gold as bg only; use `#7A5F1A` for light-mode gold text** |
| Palette cohesion | ✓ Passes | No change |
| Typography pairing | ✓ Passes | No change |

### Updated Color Tokens

| Token | Old Hex | New Hex | Change |
|---|---|---|---|
| `--color-stone` (Warm Stone) | `#8C7B6B` | `#9E8E7E` | Lightened ~15% to pass AA on Vault Slate |
| `--color-gold-deep` (new token) | — | `#7A5F1A` | Added for gold text on light backgrounds |

The brand kit passes visual QA with these two targeted corrections applied. Jorunn's copy, rationale, tagline, and voice guide are unchanged.

---

*Visual QA complete — ingrid, 2026-04-11*
