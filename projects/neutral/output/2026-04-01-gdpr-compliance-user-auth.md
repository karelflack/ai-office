# GDPR and Privacy Compliance — User Authentication System

**Agent:** magnus
**Date:** 2026-04-01
**Project:** URL Shortener — User Auth Feature
**Status:** Draft — requires qualified legal counsel review before publication or enforcement

---

## Overview

This document covers GDPR and privacy compliance requirements for the user authentication system added to the URL shortener. The system allows users to register with an email address and password, log in via JWT, and have shortened URLs associated with their account. It also records click analytics (timestamp, referrer, user-agent) on every redirect.

This document is scoped to the authentication feature specifically. It does not replace the broader privacy policy or DPA obligations already documented in `2026-04-01-privacy-policy.md` and `2026-04-01-compliance-checklist.md` — it builds on them with auth-specific detail.

---

## 1. Personal Data Collected and Legal Basis for Processing

### 1.1 Data Inventory

The following personal data is collected by the system as implemented in `app/models.py`, `app/schemas.py`, and `app/auth.py`.

| Data Element | Table | Column | Personal Data? | Sensitivity |
|---|---|---|---|---|
| Email address | `users` | `email` | Yes | Standard personal data |
| Bcrypt-hashed password | `users` | `hashed_password` | Yes (derived from personal secret) | Medium — irreversible hash, but still personal |
| Account creation timestamp | `users` | `created_at` | Yes (linked to identifiable user) | Low |
| Shortened URLs created by user | `links` | `original_url`, `code`, `created_at` | Yes (linked to user via `owner_id`) | Variable — original_url may reveal sensitive browsing intent |
| Click timestamp | `clicks` | `clicked_at` | Yes (linked to link which is linked to owner) | Low |
| HTTP Referrer header | `clicks` | `referrer` | Yes — can reveal browsing context and source site | Medium |
| User-Agent string | `clicks` | `user_agent` | Yes — fingerprinting risk when combined with IP | Medium |

**What is not collected but should be noted:**

- IP addresses are not stored in the database as implemented. However, the FastAPI server and any upstream reverse proxy or load balancer will log IP addresses at the infrastructure layer. Those logs are personal data and must be covered by a separate retention and access policy.
- The JWT access token encodes the user's email as the `sub` claim and is transmitted with every authenticated request. The token itself is not stored server-side, but it is a credential that identifies the user.

### 1.2 Legal Basis for Processing (GDPR Article 6)

| Processing Activity | Legal Basis | Justification |
|---|---|---|
| Storing email and hashed password to enable login | Article 6(1)(b) — performance of a contract | The user requests account creation; authentication is necessary to deliver the service |
| Associating shortened URLs with a user account | Article 6(1)(b) — performance of a contract | URL ownership is the core feature of a registered account |
| Recording click timestamps | Article 6(1)(f) — legitimate interests | Providing usage statistics to the link owner is a reasonable expectation of the service; low intrusion |
| Recording referrer headers | Article 6(1)(f) — legitimate interests | Analytics value to the link owner; medium intrusion — see risk note below |
| Recording user-agent strings | Article 6(1)(f) — legitimate interests | Analytics value; medium intrusion — fingerprinting risk noted below |
| Account creation timestamp | Article 6(1)(b) — performance of a contract | Needed for account management and audit purposes |

**Risk note — legitimate interests balance test required:**

Referrer and user-agent data collection is justified on legitimate interests grounds, but a Legitimate Interests Assessment (LIA) must be documented before going live with EEA users. The LIA must show that: (a) the interest is genuine and specific, (b) the processing is necessary and proportionate, and (c) the data subject's interests do not override yours. Referrer data in particular can reveal sensitive context (e.g., a user clicking a link from a mental health support forum). Consider whether anonymisation or aggregation before storage is sufficient for the use case.

---

## 2. Required Privacy Policy Clauses for User Accounts and URL History

The following clauses must be present in the published privacy policy before any EEA user can create an account. These are additions or expansions to the base policy in `2026-04-01-privacy-policy.md`.

### 2.1 Account Data

The policy must state:

- What data is collected on registration (email address, creation date).
- That passwords are never stored in plain text — only a one-way cryptographic hash (bcrypt) is stored.
- That the email address is used as the login identifier and for any transactional communications (e.g., password reset). If marketing email is ever added, that requires a separate opt-in.
- That account data is processed on the legal basis of contract performance (GDPR Article 6(1)(b)).

### 2.2 URL History

The policy must state:

- That shortened URLs created while logged in are associated with the user's account and visible in the user's link history.
- That the original destination URL is stored in full and may reveal the subject matter of the content the user was sharing.
- That users can delete individual links or all links by deleting their account (see Section 4 on erasure).
- That links created without being logged in are anonymous and not associated with any account.

### 2.3 Click Analytics

The policy must state:

- That the service records analytics data each time a shortened link is clicked, including: the timestamp of the click, the HTTP Referrer header (the page the visitor came from), and the visitor's User-Agent string (browser and device type).
- That this data is linked to the shortened link and therefore indirectly to the link owner's account.
- That click analytics data is processed on legitimate interests grounds to provide link owners with usage statistics.
- That visitor IP addresses are not stored in the application database, though they may appear in server infrastructure logs (which are covered separately).
- The retention period for click data (see Section 3).

### 2.4 JWT Tokens

The policy should note, in plain language, that logged-in sessions use short-lived cryptographic tokens stored in the user's browser. The current implementation sets token expiry at 24 hours (`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24` in `auth.py`). The policy should state this session duration.

---

## 3. Data Retention Policy Recommendations

Retention periods must be defined, documented, and technically enforced. The following are recommendations — they must be confirmed with qualified legal counsel and aligned with any applicable sector-specific requirements.

| Data Category | Recommended Retention | Rationale |
|---|---|---|
| User account (email, hashed password, created_at) | Duration of account + 30 days after deletion request | 30-day grace period allows recovery from accidental deletion; do not retain longer without specific legal justification |
| Shortened links owned by user | Duration of account; deleted with account on erasure request | Links are directly associated with the user and serve no purpose after account closure |
| Click analytics (timestamp, referrer, user_agent) | 12 months from click date, rolling | Sufficient for meaningful trend analysis; beyond 12 months the marginal value is low and the privacy cost increases |
| Anonymous links (no owner_id) | 12 months of inactivity, then deletion | No user to notify; reasonable operational lifespan |
| Server/infrastructure access logs (IP addresses etc.) | 90 days | Standard practice; sufficient for security incident investigation; longer retention requires stronger justification |
| JWT tokens | 24 hours (expiry enforced cryptographically) | As implemented in `auth.py`; no server-side session store means no server-side revocation — see risk note below |

**Risk note — JWT revocation gap:**

The current implementation uses stateless JWTs with no server-side token store. This means that if a user's account is deleted or their email is changed, existing tokens remain valid until they expire (up to 24 hours). For a right-to-erasure request, this creates a 24-hour window during which a deleted user's token can still authenticate. Mitigation options: (a) maintain a token blocklist (Redis or database); (b) reduce token TTL significantly (e.g., 15 minutes with refresh tokens); (c) accept the 24-hour gap as tolerable risk and document it. This decision must be made before launch. Recommend option (b) or (a) for any service processing EEA user data.

---

## 4. Right-to-Erasure Implementation Requirements

Under GDPR Article 17, users have the right to request deletion of their personal data. The following must be deleted or anonymised when a user submits a deletion request.

### 4.1 What Must Be Deleted

| Data | Location | Required Action |
|---|---|---|
| Email address | `users.email` | Hard delete the user row |
| Hashed password | `users.hashed_password` | Deleted with user row |
| Account creation timestamp | `users.created_at` | Deleted with user row |
| All shortened links owned by the user | `links` where `owner_id = user.id` | Hard delete all link rows |
| All click analytics for the user's links | `clicks` where `link_id` references a deleted link | Must cascade-delete — the SQLAlchemy model already defines `cascade="all, delete-orphan"` on `Link.clicks`, which handles this correctly if link deletion cascades from user deletion |

**Engineering note:** The current schema does not define a cascade from `users` to `links`. Deleting a user row without first deleting their links will either fail (foreign key constraint) or orphan the link records. The erasure endpoint must: (1) delete all links owned by the user (which will cascade to clicks via the existing cascade rule), then (2) delete the user row.

