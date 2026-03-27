# AI Agent Usage Policy

**Document type:** Internal Policy / Legal Framework
**Version:** 1.0
**Date:** 2026-03-27
**Author:** Magnus (Legal & Compliance)
**Status:** Draft — Requires professional legal review before adoption

---

> **Disclaimer:** This document is a policy draft prepared for internal review. It does not constitute legal advice. For binding legal commitments or high-stakes decisions, consult a qualified legal professional.

---

## 1. Purpose and Scope

This policy governs the use of AI agents — autonomous software systems that execute tasks, make decisions, and interact with internal and external systems on behalf of users or the organization — within the business.

It applies to:
- All employees, contractors, and third parties operating AI agents on company infrastructure
- All AI agent deployments that access company data, communicate with customers, or take actions with real-world consequences
- Both internally developed agents and third-party AI tools integrated into business workflows

---

## 2. Definitions

**AI Agent** — A software system capable of autonomous or semi-autonomous action, including language model-based agents, robotic process automation (RPA), and agentic pipelines that chain multiple AI models or tools.

**Operator** — The employee or team responsible for deploying and configuring a specific AI agent.

**Principal** — The business unit or individual whose instructions the agent acts on.

**Data Subject** — Any natural person whose personal data may be processed by an AI agent (GDPR Article 4(1)).

**High-Stakes Action** — Any action that is difficult or impossible to reverse, affects external parties, involves financial transactions, or modifies regulated data.

---

## 3. Permitted Uses

AI agents may be used for:

- Internal task automation (data summarization, code generation, report drafting)
- Customer-facing interactions where a human review step is in place before delivery
- Research and analysis where outputs are reviewed before acting upon
- Drafting communications, documents, or plans subject to human approval

All uses must be documented in the Agent Registry (see Section 8).

---

## 4. Prohibited Uses

AI agents must not be used to:

- Make final decisions on credit, employment, insurance, or other high-impact matters without human review (see EU AI Act, high-risk AI systems, Annex III)
- Process special categories of personal data (GDPR Article 9) without explicit legal basis and documented safeguards
- Impersonate a human to a customer or third party without disclosure
- Access systems or data beyond the scope granted to the operator
- Autonomously send external communications (email, messages, posts) on behalf of the business without a human approval step
- Execute irreversible financial transactions above a defined threshold without dual authorization

---

## 5. Data Protection and GDPR Compliance

### 5.1 Lawful Basis

Before deploying an AI agent that processes personal data, the operator must identify and document the lawful basis under GDPR Article 6. Common applicable bases:

- **Legitimate interests** (Article 6(1)(f)): Requires a Legitimate Interests Assessment (LIA). Must be balanced against data subject rights.
- **Contract performance** (Article 6(1)(b)): Only if processing is strictly necessary for a contract with the data subject.
- **Consent** (Article 6(1)(a)): Requires freely given, specific, informed, unambiguous consent. Not suitable for employee monitoring use cases.

### 5.2 Data Minimization

Agents must be configured to process only the minimum personal data necessary for the defined task. Prompt inputs, context windows, and tool calls must not include unnecessary personal identifiers.

### 5.3 Retention and Deletion

- Agent logs containing personal data must be subject to a defined retention schedule.
- If a Data Subject submits a deletion request (GDPR Article 17 — Right to Erasure), the operator must be able to identify and delete all personal data processed by the agent for that subject, including logs, embeddings, and derived outputs.
- **Risk flag:** Vector database embeddings and model fine-tuning data present a specific erasure challenge. If personal data is used to train or fine-tune models, erasure may require retraining. This must be disclosed in the privacy notice and assessed before deployment.

### 5.4 Data Processing Agreements

Any third-party AI provider that processes personal data on our behalf acts as a Data Processor under GDPR Article 28. A Data Processing Agreement (DPA) must be in place before deployment. The DPA must cover:

- Subject matter and duration of processing
- Nature and purpose of processing
- Type of personal data and categories of data subjects
- Obligations and rights of the controller
- Sub-processor authorization and notification obligations
- Data breach notification timelines (72 hours to supervisory authority under GDPR Article 33)

### 5.5 International Data Transfers

If an AI agent sends personal data to a provider outside the EEA, an appropriate transfer mechanism must be in place (e.g., EU Standard Contractual Clauses, adequacy decision). Log the transfer mechanism in the Agent Registry.

### 5.6 Privacy by Design

Agents must be designed with privacy by default (GDPR Article 25). Configuration options that expand data collection or retention must be off by default.

---

## 6. Liability and Risk Management

### 6.1 Operator Accountability

The operator is accountable for the actions of the agents they deploy. This includes:

- Unintended outputs or hallucinations that cause harm
- Unauthorized data access resulting from misconfiguration
- Breach of contract if an agent makes a commitment on behalf of the business

### 6.2 Liability Limitations

Where agents interact with external parties, the following must apply:

- Any terms of service presented by the agent must include a clause limiting liability for AI-generated content to the maximum extent permitted by applicable law
- Agents must not make representations of fact, warranties, or binding offers unless this is explicitly authorized and the outputs are reviewed by a human before delivery
- **Flag for legal review:** Unlimited liability clauses in third-party AI provider agreements must be escalated. Do not accept terms that hold the company liable for all downstream damages caused by AI outputs without a cap.

