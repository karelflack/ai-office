# Authentication UI/UX Design — Registration, Login, and Dashboard
**Project:** Neutral — URL Shortener
**Agent:** Ingrid
**Date:** 2026-04-01
**Depends on:** Authentication System Architecture (Bjorn), GDPR Compliance (Magnus)

---

## Design Philosophy

These screens are gates, not destinations. The job of the auth UI is to get the user through as fast as possible with zero confusion and full trust. Every element must justify its presence. Follow the same visual system established in `2026-03-30-design-direction.md`: Inter typeface, 8px spacing system, `--accent #7C6FFF`, dark mode first.

Auth flows are where users decide whether to trust a product. Errors must be precise. Recovery paths must be obvious. Empty and loading states must be handled — not ignored.

---

## Screen Inventory

1. Register page (`/register`)
2. Email verification pending page (`/verify-email`)
3. Login page (`/login`)
4. Forgot password page (`/forgot-password`)
5. Reset password page (`/reset-password?token=...`)
6. Authenticated dashboard — URL list (`/dashboard`)
7. Account settings page (`/settings`)

---

## User Flow Diagram

### Happy Path

```
[Landing page]
      |
      | Click "Get Started" or "Sign Up"
      v
[/register]
      |
      | Submit valid email + password
      v
[/verify-email] ← "Check your inbox" holding page
      |
      | User clicks email link → GET /auth/verify?token=<token>
      v
[Token valid?]
      |        \
     YES        NO (expired or invalid)
      |          \
      v           v
[/dashboard]   [/verify-email?error=expired]
                  |
                  | "Resend verification email" CTA
                  v
               [New token sent → same holding page]
      |
      | (subsequent visits)
      v
[/login]
      |
      | Submit valid credentials
      v
[JWT issued — stored in httpOnly cookie]
      |
      v
[/dashboard] ← redirect target (or originally-requested route)
```

### Error Paths

```
WRONG PASSWORD (< 5 attempts):
  /login → inline field error "Incorrect password" → stay on /login

WRONG PASSWORD (5+ attempts in 15 min):
  /login → form-level error "Too many attempts. Try again in 15 minutes."
          → "Forgot password?" link highlighted

DUPLICATE EMAIL ON REGISTER:
  /register → inline field error "An account with this email already exists."
             → "Log in instead →" link below error

EXPIRED VERIFICATION TOKEN:
  /verify-email?error=expired → banner error + "Resend email" button

EXPIRED ACCESS TOKEN (in-session):
  Client detects 401 → silent refresh via refresh token endpoint
  If refresh token also expired → redirect to /login with ?session=expired
  /login → info banner "Your session expired. Please log in again."

RESET TOKEN EXPIRED:
  /reset-password?token=... → "This link has expired" + link to /forgot-password
```

---

## Screen 1: Register Page (`/register`)

### Purpose
Convert a visitor into a registered user. Minimum friction, maximum clarity.

### Primary Action
Submit registration form — "Create account"

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo / Wordmark]                              [Log in instead →]  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                                                                     │
│              ┌───────────────────────────────────┐                  │
│              │                                   │                  │
│              │  Create your account              │                  │
│              │  ─────────────────────────────    │                  │
│              │                                   │                  │
│              │  Email address                    │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │ you@example.com             │  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              │  Password                         │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │ ••••••••••••     [show/hide]│  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │  8+ characters required           │                  │
│              │                                   │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │      Create account         │  │                  │  ← primary accent button
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              │  By signing up you agree to our   │                  │
│              │  Terms of Service and Privacy     │                  │
│              │  Policy.                          │                  │
│              │                                   │                  │
│              └───────────────────────────────────┘                  │
│                                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Field Specifications

| Field | Type | Placeholder | Validation | Error Message |
|-------|------|-------------|------------|---------------|
| Email | `email` | `you@example.com` | Required, valid RFC 5322 format | "Enter a valid email address." |
| Password | `password` | — | Required, min 8 chars | "Password must be at least 8 characters." |

**Password strength:** Do not show a strength meter. Keep it simple — just enforce the minimum and let bcrypt do its job. Complexity requirements (uppercase, symbols) are UX friction with no meaningful security benefit at this product stage.

