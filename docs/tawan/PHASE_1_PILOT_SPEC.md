# Tawan Phase 1 Pilot Specification

**Status:** Approved product-owner direction on 2026-09-09. The active documentation sequence is `TWN-01` through `TWN-12` in `FEATURE_MAP.md`.

**Product owner:** wasuwat arriyathanasak (`arriyathanasak@gmail.com`). First / `duply.official@gmail.com` is consulted when requested by the product owner.

**Scope:** A controlled, free 30-day Tawan pilot planned for ten Thai small-to-medium social-commerce retailers selling physical items by the piece. The cohort size is reassessed if recruitment evidence requires it. Fashion/accessories remain representative scenarios, not a recruitment restriction.

**Relationship to the approved baseline:** This specification retains the product principles, privacy controls, roles, commerce concepts, and launch gates in `REQUIREMENTS.md`, `REFERENCE.md`, and `DECISIONS.md`. It adds the agreed Tawan Official onboarding and pilot-commercial model. It does not silently resolve the conflicting Store Workspace tenancy descriptions or obsolete automatic-payment semantics in the older design draft; both are explicit launch blockers.

## Problem Statement

Thai LINE-first retailers selling physical items by the piece, especially solo entrepreneurs and very small teams, lose time answering repeated product questions, checking stock, remembering customer preferences, following up on unfinished sales, and assembling an understandable view of daily operations. They need a sales and administration partner that is useful before they have the time or technical capacity to connect every marketplace or back-office system.

The merchant also needs confidence that an AI will not invent stock, price, promotions, delivery promises, or customer facts; act outside the merchant's authority; or leak a customer's information to another store. A customer needs normal service without being forced to accept optional profiling or marketing.

## Solution

Tawan Phase 1 is a LINE-first, assisted pilot consisting of two connected experiences:

1. **Tawan Official** is Duply's management channel. A prospective merchant can ask about Tawan, start onboarding, supply store materials, see the onboarding checklist, receive support, and later receive a payment link. Tawan Official and the Duply team verify the setup before a store goes live.
2. **A merchant's own LINE Official Account** is the customer-facing channel. Tawan represents that merchant in the merchant's own brand voice. It answers from approved Store Knowledge and current operational facts, records structured sales progress, captures permitted Customer Memory, proposes alternatives, and creates accountable Tasks and Approvals whenever a human decision is required.

For a confirmed retail Order, Tawan revalidates stock and price, creates a time-limited reservation, presents the configured PromptPay QR, records a submitted payment slip as protected evidence, and creates a payment-review Task. In Phase 1, only a Store Owner can record the final paid/rejected decision; model or OCR output never changes payment status by itself. Fulfilment, delivery, returns, and cancellation work remain accountable Tasks. Initial store data arrives through guided onboarding templates, approved uploads, CSV, or Google Sheets; approved website imports are limited to approved merchant domains. Direct marketplace/POS integration follows only after pilot evidence identifies the highest-value source.

The pilot is free for 30 days and planned for ten Store Workspaces, subject to recruitment evidence. Merchants who continue may receive a Standard payment link through Tawan Official after pilot feedback and purchasing-power review; no price is promised yet. Pro is a future higher-paid tier for special advanced capabilities; its exact features and price require separate product-owner approval. Campaign execution, proactive outreach, segmentation, and advanced customer intelligence are post-Phase-1 candidates and always need Store Owner approval.

## User Stories

