# AI Office — Engineering Compliance Checklist (GDPR / CCPA)

**Drafted:** 2026-04-01
**Owner:** Magnus (legal review) + Engineering
**Status:** Draft — requires legal sign-off before use as a compliance gate

> This checklist translates the privacy policy into concrete engineering tasks. Each item maps to a legal obligation. Items marked **[LAUNCH BLOCKER]** must be done before the platform accepts live user data. Others are required before leaving beta or before serving EEA/UK users at scale.

---

## 1. Consent and Notice

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 1.1 | Display a cookie consent banner on first visit. Strictly necessary cookies load without consent; analytics cookies load only after opt-in. | **LAUNCH BLOCKER** | Do not use a pre-ticked opt-in. Banner must be dismissible with a clear reject option. |
| 1.2 | Include a link to the Privacy Policy in the site footer, sign-up form, and onboarding flow. | **LAUNCH BLOCKER** | Link must go to the versioned published policy, not a draft. |
| 1.3 | Show a clear notice during onboarding that Customer Content may be processed by AI models. Require acknowledgement. | **LAUNCH BLOCKER** | This notice supports the legal basis for processing Customer Content. Log the timestamp and version of policy acknowledged. |
| 1.4 | Marketing emails require a double opt-in flow with consent recorded (timestamp, source, version of consent text). | Before any marketing sends | Unsubscribe link must be functional within 10 business days of request. |
| 1.5 | Record and store consent events (cookie consent, marketing opt-in) with timestamp, IP, and consent text version. | **LAUNCH BLOCKER** | Required to demonstrate consent if challenged. |

---

## 2. Data Subject Rights (DSR) API

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 2.1 | Implement a **data export endpoint** that returns all personal data held for a given user in a structured, machine-readable format (JSON or CSV). | Before EEA launch | Must cover: account data, billing history (metadata only, not card numbers), usage logs, agent-processed content. |
| 2.2 | Implement a **data deletion endpoint** that hard-deletes all personal data for a given user on request, within 30 days. | Before EEA launch | Must cascade to: database records, object storage (documents, agent outputs), search indexes, vector stores. Retain audit trail of the deletion itself. |
| 2.3 | Implement a **rectification flow** — allow users to update name, email, and company name from their account settings. | **LAUNCH BLOCKER** | Email change must trigger re-verification. |
| 2.4 | Build an **internal DSR request tracker** — log every incoming rights request (type, date received, date resolved, outcome). | Before EEA launch | 30-day response window is legally required. The tracker enables SLA monitoring. |
| 2.5 | Deletion requests must propagate to **backup snapshots** within 90 days. | Before EEA launch | Document the backup rotation schedule and confirm the deletion window is met. |

---

## 3. Audit Logging

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 3.1 | Log all **authentication events** (login, logout, failed attempts, MFA events) with timestamp, user ID, IP address, and user agent. | **LAUNCH BLOCKER** | Retain for 12 months minimum. |
| 3.2 | Log all **admin actions** (user role changes, data exports, config changes, sub-processor credential updates) with timestamp, actor, and affected resource. | **LAUNCH BLOCKER** | Immutable audit log — admin users must not be able to delete their own audit entries. |
| 3.3 | Log **data access events** for Customer Content (reads, writes, exports by AI agents). | Before EEA launch | Required for demonstrating lawful processing under Art. 5(2) accountability principle. |
| 3.4 | Log **DSR processing events** (deletion initiated, deletion confirmed, export generated). | Before EEA launch | Provides evidence of compliance with data subject rights obligations. |
| 3.5 | Ensure audit logs are stored **separately from application data** and are access-controlled so that only security/compliance roles can read them. | **LAUNCH BLOCKER** | Prevents tampering. Consider append-only log storage. |

---

## 4. Data Minimisation and Retention

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 4.1 | Implement **automated data deletion jobs** to enforce the retention schedule in the privacy policy (e.g., delete inactive account data after 30 days post-cancellation, purge security logs after 12 months). | Before EEA launch | Schedule jobs with monitoring and alerting on failure. |
| 4.2 | Do **not** log raw request bodies that may contain personal data in general application logs. Scrub or avoid capturing sensitive fields (emails, names, document content) in logs. | **LAUNCH BLOCKER** | Common accidental data collection vector. Review logging config before launch. |
| 4.3 | Store only the **minimum necessary** data for analytics. Anonymise or pseudonymise usage events where full fidelity is not needed. | Before EEA launch | IP addresses in analytics should be truncated (drop last octet). |
| 4.4 | Implement **per-Customer retention configuration** — allow Customers to set how long their agent-processed data is retained, up to the platform maximum. | Beta blocker | Enterprise customers will require this as part of their own compliance obligations. |

---