**Show/hide toggle:** Eye icon (Lucide `Eye` / `EyeOff`), positioned right-inside the input. Toggles `type="password"` to `type="text"`. No animation needed.

**Duplicate email error:** Inline beneath the email field. Include a subtle "Log in instead →" link inline in the error text — this recovers the user in one step, not two.

**Submit state:**
- Button label changes to "Creating account…" with a spinner icon (16px, `--text-muted` color)
- Inputs go `disabled`
- On server error: form-level error banner above the button

**Form-level error banner format:**
```
┌─────────────────────────────────────────────────────┐
│  [!]  Something went wrong. Please try again.       │
└─────────────────────────────────────────────────────┘
```
Background: `--destructive` at 10% opacity. Border: `1px solid --destructive`. Text: `--destructive`. Left icon: Lucide `AlertCircle` at 16px.

### Layout Notes
- Centered card, max-width `440px`, padding `40px`
- Card uses `--bg-surface`, `1px solid --bg-border`, `border-radius: 12px`
- Page background: `--bg-base`
- Vertical centering: `min-height: 100vh`, flex column center
- No decorative elements. No illustration. No social login buttons (not in scope for this phase).
- "Log in instead →" in top-right of header — ghost style, small, not competing with the primary CTA
- Terms line: 12px, `--text-muted`, links in `--accent` underline

### Mobile
- Card goes edge-to-edge with `16px` horizontal padding
- No border-radius on card on mobile
- Full-width button

---

## Screen 2: Email Verification Pending (`/verify-email`)

### Purpose
Hold the user after registration while they verify their email. Prevent abandoned flows by giving clear instructions and a recovery option.

### Primary Action
"Resend verification email" (if delayed or expired)

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo / Wordmark]                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│              ┌───────────────────────────────────┐                  │
│              │                                   │                  │
│              │  [Envelope icon — 32px accent]    │                  │
│              │                                   │                  │
│              │  Check your email                 │                  │
│              │                                   │                  │
│              │  We sent a verification link to   │                  │
│              │  you@example.com                  │                  │  ← email shown in bold
│              │                                   │                  │
│              │  Click the link in the email to   │                  │
│              │  activate your account. It expires│                  │
│              │  in 24 hours.                     │                  │
│              │                                   │                  │
│              │  ─────────────────────────────    │                  │
│              │                                   │                  │
│              │  Didn't get it?                   │                  │
│              │  Check your spam folder, or       │                  │
│              │  [Resend verification email]      │                  │  ← ghost button
│              │                                   │                  │
│              └───────────────────────────────────┘                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Expired token variant** — same layout, banner added at top of card:
```
┌─────────────────────────────────────────────────────┐
│  [!]  That link has expired. Request a new one.     │
└─────────────────────────────────────────────────────┘
```

**Resend throttle:** After clicking "Resend", the button becomes disabled for 60 seconds. Label: "Resend in 58s…" (countdown). Prevents spam. After 60s, re-enables.

**Resend success:** Inline confirmation below button: "Email sent. Check your inbox." in `--success` color. No toast.

---

## Screen 3: Login Page (`/login`)

### Purpose
Authenticate a returning user. Fast, no confusion.

### Primary Action
Submit login form — "Log in"

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo / Wordmark]                            [Create account →]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                                                                     │
│              ┌───────────────────────────────────┐                  │
│              │                                   │                  │
│              │  [SESSION EXPIRED BANNER]         │                  │  ← conditional, see states
│              │                                   │                  │
│              │  Log in to your account           │                  │
│              │  ─────────────────────────────    │                  │
│              │                                   │                  │
│              │  Email address                    │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │ you@example.com             │  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              │  Password                         │                  │
│              │                      [Forgot?]    │                  │  ← "Forgot?" right-aligned
│              │  ┌─────────────────────────────┐  │                  │
│              │  │ ••••••••••••     [show/hide]│  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │           Log in            │  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              └───────────────────────────────────┘                  │
│                                                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Field Specifications

| Field | Type | Validation | Error Message |
|-------|------|------------|---------------|
| Email | `email` | Required, valid format | "Enter your email address." |
| Password | `password` | Required | "Enter your password." |

