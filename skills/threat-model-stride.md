# Threat model (STRIDE)

**What this does:** Walks the agent through a security threat model whenever a feature touches user data, payments, or authentication. Uses STRIDE — six categories that catch most real-world threats.

**Why it matters:** Security flaws are 10× cheaper to catch at design time than after launch. A 15-minute STRIDE pass on the data flow saves weeks of incident response later.

---

## When to apply

Run a STRIDE pass on any feature that:
- Accepts user-controlled input
- Stores or retrieves personal data, payment data, or credentials
- Authenticates users or makes authorisation decisions
- Talks to a database, third-party API, or file system
- Sends email / SMS / notifications

If the feature does none of these, you can skip — note that in the output.

## The six threats

For each component in the data flow, ask:

### S — Spoofing (impersonation)
Can someone pretend to be a legitimate user, service, or device?
- Strong authentication — passwords + MFA, signed tokens, mTLS
- Session token rotation, short expiry on access tokens

### T — Tampering (modification)
Can data be changed by someone unauthorised, in transit or at rest?
- TLS for everything (no plain HTTP)
- HMAC / signatures on critical messages
- Database constraints + audit logs

### R — Repudiation (denying action)
Can a user perform an action and later deny they did it?
- Append-only audit logs with timestamps and signed identity
- Immutable transaction records for financial events

### I — Information disclosure (leakage)
Can someone read data they shouldn't see?
- Encryption at rest + in transit
- Authorisation checks on every read path (not just the obvious ones)
- Errors that don't leak schema, paths, or stack traces in production

### D — Denial of service
Can someone exhaust resources to take the service down?
- Rate limiting per identity (not just per IP)
- Input size limits (request body, query params, file uploads)
- Timeouts on every external call

### E — Elevation of privilege
Can a low-privilege user gain higher privileges?
- Role checks at the *function* level, not just the route level
- No admin panels behind only "obscurity" — assume the URL is known
- Validate that the resource being accessed belongs to the authenticated user

## Output format

For each component handling user data, produce:

```
## Component: [name]
| Threat | Risk | Mitigation |
|--------|------|------------|
| Spoofing | low / med / high | [what protects against this] |
| Tampering | … | … |
| Repudiation | … | … |
| Information disclosure | … | … |
| Denial of service | … | … |
| Elevation of privilege | … | … |
```

Mark any **HIGH** risks as **LAUNCH BLOCKERS** that must be fixed before release. Other agents (especially arve) read this and treat blockers as required.

## Red flags

These are almost always wrong:
- "We'll add auth later." → no, you won't, and the data is already structured for an auth-less world
- "It's behind our firewall, so it's fine." → defence in depth; assume the firewall fails
- "Logs don't have anything sensitive." → check; logs almost always do
- "We trust this third-party API." → they get breached; don't pass them more than they need