## 5. Access Control

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 5.1 | Enforce **role-based access control (RBAC)** — employees and contractors should only access Customer data on a need-to-know basis for support, operations, or legal purposes. | **LAUNCH BLOCKER** | Document who has access to production data and why. Review quarterly. |
| 5.2 | Require **MFA** for all accounts with access to production systems or Customer data. | **LAUNCH BLOCKER** | No exceptions for admin accounts. |
| 5.3 | Implement **customer data isolation** — one customer's data must not be accessible by another customer via the API or application layer. | **LAUNCH BLOCKER** | Test this explicitly as part of the security review. |
| 5.4 | Log and alert on **unusual data access patterns** (large exports, access outside working hours, new access to sensitive data stores). | Before EEA launch | Part of breach detection obligations. |

---

## 6. Encryption and Security

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 6.1 | Enforce **TLS 1.2+** on all endpoints. Reject older TLS versions. | **LAUNCH BLOCKER** | |
| 6.2 | Encrypt **data at rest** (database, object storage, backups) using AES-256 or equivalent. | **LAUNCH BLOCKER** | Confirm encryption is enabled at the infrastructure layer, not just application layer. |
| 6.3 | Never store **plaintext credentials, API keys, or tokens** in application databases or logs. Use a secrets manager. | **LAUNCH BLOCKER** | |
| 6.4 | Conduct a **penetration test** before accepting external customers. | Before EEA launch | Annual cadence thereafter. |
| 6.5 | Establish a **breach response runbook**: who to call, what to assess, how to notify customers within 72 hours. | **LAUNCH BLOCKER** | Without this, the 72-hour notification window under GDPR Art. 33 is very hard to meet. |

---

## 7. Third-party and Sub-processor Governance

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 7.1 | Maintain a **named sub-processor list** at a public URL (e.g., aioffice.com/legal/sub-processors). Update with 30 days' notice before adding new sub-processors. | **LAUNCH BLOCKER** | Required by DPA and GDPR Art. 28. |
| 7.2 | Ensure all sub-processors have **signed DPAs** in place before sending them any personal data. | **LAUNCH BLOCKER** | File signed copies. |
| 7.3 | Confirm that **AI model providers** (inference APIs) have DPAs that cover the EU SCCs and commit to not training on Customer data. | **LAUNCH BLOCKER** | This is a high-risk area — AI models processing Customer Content without a DPA is a GDPR violation. |
| 7.4 | Publish the standard **Customer DPA** on the website. Make it available during the sign-up flow for enterprise customers. | **LAUNCH BLOCKER** | EU/UK enterprise customers will not sign without it. |

---

## 8. CCPA-Specific Requirements

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 8.1 | Add a **"Do Not Sell My Personal Information"** link in the footer (even though AI Office does not sell data — presence of the link is required for CCPA compliance if you have California users). | Before US launch | |
| 8.2 | Support **CCPA deletion requests** via the DSR endpoint (same mechanism as GDPR, but 45-day response window). | Before US launch | |
| 8.3 | Review whether AI Office qualifies as a **"service provider"** under CCPA for Customer data. If so, ensure the Customer agreement includes the required service provider language restricting use of personal information. | Before US launch | A qualified attorney should make this determination. |

---

## 9. Ongoing Compliance Operations

| # | Requirement | Priority | Notes |
|---|---|---|---|
| 9.1 | Assign a **privacy contact** (privacy@aioffice.com) and ensure the inbox is monitored with a defined SLA (respond within 5 business days, resolve within 30 days). | **LAUNCH BLOCKER** | |
| 9.2 | Conduct an **Article 30 Records of Processing** review and complete the full record before handling live EU personal data. | Before EEA launch | See Appendix A in the privacy policy for the starting outline. |
| 9.3 | Conduct a **Data Protection Impact Assessment (DPIA)** for high-risk processing activities — specifically: AI agent processing of Customer Content, and any systematic monitoring features. | Before EEA launch | Required under GDPR Art. 35 for high-risk processing. Legal counsel should determine scope. |
| 9.4 | Review the privacy policy and compliance posture **annually**, or whenever a material new feature is launched that involves new personal data processing. | Ongoing | Magnus (or equivalent role) should be consulted on any feature that touches personal data. |
| 9.5 | Track and file **Legitimate Interests Assessments (LIAs)** for processing activities based on legitimate interests. | Before EEA launch | Required to demonstrate compliance with Art. 6(1)(f). |

---

## Summary — Launch Blocker Count

Items marked **[LAUNCH BLOCKER]** above: **20 items**

These represent the minimum required before the platform can accept live user data. Engineering should treat this as a pre-launch gate checklist, signed off by legal and security before go-live.

---

*Draft produced by Magnus agent. Must be reviewed by qualified legal counsel and the engineering lead before use as a compliance gate.*
