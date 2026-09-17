# TWN-10 — AI Workflow and Daily Insights

**Status:** Approved for documentation and implementation planning (2026-09-17)
**Phase:** 1 operational workflow; Pro/post-Phase-1 intelligence reserved
**Depends on:** TWN-05 Store Brain, TWN-07 Orders, TWN-08 Privacy/consent, TWN-09 Dashboard

## Outcome

Tawan responds naturally while turning meaningful conversation progress into
structured, auditable work. It recommends evidence-backed operational actions,
but Owner/Staff make accountable commercial decisions. The workflow uses the
Store Workspace timezone and business date at every schedule boundary.

## Conversation and event capture

For each inbound customer event, Tawan reads the current conversation and
workspace context, responds using approved Store Brain information, and records a
structured event when a meaningful field is known or changed. It sounds like a
curious Thai seller getting to know the customer, not like an interrogation:
one focused question at a time, no repeated question when the answer is already
known, and a concise confirmation before an important action.

Meaningful fields include customer intent, product/variant, quantity,
budget/price sensitivity, Order status, payment status, stock/restock request,
delivery details, follow-up date, preference, and consent status. Each event
records a source interaction ID plus a minimised/redacted excerpt or hash by
default—not a durable raw transcript—along with Store Workspace, customer,
field/value, confidence, confirmation state, actor/model/rule version, timestamp,
and resulting Order/Task/Memory/consent reference where applicable. Any excerpt
has the same purpose, audience, consent, retention, deletion propagation, and
legal-hold rules as TWN-08. A negative test must prove deleted raw content cannot
reappear through events, digests, recommendations, or exports.

Every captured field must have an approved purpose, audience, consent basis where
required, retention, and deletion behavior under TWN-08. Price sensitivity and
preference/demand signals are operational inputs only; they are not hidden
profiling or general training data.

Tawan may reply, create/update customer details, create/update an Order or Task,
create a low-stock or waitlist signal, and prepare a recommendation. It cannot
finalize payment, execute a refund, change price/discount, change subscription,
delete customer data, or alter Duply settings. Important facts are confirmed
before Order creation, payment/stock reservation, or durable-memory use.

If information is low-confidence, contradictory, stale, or missing, Tawan says
what is uncertain, asks a focused question or creates a human Task, and does not
guess. All actions are idempotent and re-check current workspace, Capability,
state, consent, and approval boundary at execution.

## Operating cadence

| Cadence | Behavior | Output |
| --- | --- | --- |
| Real-time | Reply, capture meaningful event, update current operational state | Customer message plus Order/Task/lead/stock/payment signal |
| Hourly | Refresh dashboard aggregates and stale-state checks | `last_updated_at`, aging queues, alert changes |
| Daily close | Finalise store-local business-day totals and unresolved-work snapshot | Daily digest input; no silent source-state change |
| Weekly review | Summarise evidence-backed trends, unresolved work, and recurring risks | Owner/Staff review; no advanced intelligence in Phase 1 |

## Daily owner digest

At a Store Owner-configured local time, the digest appears in Duply and the
authenticated management LINE. It covers sales/orders, inventory risk,
unresolved questions, leads/follow-ups, payment/cancellation work,
preference/demand signals, and up to three ranked recommended actions. Each
section shows current period, comparison or source where available, and a clear
empty state (`ไม่มีรายการ` / no items) when there is no activity.

Approved sample:

> สรุปวันนี้ของร้านค่ะ  
> สต็อกเสี่ยง: เสื้อเชิ้ตขาว เหลือ 2 ชิ้น (จำกัดขาย 3 ชิ้น) มีลูกค้ารอ 4 ราย  
> งานค้าง: ยืนยันสต็อกออเดอร์กลางคืน 2 รายการ  
> คำถามที่ยังไม่ได้ตอบ: 1 รายการ  
> แนะนำ 1: ตรวจสอบสต็อกเสื้อเชิ้ตขาวและกำหนดวันเติมสต็อก (หลักฐาน: สต็อกล่าสุด 09:00 น., ความมั่นใจสูง, หมดอายุ 18:00 น.)  
> กดดูรายละเอียดและมอบหมายงานใน Duply ได้เลยค่ะ

