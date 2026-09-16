# TWN-07 — Orders and Store Operations

**Status:** Approved planning specification; product-owner decisions confirmed 2026-09-16. Production implementation remains gated by TWN-04 isolation/security, TWN-05 Store Brain, TWN-06 reply capture, TWN-08 privacy/consent, and Duply/legal review.

**Purpose:** Define a safe Order-to-outcome workflow for piece-based retail, including 24-hour selling without nightly manual approval, payment evidence, fulfilment failures, demand requests, and auditable human authority.

## 1. Order and request boundary

An Order is created only after the customer has an accepted item/variant, price snapshot, availability decision, and applicable fulfilment/payment terms. Before that point, Tawan creates an `order_request` or `waitlist_request`; it is not an Order and does not receive payment instructions.

The lifecycle is:

`draft → awaiting_confirmation → confirmed → stock_reserved → awaiting_payment → payment_review → paid → fulfilment → shipped → completed`

Side outcomes are `stock_issue`, `fulfilment_blocked`, `cancel_requested`, `cancelled`, `returned`, `expired`, and `payment_rejected`. Every transition records workspace, Order/request, actor, timestamp, reason, source snapshot, and elapsed time.

Customer-facing wording distinguishes “request received,” “store accepted,” “payment review pending,” and “fulfilment started.” Tawan never says the Owner confirmed an Order without a verified authenticated acceptance event.

## 2. Price, stock, and availability-to-sell

Approved merchant catalog/Store Brain sources are authoritative for product, variant, price, and stock. Price and stock are revalidated at acceptance and again before payment/fulfilment. The system never uses model inference as a stock or price source.

To support 24-hour automation, the merchant configures a recurring **availability-to-sell profile** rather than approving every Order manually. A profile contains active days and start/end time, allowed products/variants, maximum sellable quantity per item, cross-channel safety buffer, payment deadline, fulfilment cutoff and dispatch promise, blackout/closed periods, responsible Owner/staff capability, version, effective time, expiry, and pause status.

The profile uses the Store Workspace timezone and a period identifier for each
active window. Allowance resets only at the configured period boundary. The
Store Owner approves the initial profile and all material changes to quantity,
payment deadline, dispatch promise, fulfilment cutoff, blackout periods, or
financial/customer commitments. Staff may operate within an already-approved
profile only when their capability permits it; they cannot self-change those
high-impact settings. A trusted stock sync may reduce availability; without
one, the safety buffer protects other marketplaces and a reconciliation Task is
created.

Each acceptance performs an atomic reserve/release transaction keyed by
workspace, product/variant, period identifier, and idempotency key. Concurrent
Orders and cross-channel reductions cannot reserve beyond the allowance. Tests
cover concurrent acceptance, retry, release, timezone reset, and cross-channel
reconciliation.

Automatic renewal is allowed only within a pre-approved renewal window. At hard
expiry the profile stops and cannot silently renew; the Owner must approve a new
version. A stale or expired profile never accepts a new Order.

At 70% allowance use, notify the store; at 90%, warn and show demand risk; at 100%, stop automatic acceptance for that item. Existing accepted Orders continue under their recorded workflow. An expired or stale profile stops automatic acceptance and creates a stock-refresh Task; yesterday’s allowance is never silently reused.

## 3. Overnight operation and morning handoff

The recurring overnight profile supports 24-hour selling without a nightly human approval. Tawan may accept only within the configured allowance and payment/fulfilment terms. A morning digest reports overnight Orders, paid/unpaid status, remaining allowance, stock warnings, blocked fulfilment, cancellations, customer complaints, and Tasks requiring action.

The Owner-only **Pause automatic Orders** control stops new automatic acceptance and queued payment instructions for the selected product/profile or workspace. It records actor, reason, timestamp, and scope; it does not silently cancel accepted Orders.

## 4. Full capacity and demand requests

When allowance is full, stock is uncertain, or the profile is stale, Tawan creates a `waitlist_request` instead of an Order or payment request. The customer is told in Thai that the selling round is full, the request is not an Order, and no payment is due.

The request stores workspace, customer, product/variant, quantity, request time, preferred date, Channel, consent to follow-up, current stock/allowance status, expiry, and withdrawal/notification status. Requests are first-requested-first-served unless the customer chooses a later date; no sensitive traits or hidden spending score may change priority.

The Owner dashboard shows product/variant, request count, total requested quantity, first/latest request time, stock estimate, allowance, restock date, notification status, fulfilled/expired requests, and demand summary. The Owner may increase allowance, enter a restock date, offer a substitute, notify selected customers, or close a request with a reason. Default request expiry is 90 days and configurable.

When capacity becomes available, Tawan uses TWN-08 consent evidence and sends an approved transactional notice. The customer receives a new Order/payment deadline; a waitlist entry never silently becomes an Order. Forecasting, segmentation, campaigns, and multi-channel outreach remain Pro/later work.

## 5. Payment and PromptPay

Customer PromptPay QR/instructions belong to the merchant Order flow. Merchant subscription billing is Duply-controlled and separate; Tawan never treats a customer Order payment as a Tawan/Duply subscription payment.

Payment instructions are shown only after the acceptance/reservation gate, with the accepted item/price snapshot, recipient/store identity, expected dispatch window, cancellation/return terms, and payment deadline. The initial payment window is configurable with a 30-minute default; a 60-minute option must be explicitly configured and displayed.

If payment is not received by the deadline, the reservation expires, allowance is released, the Order becomes unpaid/expired, the customer is notified, and the event appears in the morning digest. A late payment requires a new acceptance or human review.