### 4.2 What May Be Retained After Erasure

| Data | Basis for Retention |
|---|---|
| Anonymised aggregate click counts (e.g., "this link was clicked 47 times") | If genuinely de-identified and unlinked from any user, aggregate statistics may be retained for service improvement — not personal data |
| Billing or transaction records (if payment is ever added) | Legal obligation under Norwegian accounting law (Bokføringsloven) — typically 5 years |
| Security incident logs referencing the account | Legitimate interests in security investigation, but only for the period strictly necessary |

### 4.3 Erasure Response Timeline

Under GDPR Article 12(3), erasure requests must be acted upon within one calendar month. A response must be sent to the user confirming deletion. If the request is complex, the deadline can be extended by two months, but the user must be notified within the first month.

### 4.4 Erasure Endpoint Requirement

The service must expose a mechanism for users to submit a deletion request. For a self-serve product, this should be an authenticated API endpoint (e.g., `DELETE /me`) that:

1. Authenticates the user via their existing JWT.
2. Deletes all links owned by the user (triggering cascade delete of clicks).
3. Deletes the user row.
4. Invalidates or blocks the user's existing JWT (see JWT revocation note in Section 3).
5. Returns a confirmation response.

This endpoint does not currently exist in the implementation. It is a launch blocker for EEA users.

---

## 5. Consent and Terms-of-Service Requirements for Registration

### 5.1 Consent vs. Contract

For this service, the primary legal basis for processing account data is contract performance (Article 6(1)(b)), not consent. This is important: it means the user does not need to tick a "I consent to processing" checkbox for the account data itself. However, the following consent or notice requirements still apply at registration:

### 5.2 Required at Registration

The registration flow must:

1. **Display a link to the Privacy Policy** before or at the point of account creation. The user must be able to read it before committing. A checkbox saying "I have read and accept the Privacy Policy" is one approach; alternatively, a notice stating "By registering, you agree to our [Privacy Policy]" is acceptable under many interpretations of GDPR, though the checkbox provides cleaner evidence of notice.

2. **Display a link to the Terms of Service** and require acceptance. This is a contractual requirement, not a GDPR requirement per se, but it is necessary to establish the contract that is the legal basis for processing.

3. **Not pre-tick any optional consent boxes.** If any optional processing is ever added (e.g., marketing emails, sharing usage data with third parties for analytics), those must be presented as separate, unticked opt-ins. They cannot be bundled with account creation.

4. **State the purpose clearly.** Users must understand what they are signing up for. The registration form should state in plain language what the account enables and what data is collected.

### 5.3 Age Verification

GDPR Article 8 requires that if a service is directed at children, parental consent is required for users under 16 (the threshold used in Norway). If the URL shortener is a general-purpose tool not specifically directed at children, this is lower risk, but the Terms of Service should include a minimum age clause (e.g., "You must be at least 16 years old to create an account") and the registration form should include a birth year or age confirmation step if the service may attract younger users.

### 5.4 Email Address as Account Identifier — Verification

The current implementation does not require email verification before account activation. An unverified email creates two risks: (a) someone can register with another person's email address, creating a false data association; (b) it is harder to fulfil erasure requests if the email on file was not genuinely that person's. Requiring email verification before full account activation is strongly recommended as a data integrity measure.

---

## 6. Additional GDPR Risks Specific to the Auth Implementation

### 6.1 Email Enumeration via Registration Endpoint

The `POST /register` endpoint returns HTTP 409 with the message "Email already registered" if a registration attempt is made with an existing email. This confirms whether a given email address has an account. This is an information disclosure that can be exploited to enumerate registered users' email addresses. Mitigation: return a generic "If this address is not already registered, you will receive a confirmation email" message regardless of whether the email exists (requires email verification flow).

This is both a security risk and a GDPR risk: the email address is personal data, and confirming its presence in the system without the subject's knowledge is a form of unauthorised disclosure.

### 6.2 Password Requirements

The implementation accepts any password string without length or complexity validation. A minimum length of 12 characters should be enforced. Very short passwords increase the risk of account compromise, which is a personal data breach risk under GDPR Article 33.

