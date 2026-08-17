# Thailand PDPA research for Tawan customer data

**Research date:** 2026-08-17

**Scope:** Tawan's proposed storage of customer conversations, extracted memories and preferences, VIP tiers, recommendations, direct marketing, store isolation, cross-store analytics, exports, subprocessors, international transfers, security, and breach response.
**Source standard:** Thai primary authoritative sources only: the Personal Data Protection Act B.E. 2562 (2019), Royal Gazette notifications, and official PDPC/GPPC material.

> This is product and engineering research, not a legal opinion. Thai counsel should approve the controller/processor allocation, privacy notices, direct-marketing basis, retention schedule, cross-border mechanism, and export/pricing terms before production launch.

## Executive conclusion

Tawan can lawfully store customer conversations and build useful customer memory, but there is no lawful basis called "keep everything for future analysis." Every processing activity needs a defined purpose, a lawful basis, appropriate notice, a retention rule, security controls, and support for data-subject rights. Collection must be limited to what is necessary for a lawful purpose, and a materially new purpose normally requires new notice and consent unless another statutory basis applies. ([PDPA sections 21-24](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

The safest product model is:

- the store is normally the **controller** for its customer sales, service, memory, tiering, and campaigns;
- Duply is normally the **processor** when it operates Tawan only on the store's documented instructions;
- Duply becomes a separate controller for any purpose it independently decides, such as its own account security, billing, or identifiable cross-store product analytics;
- operational service and order data use contract or pre-contract necessity where genuinely required; limited fraud, security, service-quality, and CRM uses may use documented legitimate interests after balancing against customer rights;
- optional durable profiling and direct marketing should be separately disclosed and controlled, with immediate objection/opt-out; consent is the conservative basis for promotional messaging and sensitive or unexpectedly intrusive memory;
- cross-store analytics should use genuinely anonymized aggregates. A customer key that is merely hashed or pseudonymized remains risky because the person may still be indirectly identifiable under the Act's broad definition of personal data. ([PDPA sections 6, 24 and 32](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

The proposed termination rule, "raw data is free but Tawan's customer-level summaries are paid," is legally risky. Existing summaries, inferred preferences, VIP tiers, scores, and recommendations tied to identifiable customers are likely personal data and may fall within a customer's access right. They are also data the store, as controller, needs to honor rights and explain its processing. Tawan may charge for a new bespoke report, consulting, migration work, or truly anonymous platform benchmark, but should not condition statutory data-subject access or the controller's export of existing customer-level records on payment. The Act clearly grants access to a copy of personal data and requires a response within 30 days; it does not clearly resolve every question about fees or whether all inferred data is portable, so Thai counsel must approve the commercial boundary. ([PDPA sections 30-31](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

## 1. Conversations, extracted preferences, and customer memory

### What is personal data

The Act defines personal data as information relating to a person that permits direct or indirect identification. Raw LINE conversations, LINE identifiers, purchase history, addresses, customer summaries, preferences, confidence scores, VIP tiers, churn predictions, and personalized recommendations are therefore personal data whenever they remain linked or linkable to a customer. Labeling a value "AI-derived" does not take it outside the definition. ([PDPA section 6](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

Tawan should separate three domains even if they reference one another:

1. **Operational records:** inquiries, sales journeys, orders, payments, fulfilment, disputes, and tasks.
2. **Customer memory:** explicit preferences, inferred preferences, tier, engagement, and staff notes.
3. **Store knowledge:** catalog, price, stock, policy, promotion, and approved answers.

This separation supports purpose limitation, retention, access control, correction, deletion, and auditing. It also prevents a store policy or another customer's information from becoming customer memory.

### Candidate lawful bases

The appropriate basis is purpose-specific, not table-specific:

| Purpose | Likely starting basis | Product consequence |
|---|---|---|
| Answering an inquiry, preparing a quote, taking an order, payment and fulfilment | Contract or steps requested before contract, section 24(3) | Keep only information genuinely needed for the transaction and customer request. |
| Fraud prevention, security, dispute evidence, limited service-quality review | Legitimate interests, section 24(5), or legal obligation where a specific law applies | Document the interest, necessity, balancing test, safeguards, and objection handling. Do not describe every internal use as "security." |
| Remembering service preferences needed for the current relationship | Contract necessity or a narrowly balanced legitimate interest may be possible | Tell the customer what is remembered; distinguish explicit facts from inferences; permit correction and deletion where applicable. |
| Long-term optional personalization, behavioral segmentation, churn prediction, or future promotions | Consent is the conservative basis; a legitimate-interest basis may sometimes be arguable | Keep this separate from service-required processing and obtain Thai counsel's basis assessment. Refusal must not block unrelated core service. |
| Direct marketing | Consent is the conservative product choice; legitimate interests may be possible in limited circumstances | In all cases, honor an objection immediately. Do not treat a purchase as blanket permission for every channel or store. |
| Compliance with tax, accounting, consumer, or other law | Legal obligation, section 24(6), only where a specific law actually requires it | Record the exact law and required retention period; do not use a generic compliance label. |

The available bases and the requirement to balance legitimate interests against fundamental data rights are in [PDPA section 24](https://ratchakitcha.soc.go.th/documents/17082307.pdf). Consent must be clear, distinguishable, understandable, freely given, and as easy to withdraw as to give; unnecessary consent cannot be made a condition of service. ([PDPA section 19](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

### Sensitive information

Customer chats may unexpectedly reveal health, disability, religion, political opinion, sexual behavior, biometrics, criminal history, or other sensitive information. Section 26 generally requires explicit consent unless a narrow statutory exception applies. Tawan should not infer sensitive traits for VIP scoring, personalization, or marketing; should avoid sending sensitive text to models unless necessary and authorized; and should quarantine, redact, or tightly restrict accidental sensitive content. ([PDPA section 26](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

**Counsel required:** confirm the lawful basis for each memory category, whether a particular inferred attribute is sensitive, and how consent for minors or persons lacking legal capacity will be handled under section 20.

## 2. Purpose limitation, minimization, notices, and retention

Tawan must process data for the purpose told to the customer. A different purpose generally requires notice and consent unless another law permits it. Collection must be limited to what is necessary for a lawful purpose. At or before collection, the controller must disclose purposes and legal bases, required versus optional data and consequences of refusal, categories collected, retention period or expected period, recipient categories, controller/DPO contacts, and statutory rights. ([PDPA sections 21-23](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

Therefore:

- "improve Tawan" and "future data science" are too broad to serve as the only descriptions of purpose. Define concrete uses such as conversation quality review, store-level sales forecasting, customer segmentation, or anonymous platform benchmarking.
- Store analytics and Duply platform analytics are different purposes and may have different controllers and legal bases.
- Raw chat retention, structured customer memory, order retention, consent logs, security logs, and anonymous aggregates need separate schedules.
- A privacy notice must describe AI extraction and profiling in plain language, including the categories inferred and how the store uses them.

The notice must state the retention period or an expected standard when an exact period cannot be fixed. Controllers must maintain a system to delete or destroy data after the retention period, when it is irrelevant or excessive, following a valid request, or after consent withdrawal, subject to statutory exceptions such as legal obligations and legal claims. ([PDPA sections 23(3), 33 and 37(3)](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

### Recommended retention design

Do not hard-code a single period across all stores. Build a policy engine with purpose, trigger, period, legal hold, disposition, approver, and evidence of deletion:

- raw conversation content: short store-configurable period justified by support/dispute needs;
- approved structured memory: until the relationship ends, the preference becomes stale, the customer corrects/deletes it, or the lawful purpose ends;
- unconfirmed AI inference: much shorter period, with automatic expiry if not confirmed or used;
- abandoned sales journey: short commercial follow-up period, then delete or anonymize;
- orders/payments/tax evidence: retain for the exact period required by applicable commercial, tax, accounting, and dispute rules, to be confirmed by Thai counsel;
- consent, objection, deletion, and security audit evidence: retain as needed to demonstrate compliance and handle claims, without retaining unnecessary message content;
- truly anonymous aggregate statistics: may be retained outside the personal-data lifecycle only after de-identification is robust and re-identification is not reasonably possible.

The deletion rule must reach replicas, caches, exports, vector stores, model context stores, logs, and backups through documented expiry or restricted-backup procedures. The Act requires a deletion system, but the precise technical deletion standard and backup treatment should be approved against any current PDPC instrument before launch. ([PDPA sections 33 and 37(3)](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

## 3. Profiling, VIP tiers, and automated recommendations

The PDPA applies to profiles and recommendations because they are personal data when tied to a person. The Act also requires personal data to remain accurate, current, complete, and not misleading, and gives the customer rights to correction, objection, restriction, and deletion in applicable cases. ([PDPA sections 32-36](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

The reviewed primary sources do not establish a general Thai equivalent of the GDPR's stand-alone prohibition on solely automated decisions. That absence is not permission to make opaque or harmful decisions. Tawan should:

- record whether each attribute was customer-stated, imported, staff-set, or AI-inferred;
- record source, confidence, first/last seen, confirmation, expiry, and model/rule version;
- show the owner why a tier or recommendation was produced;
- let authorized staff override it and customers correct facts;
- require human approval for discounts, adverse treatment, campaign launch, and other material commercial decisions;
- never use sensitive traits or proxies for them in scoring;
- test for systematic exclusion or unfair treatment;
- say "insufficient data" rather than fabricate confidence.

**Counsel required:** assess whether each VIP, propensity, churn, or next-best-offer model can rely on legitimate interests, requires consent, or creates consumer-law/fairness obligations beyond the PDPA. A formal data-protection impact assessment is recommended for large-scale behavioral profiling even though this memo does not identify a general DPIA mandate in the cited PDPA text.

## 4. Direct marketing, campaigns, consent, and opt-out

Customers have an express right to object at any time to processing for direct marketing. Once they object, the controller cannot continue that direct-marketing processing and must separate it from other data immediately. ([PDPA section 32(2)](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

Product requirements:

- maintain consent/objection by **store, customer, purpose, and channel**;
- make `STOP`, Thai-language opt-out, and dashboard opt-out effective immediately across scheduled and active campaigns;
- do not infer consent from a purchase, from consent given to another store, or from consent for order fulfilment;
- keep proof of wording, version, timestamp, channel, actor, and withdrawal;
- separate marketing permission from required transaction processing;
- enforce frequency caps, quiet hours, suppression lists, and campaign expiry;
- require the owner to approve products, eligibility, price/discount, dates, and audience rules before Tawan sends;
- ensure a special-price approval is customer-, product-, quantity-, and time-specific.

The PDPA does not state that consent is the only possible legal basis for every direct-marketing activity, but the unconditional objection right still applies. Thai counsel must determine the basis for each campaign and also review other applicable electronic-message, consumer-protection, and LINE platform rules, which are outside this PDPA-only research scope. ([PDPA sections 19, 24 and 32](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

## 5. Store and Duply roles

Roles follow actual decisions, not contract labels. A controller decides the purposes and means of processing; a processor acts on or for the controller's instructions. ([PDPA section 6](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

### Recommended role map

| Activity | Likely role |
|---|---|
| Store catalog, customer service, orders, store CRM memory, VIP rules, staff tasks, store campaigns | Store: controller; Duply: processor |
| Duply account administration, billing, fraud/security of its own platform, legal compliance | Duply: independent controller for these narrow purposes |
| Product telemetry containing identifiable customer/store activity, where Duply chooses the purpose | Duply likely independent controller for that activity; minimize or anonymize first |
| Cross-store identifiable or pseudonymous model training/benchmarking chosen by Duply | High-risk independent-controller activity; do not launch without separate basis, notice, contracts, and counsel approval |
| Irreversibly anonymized aggregate benchmarking | Outside personal data only if individuals are no longer directly or indirectly identifiable; document and test de-identification |

A processor must follow controller instructions, provide appropriate security, notify the controller of breaches, and maintain processing records. If a processor processes outside instructions, the Act treats it as controller for that processing. The controller and processor must have an agreement governing the processing. ([PDPA section 40](https://ratchakitcha.soc.go.th/documents/17082307.pdf)) Processor records must include controller/processor/DPO details, processing categories and purposes, foreign recipients, and security measures, and must be quickly available for inspection. ([Royal Gazette processor-record notification, B.E. 2565](https://ratchakitcha.soc.go.th/documents/17211325.pdf))

The data-processing agreement should cover documented instructions, purposes, data/subject categories, duration, confidentiality, access controls, subprocessor authorization and flow-down terms, rights assistance, deletion/return, audits, incident deadlines, international transfers, and evidence of compliance. Some of these terms are prudent contract implementation rather than verbatim statutory clauses and should be finalized by Thai counsel.

Because Tawan performs regular customer monitoring and may operate at scale, Duply and larger stores may cross the DPO threshold. Section 41 requires a DPO where core activity involves large-scale regular monitoring or sensitive data, as further specified by the PDPC. Confirm applicability before production and as volume grows. ([PDPA section 41](https://ratchakitcha.soc.go.th/documents/17082307.pdf); [Royal Gazette DPO notification, B.E. 2566](https://ratchakitcha.soc.go.th/documents/140D226S0000000001200.pdf))

## 6. Cross-store anonymized analytics

Per-store schemas and roles are an excellent security boundary, but they do not by themselves authorize cross-store use. Exporting data into a shared analytics schema is a new disclosure/use that must match the customer notice, store instructions, lawful basis, and contracts. ([PDPA sections 21, 24, 27 and 40](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

Use this architecture:

1. Calculate store-level measures inside the isolated store boundary where practical.
2. Remove direct identifiers and rare/free-text fields before export.
3. Aggregate using minimum cohort thresholds and suppress small cells/outliers.
4. Rotate or eliminate linkable customer keys; hashing a LINE ID alone is not anonymization.
5. Prohibit joining benchmark data back to a person or another store.
6. Test re-identification risk and record the method/version.
7. Keep identifiable training and analytics datasets disabled by default.
8. Obtain store contractual permission for anonymous benchmarking and describe it transparently, even where the final output is non-personal.

Whether a dataset is truly anonymous is fact-specific. If Duply or another party retains a practical route to re-identify a person, treat it as personal data. This follows from the Act's direct-or-indirect identifiability definition and its recognition of making data non-identifiable as an alternative to deletion. ([PDPA sections 6 and 33](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

## 7. Data-subject rights and product workflow

| Right | Clear requirement | Tawan implementation |
|---|---|---|
| Access and copy | A person may access and obtain a copy of personal data concerning them and learn the source of data obtained without consent; valid requests must be handled without delay and within 30 days. Refusal grounds are limited. | One verified request flow covering chats still retained, memories, preferences/inferences, tier, orders, campaigns, tasks, consent, and relevant decision outputs. |
| Portability | Applies where data is in a commonly usable machine-readable automated format and processed on consent or contract (plus any categories later prescribed). It must not harm others' rights. | Export applicable data as documented JSON/CSV; do not assume every internal aggregate or proprietary model is portable. |
| Objection | Applies to legitimate-interest/public-task processing, direct marketing at any time, and some research/statistics. | Immediate suppression for direct marketing; route other objections for documented review and record reasons for any refusal. |
| Erasure/anonymization | Applies when data is no longer necessary, consent is withdrawn without another basis, a valid objection succeeds, or processing is unlawful, subject to statutory exceptions. | Delete/anonymize across active stores, vectors, caches, exports and downstream processors; track legal holds and completion evidence. |
| Restriction | Applies during accuracy/objection review and in specified retention situations. | Lock the record from normal processing while preserving only permitted handling. |
| Correction | Data must be accurate, current, complete and not misleading. | Customer and staff correction flow; retain audit evidence without continuing to use superseded values. |

These rights and limits are in [PDPA sections 30-36](https://ratchakitcha.soc.go.th/documents/17082307.pdf). The official GPPC platform likewise presents access, portability, objection, erasure, restriction, and correction as operational request workflows. ([Official GPPC privacy policy](https://gppc.pdpc.or.th/privacy-policy/); [GPPC Plus rights-management description](https://register-gppc-plus.pdpc.or.th/))

### Derived data and charging for export

There are two separate questions:

1. **Customer/data-subject rights.** Section 30 broadly covers personal data concerning the requester; it does not limit access to raw facts the customer typed. A customer-linked preference, tier, score, or summary is therefore likely within access if it is personal data. Section 31 portability is narrower and may not require transfer of every inference, model, or anonymous aggregate. The Act does not clearly settle the exact boundary between access, portability, intellectual property, and derived analytics. ([PDPA sections 30-31](https://ratchakitcha.soc.go.th/documents/17082307.pdf))
2. **Store exit rights.** A corporate store is not itself a natural-person data subject for its customers' records. Its right to obtain service data is mainly contractual. However, if the store is controller and Duply is processor, Duply must process on the store's instructions and the store must remain able to comply with customer rights. Withholding existing customer-level personal data, memories, or decision outputs would create accountability and continuity risk. ([PDPA sections 6 and 40](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

**Recommended commercial boundary:**

- Included in the ordinary export/exit package: raw customer data still lawfully retained; structured memories; source/confidence metadata; preferences; customer tiers and overrides; customer-level scores actually used; orders, payments, tasks and statuses; consent/objection records; campaign contacts; audit history; and store catalog/knowledge. Supply in a usable documented format.
- May be paid: custom migration labor, bespoke reports not already stored, consulting, newly generated narrative analysis, data cleaning requested by the store, dashboard access after termination, or genuinely anonymous platform benchmarks.
- Never charge a customer to exercise a statutory right or make payment a condition for stopping marketing, correction, restriction, or deletion. Although section 30 does not expressly state a comprehensive fee rule, charging for mandatory rights performance is high risk and requires counsel approval.
- Do not use "Duply calculated it" as the only reason to withhold existing personal data. Protect model weights, source code, other stores' information, and true trade secrets separately while still providing the requester's personal data and meaningful stored outputs.

**Thai counsel decision required before terms are published:** define the precise no-charge access package, whether and when repetitive or manifestly excessive requests may incur cost, how proprietary inference is disclosed, and the distinction between a statutory request and paid B2B migration work.

## 8. Processors, subprocessors, and international transfers

Every LLM provider, embedding service, OCR service, cloud host, message service, observability tool, backup provider, and support tool must be assessed as a processor/subprocessor, independent controller, or non-recipient transit provider based on actual behavior. Maintain a live subprocessor register and do not send store data to a provider until its purpose, location, retention, training policy, security, deletion, incident process, and contract are approved.

Section 28 generally requires an adequate protection standard in the destination, subject to listed exceptions. Section 29 permits intra-group policies and appropriate safeguards capable of enforcing data-subject rights and effective legal remedies. The PDPC's 2023 notifications provide the operative criteria, including treatment relevant to overseas cloud services, binding corporate rules, and appropriate safeguards; both took effect in 2024. ([PDPA sections 28-29](https://ratchakitcha.soc.go.th/documents/17082307.pdf); [Royal Gazette section 28 notification, B.E. 2566](https://ratchakitcha.soc.go.th/documents/14915.pdf); [Royal Gazette section 29 notification, B.E. 2566](https://ratchakitcha.soc.go.th/documents/14913.pdf))

Product requirements:

- record data locations and transfer paths, including inference, logs, support, backups, and disaster recovery;
- prefer regional processing and no-training/no-retention API settings where available, but do not treat them as a substitute for a lawful transfer mechanism;
- execute controller-processor and subprocessor contracts before transfer;
- select and document the section 28/29 mechanism for each foreign recipient;
- expose recipient categories and transfer information in notices;
- ensure foreign recipients can support access, correction, deletion, objection, incident response, and audit evidence;
- block provider changes until legal/security review updates the register and notices.

**Counsel required:** determine whether each provider interaction is a cross-border transfer under the notifications, whether an adequacy route is available, which safeguards/contract clauses are valid, and whether an exception can lawfully be used. Consent to a non-adequate destination is an exception with notice requirements, not a convenient default architecture.

## 9. Security and breach obligations

Controllers must implement appropriate security, review it when needed or technology changes, protect data given to others, maintain deletion controls, and handle breaches. Processors independently owe appropriate security and must notify controllers of a breach. ([PDPA sections 37 and 40](https://ratchakitcha.soc.go.th/documents/17082307.pdf))

The PDPC security notification requires risk-appropriate organizational and technical measures, and physical measures where necessary, preserving confidentiality, integrity, and availability across processing. It calls for risk identification, prevention, monitoring, response/recovery, access control, user-access management, responsibilities, traceability/logging, awareness, and review as risks, technology, context, or processing change. ([Royal Gazette security-measures notification, B.E. 2565](https://ratchakitcha.soc.go.th/documents/17211326.pdf))

For Tawan this means, at minimum:

- one schema and least-privilege database role per store, with automated negative tests proving cross-store denial;
- encryption in transit and at rest as risk-appropriate engineering controls, plus managed keys and secret rotation;
- MFA for platform admins; scoped staff roles; time-limited, reason-coded support access; and immutable access/audit logs;
- tenant context derived server-side, never accepted solely from model output or client parameters;
- no direct model-to-database writes: validated tools enforce store, user, role, purpose, price, stock, and consent rules;
- malware scanning and isolation for uploaded files; prompt-injection defenses for ingested store knowledge;
- data-loss prevention for sensitive content and foreign-provider routing;
- tested backups, restore exercises, expiry handling, and store-level export;
- rate limits, monitoring, dependency patching, incident drills, and periodic access review.

A controller must notify the PDPC without delay and, where feasible, within 72 hours after becoming aware of a breach unless it is unlikely to risk individuals' rights and freedoms. High-risk breaches also require prompt notice to affected people with remediation guidance. ([PDPA section 37(4)](https://ratchakitcha.soc.go.th/documents/17082307.pdf)) The breach notification further requires assessment, containment, documented notification content, mitigation, and justification for delayed reports. ([Royal Gazette breach-notification rules, B.E. 2565](https://ratchakitcha.soc.go.th/documents/17233460.pdf))

Duply's processor contracts should require subprocessors to notify Duply immediately and Duply to notify the store on a much shorter internal deadline than 72 hours, leaving the controller time to investigate and meet its legal deadline. Maintain an incident register even where notification is not required.

## 10. Required product controls before real customer data

### Launch blockers

1. Create a processing inventory and Record of Processing Activities covering every field, inference, vector, log, recipient, purpose, basis, retention rule, and transfer.
2. Approve a role matrix for store-as-controller, Duply-as-processor, and Duply's limited independent-controller activities.
3. Execute store data-processing terms and a reviewed subprocessor/transfer schedule.
4. Publish layered Thai privacy notices for customer service, memory/profiling, marketing, store import, and Duply platform purposes.
5. Build purpose- and channel-specific consent/objection records with immediate suppression.
6. Build access, machine-readable export, correction, restriction, objection, deletion/anonymization, identity verification, deadline, and refusal-record workflows.
7. Implement configurable retention plus legal holds and verified downstream deletion.
8. Disable sensitive-trait inference and cross-store identifiable analytics by default.
9. Add human approval for discounts, campaigns, knowledge publication, and material customer treatment.
10. Complete tenant-isolation, authorization, prompt-injection, concurrency, export, deletion, and breach-response tests plus an independent security review.
11. Decide whether Duply and relevant stores require a DPO and publish the contact where required.
12. Obtain Thai counsel sign-off on the items listed below.

### Counsel sign-off questions

1. Is the proposed controller/processor split accurate for each feature, including platform telemetry and support access?
2. Which precise lawful basis applies to each memory, tiering, recommendation, fraud, analytics, and campaign purpose?
3. What direct-marketing and electronic-message rules beyond the PDPA apply to LINE OA campaigns?
4. What retention periods are required under tax, accounting, consumer, payment, construction, and limitation laws for each demo business?
5. Does Tawan's scale and regular behavioral monitoring require Duply or a store to appoint a DPO?
6. Which inferred/derived fields must be supplied under access, which are portable, and what fees, if any, are legally permissible?
7. What de-identification test is sufficient for cross-store anonymous benchmarks?
8. Which section 28/29 mechanism applies to each foreign LLM/cloud/subprocessor?
9. How should minors, sensitive incidental chat content, and deletion from backups be handled?
10. Are the store exit, grace-period, data return, and secure deletion clauses enforceable and fair?

## 11. Risk register

| Risk | Severity | Why | Required response |
|---|---:|---|---|
| Cross-store customer or product leakage | Critical | Breaches purpose, confidentiality, store trust, and potentially statutory security duties | Hard tenant isolation, server-side tenant context, negative authorization tests, audited support access. |
| Keeping all conversations indefinitely for unspecified future analysis | High | Conflicts with purpose limitation, minimization, notice, and deletion duties | Purpose-specific retention and deletion; anonymize only after tested de-identification. |
| Marketing after `STOP` or objection | High | Section 32 requires direct-marketing processing to stop | Immediate global suppression per store/channel and delivery cancellation. |
| Hidden sensitive inference | High | Section 26 imposes a stricter rule | Block sensitive profiling; explicit counsel-approved exception/consent only. |
| Charging for existing customer-level summaries or rights access | High | Summaries may be personal data within access; store controller needs them for accountability | Include stored personal/operational outputs in ordinary export; charge only for separate value-added work pending counsel. |
| Foreign LLM/cloud use without transfer mechanism | High | Sections 28-29 and notifications regulate overseas transfers | Transfer inventory, contracts, safeguards, notices, regional/no-training settings. |
| Duply reusing processor data for its own analytics without role change | High | Processing outside instructions makes Duply controller for that activity | Separate purpose/basis/notice or use irreversible anonymous aggregates. |
| Hallucinated price, stock, discount, or policy | High business and fairness risk | Produces inaccurate/misleading customer data and commercial harm | Database-grounded facts, validated tools, confidence gates, owner approval, audit trail. |
| Missing 72-hour breach capability | High | Statutory controller deadline | Detection, incident ownership, risk assessment, templates, drills, fast processor notice. |

## 12. Authoritative sources

- [Personal Data Protection Act B.E. 2562 (2019), Royal Gazette](https://ratchakitcha.soc.go.th/documents/17082307.pdf)
- [PDPC Notification on Security Measures of Data Controllers B.E. 2565 (2022), Royal Gazette](https://ratchakitcha.soc.go.th/documents/17211326.pdf)
- [PDPC Notification on Personal Data Breach Notification B.E. 2565 (2022), Royal Gazette](https://ratchakitcha.soc.go.th/documents/17233460.pdf)
- [PDPC Notification on Processor Records of Processing Activities B.E. 2565 (2022), Royal Gazette](https://ratchakitcha.soc.go.th/documents/17211325.pdf)
- [PDPC Notification on Cross-border Protection under section 28 B.E. 2566 (2023), Royal Gazette](https://ratchakitcha.soc.go.th/documents/14915.pdf)
- [PDPC Notification on Cross-border Protection under section 29 B.E. 2566 (2023), Royal Gazette](https://ratchakitcha.soc.go.th/documents/14913.pdf)
- [PDPC Notification on DPOs for Large-scale Regular Monitoring under section 41(2) B.E. 2566 (2023), Royal Gazette](https://ratchakitcha.soc.go.th/documents/140D226S0000000001200.pdf)
- [Official GPPC privacy policy](https://gppc.pdpc.or.th/privacy-policy/)
- [Official GPPC Plus compliance platform](https://register-gppc-plus.pdpc.or.th/)

## Product decision recommended from this research

Proceed with Tawan's per-store customer memory, VIP tiering, owner-approved campaigns, and anonymized cross-store BI only after the launch blockers above are implemented. Do **not** adopt the current proposed exit rule in which only raw data is included and existing Tawan-generated customer summaries require a special purchase. Include existing store-controlled personal and operational outputs in the standard export; monetize ongoing analytics, bespoke synthesis, migration assistance, and non-personal benchmark products instead. Obtain Thai counsel's written approval before publishing the final privacy notice, DPA, retention schedule, marketing workflow, international-transfer terms, or export pricing.
