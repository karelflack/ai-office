## [2026-04-11] magnus — Compliance & GDPR Review

**Decision:** 17 LAUNCH BLOCKER items identified across GDPR, SOC 2 readiness, and API key confidentiality. All must be resolved before Stackr can launch to any EU user or enterprise customer.

**Reason:** Stackr processes personal data (user accounts, audit logs, team memberships) and stores sensitive credentials (API keys). Both GDPR and SOC 2 CC6 impose hard technical requirements on these features — they cannot be deferred post-launch.

**Impact:** Arve (implementation) must implement the following non-negotiable controls:
- API keys: envelope encryption (AES-256 + KMS), never plaintext, mask on display after creation
- Passwords: bcrypt cost ≥ 12 or Argon2id — no MD5/SHA-1/SHA-256
- RBAC: enforced server-side at the data layer, never client-side only
- Audit logs: append-only store, no delete capability for any role including admin
- Team isolation: cross-tenant data access must be impossible at the database/RLS layer
- Member removal: access revocation must be immediate, not deferred
- Account deletion: personal data purged within 30 days of request
- No logging of raw API key values or password material anywhere

Dag (infrastructure) must:
- Execute cloud provider DPA (AWS/GCP/Azure standard addendum)
- Enforce TLS 1.2+ on all endpoints
- Provision append-only log storage (e.g., CloudWatch with deny-delete policy)
- Document data residency region

Privacy policy clauses and full checklist at: output/llm-test/compliance/2026-04-11-compliance-checklist.md
---