**Wrong credentials error:** Do not specify whether the email or the password was wrong. Show a single field-agnostic message:
> "Incorrect email or password."

This is both better UX (user reconsiders both fields) and better security (no email enumeration).

**Rate limit error (5 attempts):**
```
┌─────────────────────────────────────────────────────┐
│  [!]  Too many attempts. Try again in 14 minutes.   │
└─────────────────────────────────────────────────────┘
```
Both fields and the submit button go `disabled`. "Forgot password?" link remains enabled — this is the correct recovery path.

**Session expired banner (conditional, shown when `?session=expired` in URL):**
```
┌─────────────────────────────────────────────────────┐
│  [i]  Your session expired. Please log in again.   │
└─────────────────────────────────────────────────────┘
```
Background: `--warning` at 10% opacity. Border: `1px solid --warning`. Icon: Lucide `Clock` 16px.

**Submit state:** Same as register — label → "Logging in…", inputs disabled.

**"Forgot?" link:** Positioned right-aligned above the password label row. 12px, `--text-secondary`, hover `--accent`. Navigates to `/forgot-password`.

**Remember me:** Not included in v1. Session persistence is handled by refresh token expiry (7 days). No need to surface this decision in the UI — keep it simple.

### Redirect Behavior After Login
- If user navigated to `/login` directly: redirect to `/dashboard`
- If user was redirected to `/login` from a protected route: redirect back to that original route
- Implementation: store `?next=/path` in URL before redirect, or use server-side session; Arve to implement
- Logged-in users visiting `/login` or `/register`: redirect immediately to `/dashboard`

---

## Screen 4: Forgot Password (`/forgot-password`)

### Purpose
Initiate password reset. Collect email only.

### Primary Action
"Send reset link"

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo / Wordmark]                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│              ┌───────────────────────────────────┐                  │
│              │                                   │                  │
│              │  Reset your password              │                  │
│              │  ─────────────────────────────    │                  │
│              │                                   │                  │
│              │  Enter the email address for your │                  │
│              │  account and we'll send you a     │                  │
│              │  reset link.                      │                  │
│              │                                   │                  │
│              │  Email address                    │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │ you@example.com             │  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │       Send reset link       │  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              │  ← Back to login                  │                  │
│              │                                   │                  │
│              └───────────────────────────────────┘                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Success state (after submission — regardless of whether email exists):**
Replace the form with:
```
[Envelope icon — 32px accent]

Check your email

If an account exists for you@example.com,
we sent a password reset link. It expires in 1 hour.

← Back to login
```

Always show the same success message whether or not the account exists — prevents email enumeration. The reset link expires in 1 hour (per security spec from Bjorn's architecture).

---

## Screen 5: Reset Password (`/reset-password?token=...`)

### Purpose
Let the user set a new password after clicking the email link.

### Primary Action
"Set new password"

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo / Wordmark]                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│              ┌───────────────────────────────────┐                  │
│              │                                   │                  │
│              │  [EXPIRED TOKEN ERROR — if needed]│                  │
│              │                                   │                  │
│              │  Set a new password               │                  │
│              │  ─────────────────────────────    │                  │
│              │                                   │                  │
│              │  New password                     │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │ ••••••••••••     [show/hide]│  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │  8+ characters required           │                  │
│              │                                   │                  │
│              │  Confirm new password             │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │ ••••••••••••     [show/hide]│  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              │  ┌─────────────────────────────┐  │                  │
│              │  │       Set new password      │  │                  │
│              │  └─────────────────────────────┘  │                  │
│              │                                   │                  │
│              └───────────────────────────────────┘                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Expired token state (detected on page load via token validation):**
Hide the form entirely. Show:
```
[Lock icon — 32px --text-muted]

This link has expired

Password reset links are valid for 1 hour.

[Request a new reset link]    ← accent button, navigates to /forgot-password
```

**Passwords don't match error:** Inline beneath the confirm field: "Passwords do not match."

**Success state (after submit):**
Replace the form with:
```
[CheckCircle icon — 32px --success]

Password updated

Your password has been changed successfully.

[Log in now]    ← accent button, navigates to /login
```