An authenticated management-LINE user may open only digest sections and source
details permitted by the recipient's Store Workspace Capability and assignment.
Sensitive payment, consent, preference, and customer details are redacted when
not needed for that action. Accepting creates/updates accountable work; it does
not execute an unapproved commercial action or send a customer message.

## Recommendation contract

Every recommendation contains:

- action and expected operational outcome;
- source records/links and a short explanation;
- confidence (`high`, `medium`, `low`) and evidence age;
- model/rule version, generated timestamp, expiry, and assignee;
- accept, dismiss, snooze, and reason/audit result.

Recommendations are limited to operational actions such as checking stock,
replying to a customer, reviewing payment, following up, or escalating. Ranking
uses approved operational evidence only; it never uses sensitive traits, hidden
spending scores, unauthorized Customer Memory, or cross-customer profiling.
After
expiry or dismissal, the recommendation is hidden unless materially new
evidence appears. A recommendation never changes price, discount, payment,
refund, subscription, or other commercial state by itself.

## Insufficient-data behavior

When evidence is not sufficient, Tawan writes **“ข้อมูลยังไม่เพียงพอ”** and
identifies the missing field, source, or confirmation needed. It may ask one
focused customer question, request Owner/Staff input, or create a Task. It does
not produce a numeric forecast, customer ranking, stock claim, or financial
recommendation from incomplete evidence. The digest includes an explicit
insufficient-data section rather than filling gaps with assumptions.

## Approval boundaries and safety

Tawan recommends and prepares. Store Staff act only within assigned Capability;
the Store Owner makes final Phase 1 payment decisions and approves commercial
exceptions. Refunds are prepared as idempotent requests and completed only by an
authorized human. Customer-facing messages use the approved Order/consent path;
Phase 1 does not send proactive sales campaigns. Management LINE authentication,
workspace binding, current Capability, state, confirmation, and idempotency are
rechecked for every action.

## Phase boundary

Phase 1 includes reply orchestration, structured capture, Orders/Tasks/signals,
hourly refresh, daily close, weekly evidence summary, and up to three
operational recommendations. Pro/post-Phase-1 may later add segmentation,
proactive campaigns, customer lifetime value, churn, demand forecasting, and
advanced intelligence, but this document does not commit their final behavior.

## Approved insufficient-data sample

> วันนี้ยังสรุปแนวโน้มสต็อกไม่ได้ค่ะ ข้อมูลยังไม่เพียงพอ เพราะยังไม่มีจำนวนสต็อกที่ยืนยันในช่วงเช้า 2 รายการ และยังไม่มีข้อมูลขายต่อเนื่อง 7 วันค่ะ  
> งานถัดไป: ยืนยันสต็อกใน Morning Confirmation และตรวจสอบข้อมูลขายใน Duply

## Acceptance gates

- Real-time events are captured without waiting for a nightly process.
- Every Order/Task/Memory/payment/stock transition has source, confidence,
  confirmation, actor/model version, and idempotent audit evidence.
- Low-confidence/conflicting input creates a focused question or human Task;
  unsupported insights are blocked.
- Digest appears in Duply and authenticated management LINE at store-local time,
  with empty/insufficient-data states and no more than three recommendations.
- Recommendations expire, dismiss, and reappear only for materially new evidence.
- Negative tests prove Tawan cannot finalize payment, execute refunds, change
  commercial state, cross workspace boundaries, or use customer LINE OA as a
  management channel.

## Out of scope

Autonomous commercial decisions, proactive campaigns, segmentation, LTV, churn,
demand forecasting, advanced intelligence, and any background action that alters
a store's commercial state without Owner authority.