1. As a prospective merchant, I want to ask Tawan Official what Tawan can do, so that I can decide whether it suits my business.
2. As a prospective merchant, I want to begin onboarding through LINE, so that I do not need technical knowledge to start.
3. As a Store Owner, I want a visible onboarding checklist, so that I know what remains before customer-facing activation.
4. As a Store Owner, I want to give business details, hours, brand voice, policies, products, prices, variants, and stock through guided forms or imports, so that Tawan understands my store.
5. As a Store Owner, I want imported facts to appear as Knowledge Candidates before publication, so that outdated or incorrect materials do not change customer-facing answers.
6. As a Store Owner, I want to approve final Store Knowledge and test Tawan before launch, so that customers receive accurate store information.
7. As a Store Owner, I want to connect my own LINE Official Account, so that my customers continue talking to my brand rather than a central marketplace account.
8. As Store Staff, I want only the Capabilities appropriate to my job, so that routine work is possible without granting owner-level authority.
9. As a Customer, I want Tawan to answer product, colour, size, price, promotion, and availability questions from current approved facts, so that I can shop confidently.
10. As a Customer, I want Tawan to say it is checking when a fact is missing, stale, or conflicting, so that I am never given a made-up answer.
11. As a Customer, I want Tawan to suggest relevant alternatives, colours, or sizes while I am shopping, so that I can find a suitable item.
12. As a Customer, I want normal service even when I decline optional preference memory or marketing, so that consent remains a real choice.
13. As a Customer, I want to choose separately whether the store may remember my stated preferences and whether it may send promotions, so that I control optional uses of my data.
14. As a Customer, I want to send STOP and have marketing cease immediately for that store and Channel, so that my objection is respected.
15. As a Customer, I want a practical way to view, correct, restrict, or delete applicable information about me, so that I can exercise my privacy rights.
16. As Tawan, I want to record an Interaction Event and Sales Journey while replying, so that sales progress is not lost if a conversation pauses.
17. As a Store Owner, I want Customer Memory to identify its source, confidence, validity, confirmation, and expiry, so that preference data remains useful and correct.
18. As a Store Owner, I want no Customer Memory, Customer Tier, recommendation, or campaign audience to use sensitive traits, so that the store avoids harmful and unlawful profiling.
19. As a Store Owner, I want Tawan to create a Task when a human must check a fact, review a payment, handle an exception, or take over a conversation, so that nothing falls through the gap.
20. As a Store Owner, I want Tawan to create a cancellation request but require human approval before cancellation is completed, so that irreversible commercial actions remain controlled.
21. As a Store Owner, I want a basic dashboard with current sales, stock risks, unanswered customers, pending work, and customer demand signals, so that I can act without reading every chat.
22. As a Store Owner, I want a daily LINE digest in plain Thai, so that I can understand what needs attention in minutes.
23. As a Store Owner, I want every recommendation to show its evidence, confidence, and an insufficient-data state where appropriate, so that I can judge whether to act.
24. As a Platform Administrator, I want time-limited, reason-coded, audited support access, so that I can help a merchant without becoming an untracked superuser.
25. As a merchant, I want my customers, Channel credentials, Store Knowledge, operational facts, and analytics isolated from every other Store Workspace, so that Tawan earns my trust.
26. As Duply, I want a pilot readiness gate before live customer data is accepted, so that legal, security, operational, and cost controls are proven before scale.
27. As a pilot merchant, I want a free 30-day trial followed by a clear Standard payment link, so that I can assess value before I commit.
28. As a product owner, I want measurable pilot results, so that Phase 2 integrations and Pro features follow real merchant demand rather than assumptions.
29. As a Customer, I want Tawan to create a confirmed Order with a time-limited stock reservation and a configured PromptPay QR, so that I can complete a purchase without stock being oversold.
30. As a Customer, I want a submitted payment slip to receive a human-reviewed outcome, so that I am not told payment is complete based only on an automated image reading.
31. As Store Staff, I want fulfilment, delivery, return, and cancellation work to be assigned and visible, so that a completed sale reaches the right outcome.
32. As a Customer, I want a machine-readable export of applicable information about me where the law requires it, so that I can use my rights without being trapped in a system.
33. As a Store Owner, I want an ordinary export of my store-controlled records, so that I can meet customer-rights duties and leave the service without losing existing operational data.
34. As a Platform Administrator, I want the canonical role identifiers and capability mapping enforced, so that legacy role labels cannot grant unintended authority.
35. As a Store Owner, I want Tawan to recover safely from an incident or failed operation, so that my customer data and business continuity are protected.

## Implementation Decisions