Invalidate all existing refresh tokens on password change (security requirement — Arve to implement).

---

## Screen 6: Authenticated Dashboard — URL List (`/dashboard`)

### Purpose
Show the user their shortened URLs and let them create new ones. This is the core product screen.

### Primary Action
"Shorten a URL" — persistent action in the top section, always visible.

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo]    Dashboard    Settings         [user@example.com ▾]       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Your URLs                                       [+ Shorten URL]   │
│  ────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Shorten a new URL                                          │   │
│  │  ┌──────────────────────────────────────────┐  [Shorten]   │   │
│  │  │  https://paste-your-long-url-here        │              │   │
│  │  └──────────────────────────────────────────┘              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Short URL              Original URL          Clicks  Date  │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │  neu.tr/ab3k  [Copy]   https://example.com/very-long...      │   │
│  │                         24 clicks   Jan 15, 2026   [Delete] │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │  neu.tr/xq9p  [Copy]   https://github.com/org/repo/pull/...  │   │
│  │                         3 clicks    Jan 12, 2026   [Delete] │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │  neu.tr/m2zt  [Copy]   https://docs.google.com/spreadshee... │   │
│  │                         0 clicks    Jan 10, 2026   [Delete] │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Showing 3 of 3 URLs                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### URL List Row Design

Each row contains:
- Short URL (monospace, `JetBrains Mono`, `--accent`, clickable — opens in new tab)
- [Copy] button: ghost, small, Lucide `Copy` icon + "Copy" label. On click: copies to clipboard, label changes to "Copied!" for 1.5s, then reverts. No toast — inline is cleaner.
- Original URL: truncated with ellipsis at ~40ch. Full URL on hover via `title` attribute. `--text-secondary` color.
- Click count: `--text-secondary`, `body` size
- Date created: `--text-muted`, `caption` size
- [Delete] button: ghost, small, Lucide `Trash2` icon, `--text-muted` color. Hover: `--destructive`. Clicking opens an inline confirmation (see below) — not a modal.

**Delete confirmation (inline, replaces the row):**
```
│  Delete neu.tr/ab3k?  This cannot be undone.    [Cancel]  [Delete] │
```
`[Delete]` button: `--destructive` background. `[Cancel]`: ghost. Keyboard: Escape cancels.

**[Copy] state machine:**
```
Default: [Copy icon] Copy
On click: copy to clipboard
After copy: [Check icon] Copied!   ← --success color, 1.5s
Return to: [Copy icon] Copy
```

### Empty State (new user, no URLs yet)

Replace the URL table with:
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              [Link icon — 32px --text-muted]                    │
│                                                                 │
│              No URLs yet                                        │
│              Shorten your first link above.                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

No illustration. No confetti. Just honest, minimal guidance.

### Loading State (fetching URLs)

Replace rows with skeleton rows: 3 rows of horizontal bars in `--bg-border` color with a subtle shimmer animation (CSS `@keyframes`, left-to-right gradient sweep). Match actual row height. Do not show a spinner.

### Shorten URL — Success State

After a successful shorten, a success banner inserts above the table (below the shorten input):
```
┌─────────────────────────────────────────────────────────────────┐
│  [Check]  neu.tr/ab3k created.    [Copy link]    [Dismiss x]   │
└─────────────────────────────────────────────────────────────────┘
```
Background: `--success` at 10% opacity. Auto-dismisses after 6 seconds. The new row also appears at the top of the table.

### Shorten URL — Error States

| Error | Message shown below input |
|-------|--------------------------|
| Empty input | "Enter a URL to shorten." |
| Invalid URL | "Enter a valid URL (e.g. https://example.com)." |
| URL already shortened by this user | "You've already shortened this URL: neu.tr/ab3k" with a copy button |
| Server error | "Something went wrong. Please try again." |

### Navigation Header

- Left: Logo/wordmark
- Center (if needed): "Dashboard" active nav item
- Right: User email, small, `--text-secondary`, with a dropdown chevron (Lucide `ChevronDown`)

