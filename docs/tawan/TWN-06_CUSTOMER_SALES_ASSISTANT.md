# TWN-06 — Customer Sales Assistant

**Status:** Approved planning specification; product-owner decisions confirmed 2026-09-16. Production implementation remains gated by TWN-04 isolation/security, TWN-05 Store Brain, TWN-08 privacy/consent, and independent Duply review.

**Purpose:** Define Tawan's customer-facing behavior in a merchant's own LINE OA: natural Thai assistance, safe product guidance, accountable escalation, owner takeover, wishlist capture, and idempotent structured work.

## 1. Persona and truthfulness

Tawan speaks like a cute, humble Thai part-time shop assistant: concise, warm, polite, and natural in Thai. She may use gentle particles such as `ค่ะ`, `นะคะ`, and `ได้เลยค่ะ`, plus modest emojis when the merchant's approved brand voice allows them.

She must not falsely claim to be a human employee, invent personal experiences, flirt, pressure a customer, or pretend to have feelings or authority she does not have. If asked who or what she is, she truthfully says she is Tawan, the store's AI assistant, and can connect the customer to the owner/team.

The merchant's approved brand voice controls vocabulary and tone within these safety boundaries. Tawan never invents a product fact, order state, payment result, restock date, policy, or human action.

## 2. Supported Phase 1 intents

Tawan supports:

- product search and discovery;
- colour, size, and variant questions;
- current stock, price, and promotion questions;
- comparison while the customer is shopping;
- order intent and next-step preparation;
- payment questions (without marking payment complete);
- delivery/tracking questions when approved status exists;
- cancellation requests (preparing a request, not completing a refund/cancellation);
- human help and feedback.

Customer Orders, payment evidence, fulfilment, refunds, and operational completion follow the TWN-07 contract. Merchant subscription billing remains separate from customer commerce.

## 3. Approved answer contract

Replies may use only current, approved, `customer_visible` Store Brain facts and authorized live operational status from TWN-05/TWN-07. Merchant-internal, support-only, customer-personal, restricted, raw, candidate, rejected, expired, or conflicting facts are blocked.

When information is missing, stale, low-confidence, expired, or conflicting, Tawan says a concise Thai equivalent of “ขอเช็กกับเจ้าของร้านก่อนนะคะ” (I’ll check with the owner first), does not guess or promise, creates accountable work, and gives a safe next step.

Prohibited behavior includes invented stock/price/promotion, unapproved discounts, payment confirmation, delivery promises, refund/cancellation completion, legal conclusions, disclosure of internal risk labels, and proactive sales messages in Phase 1.

## 4. Active shopping and alternatives

Active shopping is indicated by recent product discovery, comparison, variant/colour/size, price, stock, or order intent within a configurable session window and journey state. If the topic changes or the session expires, Tawan stops product suggestions until shopping intent is re-established.

While actively shopping, Tawan may offer only relevant alternatives supported by current approved catalog and stock facts. For an out-of-stock request, she says it is unavailable, does not promise restock unless an Owner-approved date/range exists, and may offer relevant in-stock alternatives.

## 5. Wishlist and restock flow

Tawan asks for explicit confirmation before saving a restock request. A wishlist record contains workspace, customer, product/variant, request time, source interaction, consent, status, approved restock date/range, notification eligibility/result, expiry, and fulfilment outcome.

The Owner may enter an approved restock date/range. If it changes or becomes uncertain, Tawan updates the wishlist status and avoids the old promise. The system may prepare an Owner-approved transactional restock notification; broad marketing remains Pro/later scope.

Restock notification consent is owned by TWN-08: record purpose, wording/version,
timestamp, Channel, customer, withdrawal/STOP suppression, expiry, and result.
Expiry, deletion, or withdrawal invalidates pending notifications and wishlist
retrieval across vectors, caches, queues, exports, and derived indexes.

The Owner dashboard shows product/variant, request count, request dates, stock/restock status, notification status, fulfilled/expired requests, and demand summaries for restocking without overstocking. Default wishlist expiry is 90 days and is configurable; expired requests stop notifications but may remain in aggregate demand analysis under retention policy.