- Tawan remains one shared Duply commerce product. Each merchant receives an isolated Tawan Instance and Store Workspace, including independent customer relationships, staff access, Store Knowledge, Channel mapping, configuration, and operational data. The implementation must reconcile this approved model with the contradictory older single-schema design before any customer-facing implementation proceeds.
- Canonical roles are `platform_admin`, `store_owner`, `store_staff`, and `customer`; Store Staff receive explicit Capabilities. Any legacy owner/employee mapping is an audited migration/compatibility decision, not an authorization shortcut.
- Tawan Official is the management plane for discovery, assisted onboarding, support, configuration review, pilot activation, and later billing. It is not the shared customer-facing marketplace identity.
- A merchant's own LINE Official Account is the first complete customer Channel. The Channel Adapter must derive an authorized Store Context before any retrieval or action; the model, incoming message, and client request cannot select another store.
- Phase 1 begins with approved manual input, structured templates, CSV, and Google Sheets. Marketplace, POS, Instagram, Facebook, Shopee, TikTok, and Discord integrations are not prerequisites. Pilot evidence determines the first Phase 2 connector.
- Onboarding requires business/owner details; staff roles; merchant LINE connection; brand voice; operating hours; catalog, price, variant, and stock source; policies; consent settings; Store Owner acceptance of counsel-approved service/privacy terms; owner review of Store Knowledge; and a test conversation. Detailed shipping configuration is not required to begin the pilot, but manual fulfilment/delivery/return Task handling is.
- Store materials enter as protected Knowledge Sources with checksum, sensitivity, retention, uploader, and approved source/domain provenance. Approved website fetching is domain-restricted; uploads have type/size limits, malware scanning, protected storage, and no public access path. Sources become Knowledge Candidates with confidence, validity, conflicts, and expiry. Only Owner-approved published Store Knowledge may be used as a durable customer-facing store fact.
- Tawan may answer from approved facts, capture leads and expressed preferences, create a confirmed Order, make in-conversation product alternatives, surface current price/stock/promotion, and escalate work. It must create a Task and state that it is checking when operational data is absent, stale, uncertain, or conflicting.
- Cancellation is request-and-approval only in Phase 1. For an approved retail Order, stock/price revalidation, time-limited reservation, PromptPay QR creation, protected payment-slip intake, duplicate-evidence detection, and owner-only manual payment review are supported. A duplicate confirmed bank transaction reference can never pay two Orders; any probable fingerprint false positive needs a reason-coded owner resolution. Shipping/cancellation automation, refunds, exceptional prices, autonomous price changes, and autonomous payment completion are excluded.
- A reply produces the customer response and structured internal capture in the same orchestration: Interaction Events, Sales Journey updates, Tasks, Approvals, and eligible Customer Memory candidates. Retried inbound events are idempotent.
- A Customer relationship and Customer Memory are Store Workspace-specific. No global customer profile, cross-store matching, or identifiable cross-store model training is allowed. Any future cross-store benchmark must be genuinely anonymous, reviewed, and separately authorised.
- Operational data necessary to serve an inquiry/order uses the documented applicable lawful basis and privacy notice. Durable preference memory and direct marketing are optional, separately stated choices; refusal never blocks core service. Marketing consent/objection is stored by Store Workspace, Customer, purpose, and Channel. STOP is immediately enforced.
- The customer privacy experience has a short Thai notice, a full Thai privacy notice, distinct memory/marketing choices, a recorded versioned decision, verified-requester rights workflow for access, machine-readable portability where applicable, correction, restriction, deletion, and marketing objection. Rights handling defines identity verification, permitted requester/Store Owner authorization, minimised/redacted scope, deadlines, and auditable completion before releasing any export. Final wording, lawful bases, retention periods, the controller/processor agreement, international-transfer arrangements, and export terms require Thai counsel approval.
- Raw conversation content is encrypted and short-lived under a purpose-specific retention policy. Structured operational records, Customer Memory, consent, orders/payment evidence, security/audit evidence, and anonymous aggregates have separate documented retention and deletion rules. Tawan must not retain sensitive traits or use them for memory, segmentation, recommendation, or marketing by default.
- The dashboard is action-first and refreshes operational state in real time where possible, aggregates hourly, and closes store-local daily metrics once per business day. The daily summary includes sales/orders, low stock, unresolved questions, leads/follow-ups, payment/cancellation work, preference/demand signals, and no more than three evidence-backed actions.
- The pilot is planned for ten piece-based physical-retail merchants and is free for 30 days, subject to recruitment evidence. Standard follows by payment link through Tawan Official only after product-owner review of pilot feedback and purchasing power. Pro campaign and advanced intelligence features remain post-Phase-1 candidates pending separate approval. Tawan Official Instagram begins as Tawan product marketing; merchant showcases require an explicit opt-in commercial agreement in a later phase.
- A paid API call must be written to the project cost ledger immediately after it succeeds and before downstream parsing or processing.
- Real customer data may not enter production until credential rotation, tenant isolation/RLS and authorization controls, current runtime contracts, legal artifacts, retention/deletion controls, cost tracking, end-to-end tests, recovery/restore and incident-response evidence, and an independent engineering/security review are complete.