User dropdown (on click):
```
┌────────────────────────┐
│  user@example.com      │
│  ─────────────────     │
│  Settings              │
│  ─────────────────     │
│  Log out               │
└────────────────────────┘
```
Dropdown: `--bg-surface`, `1px solid --bg-border`, `border-radius: 8px`, `box-shadow: 0 4px 16px rgba(0,0,0,0.3)`. Position: top-right, aligned to the trigger. Close on outside click or Escape.

### Mobile Dashboard
- Shorten input goes full-width, "Shorten" button below input
- URL list becomes cards stacked vertically (not a table)
- Each card: short URL + copy button on top row; original URL truncated below; clicks + date on bottom row, small; delete icon top-right of card

---

## Screen 7: Account Settings (`/settings`)

### Purpose
Let the user update their email, change their password, and manage their account. Secondary screen — reached via nav, not a primary flow.

### Primary Actions (two independent sections, each with their own submit):
1. Change email
2. Change password

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo]    Dashboard    Settings         [user@example.com ▾]       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Settings                                                           │
│  ────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Email address                                              │   │
│  │  ──────────────────────────────────────────                 │   │
│  │                                                             │   │
│  │  Current: user@example.com                                  │   │
│  │                                                             │   │
│  │  New email address                                          │   │
│  │  ┌──────────────────────────────────────────┐              │   │
│  │  │ new@example.com                          │              │   │
│  │  └──────────────────────────────────────────┘              │   │
│  │                                                             │   │
│  │  [Update email]                                             │   │
│  │  A verification email will be sent to the new address.     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Change password                                            │   │
│  │  ──────────────────────────────────────────                 │   │
│  │                                                             │   │
│  │  Current password                                           │   │
│  │  ┌──────────────────────────────────────────┐              │   │
│  │  │ ••••••••••••              [show/hide]    │              │   │
│  │  └──────────────────────────────────────────┘              │   │
│  │                                                             │   │
│  │  New password                                               │   │
│  │  ┌──────────────────────────────────────────┐              │   │
│  │  │ ••••••••••••              [show/hide]    │              │   │
│  │  └──────────────────────────────────────────┘              │   │
│  │  8+ characters required                                     │   │
│  │                                                             │   │
│  │  [Update password]                                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Danger zone                                                │   │
│  │  ──────────────────────────────────────────                 │   │
│  │                                                             │   │
│  │  Delete account                                             │   │
│  │  Permanently deletes your account and all shortened URLs.  │   │
│  │  This cannot be undone.                                     │   │
│  │                                                             │   │
│  │  [Delete my account]    ← destructive outlined button      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Settings — Field Specs and Validation

**Change Email:**
- New email: Required, valid format, must differ from current
- On submit: POST to `/auth/change-email`, triggers verification email to new address
- Success: inline confirmation below button — "Verification email sent to new@example.com. Your email won't change until you verify."
- Error states: "Enter a valid email address." / "This is already your current email." / server error

**Change Password:**
- Current password: Required (to prevent session hijacking if left unlocked)
- New password: Required, min 8 chars
- On submit: PUT to `/auth/change-password`
- Success: inline "Password updated." in `--success` color
- Error: current password wrong → "Current password is incorrect."
- On success: all other sessions are invalidated (Arve to implement server-side)

**Delete Account:**
- [Delete my account] button: `border: 1px solid --destructive`, `color: --destructive`, background transparent
- On click: confirmation dialog (modal is appropriate here, unlike inline row delete, because this is high-stakes and irreversible)

**Delete Account Modal:**
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Delete your account?                               │
│                                                     │
│  This will permanently delete your account and     │
│  all 3 of your shortened URLs. This cannot be      │  ← show URL count
│  undone.                                            │
│                                                     │
│  Type DELETE to confirm:                            │
│  ┌───────────────────────────────────────────────┐  │
│  │                                               │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  [Cancel]              [Delete my account]          │
│                         ← disabled until "DELETE"   │
│                           is typed exactly          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

Modal overlay: `rgba(0,0,0,0.6)`. Modal card: `--bg-surface`, `1px solid --bg-border`, `border-radius: 12px`. Close on overlay click: no — this action requires explicit confirmation. Close on Escape: yes (maps to Cancel).