### 6.3 Rate Limiting

The login endpoint has no apparent rate limiting. Brute-force attacks against the login endpoint are a personal data breach risk. Rate limiting (e.g., 5 failed attempts per 15 minutes per IP) is required before launch.

### 6.4 Sub-Processor Obligations

If the application is deployed on a cloud provider (AWS, GCP, Azure, Hetzner, etc.), that provider is a sub-processor under GDPR. The hosting provider must: (a) have a GDPR-compliant DPA in place; (b) be located in the EEA or a country with an adequacy decision, or have Standard Contractual Clauses (SCCs) in place. This must be confirmed before any EEA user data is stored on the platform.

---

## 7. Compliance Checklist — Launch Blockers

The following items must be completed before EEA users are permitted to register. Items marked [BLOCKER] are hard requirements under GDPR.

### Authentication-Specific Blockers

- [ ] [BLOCKER] Implement `DELETE /me` endpoint that hard-deletes the user and all associated links and click data
- [ ] [BLOCKER] Implement user cascade deletion: ensure deleting a user also deletes all their links (and clicks cascade from there via existing rule)
- [ ] [BLOCKER] Add Privacy Policy link to registration flow (displayed before form submission)
- [ ] [BLOCKER] Add Terms of Service link and acceptance mechanism to registration flow
- [ ] [BLOCKER] Publish Privacy Policy that covers: account data, URL history, click analytics (referrer, user-agent), session tokens, retention periods, sub-processors
- [ ] [BLOCKER] Confirm hosting provider has GDPR-compliant DPA and adequate data transfer mechanism (EEA hosting or SCCs)
- [ ] [BLOCKER] Document Legitimate Interests Assessment for referrer and user-agent collection
- [ ] [BLOCKER] Implement JWT revocation or reduce token TTL to close erasure gap (recommend token blocklist or refresh token pattern)

### Strongly Recommended Before Launch

- [ ] Implement email verification before account activation
- [ ] Add minimum password length enforcement (12 characters minimum)
- [ ] Add rate limiting on `/login` and `/register` endpoints
- [ ] Fix email enumeration: replace specific 409 message with generic response that does not confirm email existence
- [ ] Define and document server infrastructure log retention policy (IP addresses in access logs)
- [ ] Implement rolling deletion job for click analytics older than 12 months
- [ ] Implement deletion of anonymous links inactive for more than 12 months
- [ ] Add minimum age clause to Terms of Service; add age confirmation at registration if service may attract under-16 users

### Pre-EEA Launch (if not already in place from prior compliance work)

- [ ] Appoint a Data Protection Officer or designate a DPA contact point (required if large-scale processing of personal data)
- [ ] Maintain a Record of Processing Activities (ROPA) under GDPR Article 30 — add user auth processing activities to the ROPA
- [ ] Prepare a Data Breach Notification procedure covering the user auth system

---

## 8. Summary of Key Decisions Required

The following decisions need to be made by the team or confirmed with legal counsel before launch. These are not questions with an obvious single answer.

| Decision | Options | Recommended |
|---|---|---|
| JWT revocation strategy | (a) Token blocklist in Redis; (b) Short TTL + refresh tokens; (c) Accept 24-hour gap with documentation | Option (b) for new build; document the gap if (c) is chosen |
| Email enumeration mitigation | (a) Generic response + email verification flow; (b) Accept enumeration risk as low-severity | Option (a) — email verification also solves data integrity problem |
| Referrer collection | (a) Keep as-is with LIA; (b) Anonymise referrer to domain-only before storage; (c) Remove | Option (b) is a good balance — retains analytics value, reduces privacy surface |
| Legitimate interests basis for click analytics | Document LIA or switch to consent | LIA documentation is simpler; consent for analytics creates friction and opt-out complications |
| Age verification at registration | (a) ToS clause only; (b) Age confirmation field | ToS clause is minimum viable; age confirmation field if service may attract young users |

---

*This document is a compliance risk assessment produced for internal planning purposes. It does not constitute legal advice. All items marked [BLOCKER] and all key decisions should be reviewed by a qualified legal practitioner before the service is made available to EEA users.*