### 6.3 Insurance

Assess whether existing professional indemnity and cyber liability policies cover AI agent incidents. Confirm coverage with the insurer before deploying agents in customer-facing or financial contexts.

---

## 7. Transparency and Human Oversight

### 7.1 Disclosure to Customers

Customers interacting with an AI agent must be informed that they are interacting with an automated system. This disclosure must be:

- Clear and unambiguous
- Provided before or at the start of the interaction
- Accompanied by a route to reach a human agent on request

This is required under the EU AI Act (Article 50) for systems that interact with natural persons, and aligns with good practice under GDPR transparency obligations (Articles 13–14).

### 7.2 Human-in-the-Loop Requirements

The following actions require human approval before execution, regardless of agent capability:

| Action Type | Required Approval Level |
|---|---|
| External communication to customers | Operator review |
| Financial transaction > [threshold TBD] | Dual authorization |
| Data deletion or export | Data protection lead |
| New third-party integration | IT Security + Legal |
| Changes to production system configuration | Operator + DevOps |

### 7.3 Audit Logs

All agent actions must be logged with:

- Timestamp
- Agent identifier
- Action taken
- Data accessed or modified
- Outcome

Logs must be retained for a minimum of 12 months and be accessible to the operator and compliance team on request.

---

## 8. Agent Registry

All production AI agent deployments must be registered before going live. The registry entry must include:

- Agent name and identifier
- Operator name and team
- Purpose and task scope
- Systems and data sources the agent can access
- Lawful basis for any personal data processing
- Third-party providers involved and DPA status
- Transfer mechanism if data leaves the EEA
- Human oversight mechanism
- Review date

The registry is maintained by the Legal & Compliance function and reviewed quarterly.

---

## 9. Incident Response

If an AI agent causes or contributes to:

- A personal data breach — notify the Data Protection Officer within 24 hours. GDPR Article 33 requires notification to the supervisory authority within 72 hours.
- Financial loss or erroneous transaction — suspend the agent immediately and notify Finance.
- Reputational damage through a public-facing output — notify Communications and Legal immediately.
- Unauthorized system access — notify IT Security immediately and preserve logs.

Agents involved in an incident must be suspended pending investigation.

---

## 10. EU AI Act Considerations

The EU AI Act (applicable from August 2026 for high-risk systems) introduces obligations that may apply to AI agents deployed in business contexts:

- **Prohibited AI practices** (Article 5): Agents must not use subliminal manipulation, exploit vulnerabilities, or perform real-time remote biometric identification in public spaces.
- **High-risk AI systems** (Annex III): Agents used in recruitment, credit scoring, benefits administration, or critical infrastructure management are likely classified as high-risk and require conformity assessment, registration, and ongoing monitoring.
- **General-purpose AI models** (Title VIII): If the business develops or fine-tunes foundation models, additional transparency and safety obligations apply.

**Recommended action:** Audit all AI agent deployments against the EU AI Act high-risk classification criteria before August 2026.

---

## 11. Policy Governance

| Role | Responsibility |
|---|---|
| Legal & Compliance | Policy ownership, Agent Registry, DPA review |
| IT Security | Access controls, audit log infrastructure |
| Data Protection Officer | GDPR compliance sign-off, breach notification |
| Operators | Day-to-day compliance with this policy |
| Senior Management | Risk acceptance for high-stakes deployments |

This policy is reviewed annually and after any significant change to the regulatory landscape or the company's AI agent footprint.

---

## 12. Acknowledgement

All operators deploying AI agents must confirm they have read and understood this policy. Confirmation is recorded in the Agent Registry at registration.

---

## Appendix A: Risk Assessment Checklist (Pre-Deployment)

- [ ] Does the agent process personal data? If yes, lawful basis documented?
- [ ] Does the agent access special categories of data (health, biometric, political, etc.)?
- [ ] Is a DPA in place with all third-party AI providers?
- [ ] Is personal data transferred outside the EEA? Transfer mechanism documented?
- [ ] Is the agent classified as high-risk under the EU AI Act?
- [ ] Are audit logs configured and retention period set?
- [ ] Is a deletion procedure in place to handle Subject Access / Erasure requests?
- [ ] Is there a human-in-the-loop for all high-stakes actions?
- [ ] Have customers been informed they are interacting with an AI agent?
- [ ] Has the agent been registered in the Agent Registry?
- [ ] Has IT Security reviewed access permissions?

---

## Appendix B: Key Regulatory References

| Regulation | Relevant Provisions |
|---|---|
| GDPR (EU) 2016/679 | Articles 5–9, 13–17, 25, 28, 33, 35 |
| EU AI Act 2024/1689 | Articles 5, 6, 50; Annex III; Title VIII |
| ePrivacy Directive 2002/58/EC | Electronic communications, cookies |
| Norwegian Personal Data Act (Personopplysningsloven) | Implements GDPR in Norway |
| UK GDPR / Data Protection Act 2018 | If operating in UK market |

---

*End of document. Version 1.0 — Draft. Not for external distribution.*