## Testing Decisions

- The primary external test seam is one **Merchant Pilot Journey**: Tawan Official onboarding through a Store Owner-approved activation, a customer inquiry on that merchant's LINE OA, a grounded answer or safe escalation, structured capture, owner action, dashboard update, and daily digest. This is the highest useful seam because it exercises identity, Store Context, authorization, knowledge, consent, customer reply, workflow, analytics, and notification without testing internal implementation details.
- Tests assert observable merchant/customer outcomes and safety guarantees, not which internal agent or table performed an action.
- The journey is run with a disposable fashion Store Workspace and synthetic customer data before any pilot. It covers the approved catalog/variant/stock source, an approved and rejected Knowledge Candidate, a correct answer, a missing/conflicting fact escalation, preference-memory choice, marketing refusal/STOP, customer confirmation, reservation/expiry, PromptPay QR, payment-slip intake and owner-only review, fulfilment/delivery/return/cancellation Tasks, an owner approval, a dashboard action, and a daily digest.
- Cross-store negative tests are mandatory at every boundary: Channel routing, retrieval, tool authorization, cache/search/vector access, analytics, staff access, exports, and support access. A customer or staff member for Store A must not discover facts about Store B even with identical product names or crafted prompts.
- Privacy tests verify that declining memory/marketing still provides service; consent is versioned and withdrawable; STOP updates the future-compatible marketing-suppression record without requiring Phase 1 campaign execution; verified rights requests become accountable work; access/portability exports are scoped, authorised, minimised, and auditable; retention/expiry removes data from active retrieval; and sensitive data is not turned into a memory or segment.
- Commercial safety tests verify stale facts do not produce promises; stock and price are revalidated at action time; reservations expire safely; duplicate/retried inbound events do not create duplicate work; protected payment evidence and duplicate fingerprint/bank-reference conflicts block unsafe completion; and Tawan cannot complete payment, refund, cancellation, exceptional discount, or campaign action without the defined human authority.
- Dashboard/digest tests use store-local business dates and show the evidence/confidence or insufficient-data state behind each recommendation. Existing local Python unit tests and syntax compilation remain the minimum local baseline; real LINE/runtime/database evidence is required before a card is marked complete.
- Before pilot activation, an independent engineering/security review must inspect the implemented end-to-end journey, the tenant boundary, authorization, privacy/retention/export behaviour, recovery/restore, incident detection/containment/escalation, and paid-call cost logging.

## Out of Scope

- Direct marketplace/POS/social integrations, including Shopee, Lazada, TikTok Shop, Facebook, Instagram, and Discord.
- Production-complete vertical modules beyond physical retail sold by the piece; fashion/accessories remain a representative test scenario rather than the only pilot category.
- Outbound campaigns, proactive customer outreach, RFM/segmentation, churn or lifetime-value models, demand forecasting, and advanced recommendation intelligence.
- Automatic payment approval, refunds, actual order cancellation, autonomous discounts, autonomous price changes, or other irreversible commercial actions.
- A consumer marketplace that aggregates multiple merchants under Tawan Official.
- Identifiable cross-store analytics, cross-store Customer Memory, or using merchant/customer data to train Duply models outside documented permissions.
- Final recurring-billing automation and a paid merchant showcase programme.

## Further Notes

- The Phase 1 acceptance targets are: ten pilot merchants; 80% onboarding completion; 14 consecutive useful daily summaries for each active merchant; at least 85% of routine replies needing no correction; at least two owner/staff hours saved per merchant each week; zero cross-store data leakage or unapproved commercial action; and 50% of active pilots converting to paid Standard.
- The no-go conditions are as important as the feature list: no production customer data before legal counsel approval and the existing security/runtime gates close.
- Phase 2 chooses marketplace/POS and additional Channel integrations from measured pilot demand. Phase 3 addresses reliable multi-channel operations, mature recurring billing, advanced intelligence, and any merchant showcase/brand-ambassador programme.