## 6. Payment-slip evidence and duplicate detection

A customer-uploaded slip is stored in private workspace-bound storage, malware-scanned, and treated as evidence—not proof of payment. OCR/AI may extract candidate amount, timestamp, bank reference, and Order fields, but cannot mark `paid`.

Only the `store_owner` makes the final Phase 1 `paid` or `payment_rejected`
decision. The `payment_review` capability may inspect evidence, extract
candidates, recommend an outcome, and create review work, but cannot finalize
payment. Duplicate detection compares exact evidence, normalized fingerprint,
amount, timestamp, bank reference, customer, and Order only within the same
Store Workspace. Cross-workspace slip/fingerprint comparison is disabled.
A probable duplicate or conflict immediately notifies the Store Owner/payment
reviewer and creates a reason-coded review Task. It never auto-rejects or
auto-approves.

## 7. Fulfilment failures, incidents, and liability boundary

Store-side outcomes are separately recorded: `stock_issue`, damaged item, supplier delay, incorrect price, unavailable variant, delivery limitation, suspected fraud, payment uncertainty, and other with required note. A blocked Order stops further automated promises, creates an urgent Store Task, notifies the Store Owner and Duply where appropriate, preserves evidence, and offers approved customer options: wait, substitute, cancellation request, or human help.

Before using automatic Orders, the merchant acknowledges that accepted Orders, source accuracy, stock, fulfilment, delivery, returns, refunds, and truthful store information are the merchant’s responsibility. Duply/Tawan remains responsible for platform defects, authorization failures, duplicate actions, security incidents, and errors introduced by the system. Final terms require legal review and must not claim to waive non-waivable consumer rights.

The immutable incident timeline preserves source/version, daily allowance, stock/price snapshot, acceptance event, payment state, notifications, staff actions, changes, retries, customer messages, and reasons. A reason-coded review assigns owner, severity, customer impact, remediation, and customer remedy. Repeated acceptance-then-no-stock behavior or “Tawan did it” disputes can suspend new paid Orders for the workspace and escalate to Duply risk review; the history is never rewritten.

If a suspected prompt injection, AI exploit, unauthorized action, or secret exposure occurs, stop affected automation, preserve logs/evidence, revoke affected sessions/keys, isolate the workflow/workspace, notify Duply security, and communicate only verified customer-safe information.

## 8. Tasks, SLAs, cancellation, and exceptions

Tasks cover fulfilment, delivery, tracking, returns, cancellation requests, stock issues, payment review, customer follow-up, reconciliation, and unresolved conflicts. Each Task has workspace, capability owner, severity, status, due time, start/end timestamps, elapsed duration, SLA target, breach/escalation, reason, and resolution.

The system tracks time in every Order state and queue: confirmation, reservation, payment upload/review, fulfilment, dispatch, delivery, return/cancellation, escalation, and final resolution. Targets are configured by task type and merchant support hours; the pilot measures p50/p90 duration and breach rate without promising an exact customer time unless configured.

Tawan can receive and prepare cancellation/return requests and communicate status. An authorized human completes the cancellation, refund, or return; no automated refund/cancellation occurs in Phase 1. Exceptional prices, discounts, and price changes always use Approval and cannot be invented by Tawan.

## 9. Safe customer updates and reporting

During payment, stock, fulfilment, or incident review, Tawan sends concise Thai updates saying the store is checking, without exposing fraud labels, internal risk signals, credentials, or private evidence. The customer receives a safe next step and a new deadline only after an authorized state change.

The dashboard reports Order funnel, time in each state, allowance utilization, blocked reasons, stock mismatch rate, payment-review duration, duplicate-alert rate, fulfilment SLA breaches, cancellation/return outcomes, unresolved Task aging, waitlist demand, and lost-sale/request trends.

## 10. Acceptance example and approval boundary

The approved Thai end-to-end baseline is:

1. The customer selects a black size-M shirt. Tawan revalidates the current
   price and the active overnight availability profile before accepting.
2. The system atomically reserves one unit under the store-local period
   identifier and shows the 30-minute payment deadline.
3. The customer uploads a PromptPay slip. Private storage and OCR produce a
   candidate only; a matching fingerprint alerts the Store Owner and creates a
   payment-review Task.
4. The Store Owner reviews the evidence and makes the final paid decision. A
   payment reviewer may recommend but cannot finalize it.
5. Fulfilment starts and the customer receives the approved Thai status update.
   If the store discovers no stock, the Order becomes `stock_issue`, automatic
   promises stop, evidence is preserved, and the customer is offered wait,
   substitute, or a cancellation request.
6. A cancellation/return request is prepared by Tawan and completed only after
   authorized human approval. The final completed or remedied outcome and every
   state duration appear in the dashboard.

On 2026-09-16 the product owner approved this planning baseline. Each merchant
Store Owner must approve the store-specific terms, availability profile,
payment wording, and customer messages before activation; later changes require
a new dated review record.

TWN-07 is complete when all nine checklist tasks are evidenced here, the product owner approves the behavior, the end-to-end example is approved, and independent Duply/security/privacy/legal review records its gates. Dependencies are TWN-04 Store Context/Channel authorization, TWN-05 Store Brain, TWN-06 reply capture, and TWN-08 consent/notification controls.

**Out of scope:** automated refunds, automatic cancellation completion, automatic payment approval, autonomous discounts/price changes, general marketplace stock synchronization, unrestricted web ordering, and production activation before the required review gates.