---

## UX Decisions Log

### 1. JWT storage: httpOnly cookie, not localStorage
This is a security decision from Bjorn's architecture. No UX implication — the user does not see this. But it means the logout action must call `POST /auth/logout` to clear the cookie server-side rather than just clearing localStorage. The logout button in the dropdown must handle this.

### 2. No "remember me" checkbox
Refresh token TTL (7 days) provides sufficient session continuity for the use case. A checkbox adds cognitive load with no meaningful benefit for a URL shortener. Remove the concept entirely.

### 3. Post-login redirect
Redirect to original requested URL if available, otherwise `/dashboard`. Use `?next=` query param convention — familiar to developers, simple to implement. Arve to read `next` param before redirecting.

### 4. Email verification is required before dashboard access
If a user registers but hasn't verified their email, GET /dashboard redirects them to `/verify-email`. Unverified accounts cannot create shortened URLs. This is both a security practice and a data quality measure.

### 5. No social/OAuth login in v1
Adds complexity (token exchange, account linking, provider failures) with low marginal value for a developer tool at this stage. Ship email + password. Add OAuth in v2 if demand warrants it.

### 6. Session persistence after password change
All refresh tokens for the account are invalidated on password change and account deletion. This means other browser sessions will be logged out. This is correct security behavior. No need to warn the user — it is expected.

### 7. Error message specificity on login
The login error intentionally does not distinguish between "wrong email" and "wrong password" — prevents email enumeration. This is a deliberate UX trade-off in favor of security.

### 8. Inline delete confirmation vs modal
URL row deletion uses inline confirmation (within the row) — low stakes, easily reversible if the user acts quickly (consider adding a 5-second undo if analytics show accidental deletes). Account deletion uses a modal with typed confirmation — high stakes, fully irreversible, requires deliberate action.

---

## Component Reuse Checklist

The following components from the existing design system (see `2026-03-30-design-direction.md`) apply directly:

| Component | Usage in auth screens |
|-----------|----------------------|
| Card | Register, login, forgot-password, reset-password forms |
| Primary button | All form submit actions |
| Ghost button | Resend email, cancel actions, secondary nav links |
| Destructive button | Delete account, delete URL confirmation |
| Error banner | Form-level errors, expired token states |
| Info banner | Session expired notice |
| Success banner | URL created, password updated |
| Input field | All form inputs |
| Dropdown | User menu in nav header |
| Skeleton row | Dashboard loading state |

No new component patterns are introduced. Everything maps to established patterns.

---

## Accessibility Notes

- All form fields use `<label>` elements with `for` attributes — not placeholder-only labels
- Error messages use `role="alert"` so screen readers announce them immediately on injection
- "Show/hide password" button uses `aria-label="Show password"` / `aria-label="Hide password"` that updates on toggle
- Focus management: after form submission with errors, focus moves to first error field
- Focus management: after modal opens, focus traps inside the modal. On close, focus returns to the trigger
- All interactive elements meet 4.5:1 contrast ratio in both dark and light modes
- Confirm-before-delete modal uses `role="dialog"` with `aria-modal="true"` and a descriptive `aria-labelledby`

---

## Implementation Notes for Arve

- Auth form pages are server-rendered (Next.js App Router) — no layout shift, no hydration delay before form appears
- Redirect after login: implement with Next.js `redirect()` server action or `useRouter().push()` on client, using `?next=` param
- Session expired detection: check for `401` response in the global fetch wrapper, attempt silent token refresh, redirect to `/login?session=expired` only if refresh fails
- The delete confirmation modal can use a `<dialog>` element with `showModal()` — native, accessible, no library needed
- Skeleton loading: Tailwind `animate-pulse` on placeholder divs — no extra library
- Copy to clipboard: `navigator.clipboard.writeText()`, with a fallback to `document.execCommand('copy')` for older browsers
- All auth routes (`/dashboard`, `/settings`) must be protected at the middleware level — redirect to `/login?next=/the-route` if no valid session cookie
- The user email dropdown in the nav should be a `<details>/<summary>` or button + popover — do not use a third-party component library for this