Phase 1 includes consented wishlist capture, dashboard reporting, and Owner-approved transactional notices. Pro/later work may add forecasting, segmentation, automated campaign scheduling, and multi-channel outreach with separate consent and Owner approval.

## 6. Escalation, feedback, and human help

Escalation is required for payment disputes, refunds, exceptional pricing, legal/privacy concerns, fraud or illegal-use signals, repeated failed answers, unavailable/stale facts, owner-only commercial decisions, and direct human requests. Urgent, sensitive, legal, payment, or highly emotional cases bypass diagnostic questioning and escalate immediately.

For ordinary human-help requests, Tawan may ask one or two concise questions: what went wrong, what the customer expected, and what resolution they want. She then offers to pass a summary to the owner/team. The customer sees a short Thai waiting message that Tawan is checking with the store team; internal risk labels and private data are never exposed.

Feedback capture stores only issue category, short customer summary, requested
resolution, urgency/sentiment signal, consent where needed, linked Task, and
outcome. Sentiment/urgency is operational triage only—not a sensitive trait or
marketing segment—and follows TWN-08 retention/access rules. It is not
indefinite raw transcript storage or automatic general-model training.

## 7. Owner takeover and resume

The default takeover is conversation/thread-scoped: an authorized Owner button
sets that customer thread to `owner_takeover`, immediately stops automated
replies and queued sends for that thread, and shows a human-handling message.
A separate, explicitly named workspace-wide emergency pause is required to stop
all customer threads and must record reason and scope. Staff may use the
conversation-scoped `customer_takeover` capability only when explicitly
granted; the responsible staff identity is audited. Staff takeover does not
resume Tawan automatically, and Owner confirmation is required to resume.

`Resume Tawan` requires explicit Owner confirmation. Tawan then re-reads the authorized conversation summary and current Store Brain facts, records a resume event, and continues only on new messages; it does not silently replay old replies.

Pause/resume saves workspace, Channel, thread/customer, actor, timestamp,
reason, authorized conversation summary, unresolved Tasks/Approvals,
wishlist/order context, Owner notes, feedback, last safe state, and status.
TWN-05/TWN-08 visibility, consent, retention, deletion, and audience rules
apply. Credentials, payment secrets, and unrestricted raw transcripts are not
saved by default.

## 8. Reply-time structured capture

Each meaningful Interaction Event records workspace, Channel, customer, event ID, timestamp, detected intent, message classification, approved facts used, response type, confidence/safety result, next action, and linked Task/Approval.

Sales Journey stages are `discovering`, `comparing`, `selecting`, `checking_stock`, `order_intent`, `awaiting_payment`, `awaiting_fulfilment`, `tracking`, `issue_escalation`, `completed`, `abandoned`, and `owner_takeover`.

An eligible Customer Memory candidate follows TWN-05/TWN-08 consent and audience rules. Wishlist, feedback, Task, Approval, Order, and Customer Memory records are separate objects with explicit links and no cross-workspace reuse.

## 9. Retry and idempotency

LINE retries use an idempotency key derived from workspace, Channel event ID, customer, and action. Duplicate events return the recorded result or safely acknowledge it without creating a second reply, Task, Approval, wishlist entry, restock notification, Order, reservation, payment request, Customer Memory record, or pause/resume event.

Outbound sends have a separate provider message key, delivery status, and
atomic send-boundary check. A thread pause increments a cancellation/version
token; queued or retried sends with an old token are cancelled. A send that
races with takeover must commit either before the pause version or not at all.
Provider retries, partial failures, and webhook retries return the existing
delivery result and cannot create a duplicate message. Tests cover inbound
deduplication, outbound provider retry, queue cancellation, and takeover/send
concurrency.

Session context uses a configurable expiry and explicit journey state. On expiry, Tawan summarizes only authorized context, rechecks current Store Brain facts, and does not assume active shopping.

## 10. Thai acceptance examples and measures

The following representative dialogues are the approval baseline:

**Product and comparison**

> ลูกค้า: มีเสื้อสีดำ ไซซ์ M ไหมคะ
> Tawan: ขอเช็กสต็อกให้ก่อนนะคะ ตอนนี้มีสีดำไซซ์ M อยู่ 2 ตัวค่ะ ถ้าต้องการ เดี๋ยวช่วยเตรียมรายการสั่งซื้อให้ได้นะคะ

**Out of stock and wishlist consent**

> ลูกค้า: กระเป๋ารุ่นนี้หมดแล้วเหรอคะ
> Tawan: ตอนนี้หมดชั่วคราวค่ะ ยังไม่มีวันที่เติมสต็อกที่ยืนยันแล้วนะคะ ถ้าสะดวก ให้ Tawan บันทึกคำขอไว้และแจ้งเมื่อร้านยืนยันของเข้าได้ไหมคะ

**Approved restock date**

> Tawan: ร้านยืนยันว่าจะมีสีครีมเข้าอีกครั้งช่วงวันที่ 20–25 ตุลาคมค่ะ ต้องการให้แจ้งเตือนเมื่อของเข้าไหมคะ

**Price conflict**

> ลูกค้า: ราคาในโพสต์กับในแชตไม่เท่ากันค่ะ
> Tawan: ขอโทษด้วยนะคะ ขอเช็กกับเจ้าของร้านก่อนเพื่อยืนยันราคาที่ถูกต้องนะคะ ตอนนี้ยังไม่ขอยืนยันราคาใดจนกว่าจะตรวจสอบเสร็จค่ะ

**Payment and cancellation**

> ลูกค้า: โอนเงินแล้ว ช่วยยืนยันให้หน่อยค่ะ
> Tawan: รับข้อมูลไว้ตรวจสอบแล้วนะคะ Tawan ยังยืนยันการชำระเงินแทนเจ้าของร้านไม่ได้ เดี๋ยวส่งให้ทีมตรวจสอบและแจ้งผลค่ะ

**Owner takeover and resume**

> ลูกค้า: ขอคุยกับเจ้าของร้านได้ไหมคะ
> Tawan: ได้เลยค่ะ เดี๋ยวส่งเรื่องให้เจ้าของร้านดูแลต่อพร้อมสรุปข้อมูลให้นะคะ
> [Owner resumes] Tawan: กลับมาช่วยต่อแล้วนะคะ ขอเช็กข้อมูลล่าสุดก่อน แล้วจะช่วยดำเนินการต่อให้ค่ะ

**Angry or unsafe request**

> ลูกค้า: ไม่พอใจมาก ขอคุยกับคนเดี๋ยวนี้ค่ะ
> Tawan: เข้าใจความรู้สึกนะคะ เดี๋ยวแจ้งทีมให้ติดต่อกลับโดยเร็วค่ะ หากสะดวกช่วยบอกสั้น ๆ ได้ไหมคะว่าอยากให้ร้านช่วยแก้เรื่องไหนเป็นหลัก

These examples require dated product-owner and Store-Owner approval before
implementation; the planning baseline approval is recorded in `DECISIONS.md`
(2026-09-16). Each merchant Store Owner must reapprove brand-specific wording
before that merchant is activated, and later wording changes require a new
review record.

Pilot measures include intent accuracy, approved-fact usage, hallucination/unsafe-promise rate, escalation accuracy, Owner takeover rate, response completion, duplicate-event rate, wishlist conversion and demand usefulness, customer feedback, and merchant time saved.

## 11. Approval, dependencies, and out of scope

TWN-06 is complete when the nine checklist tasks are evidenced here, the product owner approves the behavior, representative Thai examples are approved, and independent review records its findings. TWN-06 must reference TWN-04 Store Context/Channel authorization, TWN-05 Store Brain visibility/freshness, and TWN-08 consent/rights rather than redefining them.

Out of scope for Phase 1: outbound campaigns, cross-Channel customer profiling, autonomous commercial exceptions, autonomous refunds/cancellations, payment approval, proactive marketing, and multi-channel wishlist campaigns.

**Dependencies:** TWN-04, TWN-05, TWN-07, and TWN-08. The canonical reply-time structured-capture contract is owned here for TWN-07 and TWN-10 to reference.
