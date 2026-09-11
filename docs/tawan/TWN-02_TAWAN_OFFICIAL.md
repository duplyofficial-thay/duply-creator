# TWN-02 — Tawan Official

**Status:** Approved decision basis; awaiting final review/close-out evidence (2026-09-11)

**Decision owner:** Store Owner/product owner (Arriyathanasak, `arriyathanasak@gmail.com`).

**Purpose:** Define Tawan Official as Duply's management-plane LINE experience for discovery, merchant qualification, onboarding coordination, support, and merchant subscription status. This document is an implementation and UX handoff; approval does not authorize a production LINE connection, real customer data, payment-provider spend, or database migration.

## 1. Product boundary

Tawan Official is the place where a prospective or existing merchant talks to Tawan about Tawan. A merchant's own LINE OA remains the customer-facing sales Channel. Customer Orders, customer PromptPay, payment slips, and customer support do not become Tawan Official merchant-billing messages.

The first discovery surface is the Duply main platform/marketplace, where Tawan and other approved Duples are described. A merchant can ask about Tawan, then select **Start with Tawan** and connect to Tawan Official. Tawan may link to an approved Duply topic or another Duple such as Thay or DOM when the merchant asks; the link-out does not enrol the merchant, transfer data, or change the current onboarding request.

No internal phase labels, private prompts, credentials, unrestricted agent data, customer conversations, Store Knowledge, Order records, payment evidence, or unapproved pricing claims are shown in discovery copy.

## 2. Journey and system ownership

| Stage | Merchant experience | Record/owner | Next action |
|---|---|---|---|
| `discovered` | Duply explains the approved Tawan value and CTA. | Duply marketplace | Choose Start with Tawan. |
| `handoff_pending` | Tawan link/QR and short explanation. | Duply creates immutable `handoff_id`. | Connect LINE and say “Hi”. |
| `connected` | Tawan identifies the handoff and explains Tawan, Duply, the team, and the process. | Shared handoff reference; Duply owns identity. | Read the service summary and continue. |
| `acknowledgement_pending` | Plain-Thai acknowledgement, privacy/service links, and support option. | Duply/Tawan acknowledgement evidence. | Acknowledge or ask a question. |
| `pilot_request_draft` | One qualification question at a time; partial answers are saved. | Tawan owns draft qualification; Duply owns routing. | Review the summary and submit. |
| `team_review` | “The Duply team is reviewing your request.” | Duply owns queue and accountable owner. | Wait, or provide requested input. |
| `needs_merchant_input` | The missing item and why it is needed are stated. | Tawan records request; Duply owns deadline. | Reply or use support. |
| `approved_for_onboarding` | Next onboarding link/action is shown. | Duply approval; Tawan starts Store Workspace setup. | Complete the onboarding checklist. |
| `onboarding_in_progress` | Tawan shows completed items and the next item. | Tawan owns Store Workspace onboarding. | Finish data, LINE OA, Store Knowledge, and test steps. |
| `activation_pending` | Tawan says activation is being checked. | Duply/team gate and audit record. | Wait for deterministic gate result. |
| `activated` | Tawan confirms service is ready and where to get help. | Duply entitlement + Tawan workspace. | Use the merchant's own LINE OA and dashboard. |

Exit states are `escalated`, `not_eligible`, `withdrawn`, and `closed`. A no-response merchant keeps a saved draft, receives limited team-configured reminders, then becomes waiting/paused; Tawan never spams or silently submits a request.

Duply owns platform identity, selected interests, the handoff, pilot request, team queue, subscription/payment-process status, and canonical paid-through time. Tawan owns detailed Store Workspace onboarding after handoff. Both systems reference the immutable `handoff_id`/onboarding request ID instead of copying the full record. The read path is a controlled service/API or approved view, not unrestricted direct database access. The current Supabase schema is planning evidence only; the conflicting shared-schema versus separately-provisioned tenancy designs remain a TWN-04 decision.

## 3. Qualification and copy rules

Required fields are business type, owner contact, current sales channel, store/team size, catalog or stock source, and main pain point. Optional fields are preferred contact, preferred language, expected launch timing, and existing merchant LINE OA. Tawan asks one clear question at a time, accepts “not sure”, saves partial answers, and shows a plain-Thai summary for correction before submission.

Approved Duply/Tawan product descriptions, Duple directory links, merchant identity, selected interests, onboarding/pilot status, approved service information, team escalation status, and Duply-supplied subscription status may be read. Secrets, credentials, prompts, unrestricted agent data, cross-store customer information, private Store Knowledge, Orders, payment evidence, and unapproved claims may not be read or stored.

For product improvement, use synthetic rehearsal and fully anonymous aggregate benchmarks only. Do not retain names, contact details, identifiers, raw conversations, Store Knowledge, Orders, payment evidence, or reconstructable merchant records for “training”. Any future real-data use requires product/privacy/legal approval.

Every status message contains: current stage, what is complete, the next action, whether payment or team review is pending, and a support option if blocked. Core wording is plain Thai; the exact final Thai copy is a UX/content deliverable and must be approved before implementation.

### Required Thai message catalogue

These are the approved baseline messages; UX may tune tone without changing the meaning or next action.

| Situation | Baseline Thai copy | Next action |
|---|---|---|
| Welcome/connected | “สวัสดีค่ะ นี่คือ Tawan ผู้ช่วยดูแลการขายและงานติดตามของร้านบน LINE เราจะพาคุณเริ่มทีละขั้น หากพร้อมพิมพ์ ‘เริ่มต้น’ ได้เลยค่ะ” | Start or ask a question. |
| Acknowledgement | “ก่อนเริ่ม ขอให้ตรวจสอบข้อมูลบริการและประกาศความเป็นส่วนตัว แล้วกดยืนยันเมื่อเข้าใจค่ะ” | Review and acknowledge. |
| Qualification | “ขั้นตอนนี้ขอข้อมูลร้านทีละข้อ ตอบ ‘ยังไม่แน่ใจ’ ได้ และแก้ไขได้ก่อนส่งคำขอค่ะ” | Answer the next field. |
| Draft saved | “บันทึกไว้แล้วค่ะ ตอนนี้ตอบไปแล้ว {done}/{total} ข้อ ขั้นต่อไปคือ {next}” | Continue or return later. |
| Team review | “ส่งคำขอแล้วค่ะ ทีม Duply กำลังตรวจสอบ คุณไม่ต้องส่งซ้ำ หากต้องการข้อมูลเพิ่มเราจะแจ้งในแชตนี้ค่ะ” | Wait or contact support. |
| Waiting for merchant | “ทีมต้องการข้อมูลเพิ่ม: {item} เพราะ {reason} กรุณาตอบเมื่อพร้อมค่ะ” | Provide the item. |
| Paused/no response | “เราพักคำขอไว้ชั่วคราวเพื่อไม่รบกวน หากต้องการไปต่อ พิมพ์ ‘ดำเนินการต่อ’ ได้ทุกเมื่อค่ะ” | Resume when ready. |
| Approved/onboarding | “คำขอผ่านแล้วค่ะ ขั้นต่อไปคือ {next_onboarding_step} เมื่อทำครบจะแจ้งผลการตรวจเปิดใช้งานค่ะ” | Complete the checklist. |
| Payment pending | “ยังไม่พบการยืนยันค่าสมาชิกจาก Duply จึงยังไม่เปิดใช้งาน กรุณาตรวจสอบลิงก์ชำระเงินหรือติดต่อทีมค่ะ” | Complete payment or ask support. |
| Activation pending | “ข้อมูลครบแล้วค่ะ ระบบกำลังตรวจเงื่อนไขเปิดใช้งาน หากพบข้อผิดพลาดทีมจะติดต่อกลับค่ะ” | Wait. |
| Activated | “เปิดใช้งานแล้วค่ะ คุณใช้ Tawan Official ดูสถานะและขอความช่วยเหลือได้ ส่วนการคุยกับลูกค้าให้ใช้ LINE OA ของร้านค่ะ” | Use the correct Channel. |
| Escalated/error | “เรื่องนี้ต้องให้ทีม Duply ตรวจสอบค่ะ บันทึกเรื่องเลขที่ {case_id} แล้ว สถานะถัดไปคือ {status}” | Wait for team status. |
| Cancellation scheduled | “ยกเลิกการต่ออายุแล้วค่ะ บริการยังใช้ได้ถึง {paid_through} ไม่มีการคืนเงินอัตโนมัติ” | Reactivate before expiry if needed. |
| Closed/expired | “สิทธิ์ใช้งานสิ้นสุดเมื่อ {paid_through} การดำเนินการใหม่หยุดไว้ หากต้องการกลับมาใช้บริการ ให้ติดต่อ Duply เพื่อเปิดการสมัครใหม่ค่ะ” | Contact Duply/reactivate. |

### FAQ boundary

| Question category | Tawan may answer | Escalate/redirect |
|---|---|---|
| What Tawan/Duply does | Approved product description, supported Phase 1 flow, and approved links | Unapproved roadmap, private implementation, or unconfirmed feature promise |
| Pilot eligibility | Approved pilot description, required qualification, free-pilot duration | Final eligibility exception or cohort decision |
| Setup/LINE | Connection steps, required checklist, known safe troubleshooting | LINE outage, authorization failure, or repeated technical error |
| Pricing/subscription | Approved Standard offer, payment handoff, current status, paid-through date | Unconfirmed pricing, refunds, disputed payment, or Pro entitlement |
| Customer Order/payment | Redirect to the merchant's customer-facing LINE or Duply support | All customer Order, PromptPay, QR, slip, refund, and delivery questions |
| Privacy/data | Approved short notice, data boundary, rights-request route, and STOP meaning | Legal interpretation, identity dispute, deletion/export exception, or suspected leakage |
| Technical/operational issue | Case number, safe next step, and visible escalation status | Model failure, security concern, data incident, or unresolved outage |
| Other Duples | Approved directory links and no-enrolment link-out | Automatic handoff, cross-Duple data transfer, or enrollment |

## 4. Team review, activation, and support

Escalate to a named Duply queue when qualification is missing or contradictory, a handoff is invalid/expired, payment is uncertain, LINE fails, a legal/privacy/data-rights question appears, security or data leakage is suspected, a model/tool fails, a complaint is received, a custom integration is requested, or any activation gate fails. Queues are Duply onboarding/support, payment, technical/runtime, legal/privacy, and product owner. One queue owner is accountable.

Merchant-visible escalation states are only `received`, `team reviewing`, `waiting for merchant`, `resolved`, and `unable to proceed`; sensitive diagnostics remain internal. Security, cross-store leakage, payment risk, and activation failure are high-priority incidents.

Existing owners and staff can ask operational questions or report problems in Tawan Official. Tawan first resolves the Duply account, Store Workspace, role, and Capability, then classifies onboarding/setup, Store Knowledge/catalog, LINE, model, Order/operations, payment review, staff access, privacy/data request, security, technical failure, or subscription status. Tawan gives the safe next action or creates a Task; it never grants access or changes a commercial exception from chat.

“Team-verified” means Duply owns the gate policy and audit trail; it does not require a human to click every routine activation. Automatic activation is allowed only for the regular paid path and only when every deterministic gate is true: payment confirmed by Duply, required qualification complete, valid Store Workspace assignment, merchant LINE OA verified, legal/privacy acknowledgement recorded, Store Knowledge approval recorded, test conversation passed, and no unresolved support, security, data, payment, or technical exception. A human team member must review exceptions, low-confidence/conflicting evidence, and any failed gate. The audit record stores each check, timestamp, source, automation version, and decision. Any missing, conflicting, or low-confidence check stops activation and creates a team task; self-service chat cannot bypass the gates.

## 5. Pilot, conversion, and entitlement

The free pilot is a planned 30-day pilot; any reimbursement to a tester is manual and external. There is no cashback or refund route in Tawan Official. The regular paid path is the only system payment path: Tawan explains the service, Duply presents the merchant subscription payment process, payment confirmation unlocks onboarding, and the team/gates activate the Store Workspace.

After the pilot, Tawan presents the approved Standard offer, hands off to a Duply-owned PromptPay or online payment provider such as Stripe, records follow-up and outcome, and reports whether the merchant continued, deferred, declined, or needs team contact. Standard price and Pro feature/price details remain uncommitted until pilot feedback, survey, willingness-to-pay, and purchasing-power evidence are reviewed.

Subscription state is tracked per paying merchant/Duply account and Store Workspace, not per end-customer. Duply is the canonical lifecycle owner. The minimum consumed status contract is `provider`, `subscription_id`, lifecycle `status`, `paid_through_at`, `cancel_at`, merchant timezone, provider event ID, and event idempotency key. Tawan displays status, paid-through date, scheduled cancellation, remaining active time, what will stop, and reactivation guidance. The state model is `active → payment_due/past_due → grace_period → suspended → closed`; a cancellation schedules end-of-term closure. The service remains active through the already-paid period and closes at the end of that paid-through day in the merchant Store Workspace timezone (Asia/Bangkok by default), with no automatic refund. At expiry, Tawan stops new merchant onboarding changes, customer-facing LINE replies, new API/tool actions, and queued outbound sends for that workspace; Tawan Official may still show closed status, support case history, and retention-approved records. Existing Orders, Tasks, audit evidence, and records are not bulk-deleted by shutdown and follow their own retention schedule.

PromptPay/Stripe details for merchant subscription status are Duply-owned and consumed by Tawan as status only. Customer Order PromptPay, QR, slip, and payment review remain in the merchant's Store Workspace flow. If a merchant asks Tawan Official about a customer's Order payment, Tawan redirects to the merchant customer-facing LINE or Duply support. Tests must prove no subscription-versus-customer payment status or data leakage.

## 6. UX/UI and engineering handoff

The UX/UI package must cover: Duply discovery card and CTA; Tawan Official welcome; acknowledgement; one-question qualification; review/edit summary; each onboarding status; team escalation; owner/staff support; Standard conversion/payment handoff; subscription status/cancellation; end-of-term closure; and blocked/error/insufficient-data states. Each screen/message must identify the responsible system, next action, and support route.

The engineering package must define the `handoff_id` contract, allowed read fields, lifecycle transitions, idempotency key for repeated LINE events, role/Capability check, audit events, entitlement timestamps/timezone, webhook duplicate handling, and the no-direct-DB/no-secret boundary. It must include QA scenarios for discovery, reconnect, partial qualification, correction, no response, team escalation, rejected activation, paid activation, payment uncertainty, cancellation, renewal, delayed/duplicate provider events, timezone end-of-term closure, reactivation, and customer Order-payment redirection.

## 7. Acceptance and out of scope

TWN-02 is accepted only when all eight task rows below are evidenced in this document, the UX/UI and data-contract handoff is reviewed by the Duply team, and the product owner records dated approval. No implementation starts from this document alone.

1. Prospective journey, FAQ boundary, and escalation are mapped.
2. Six required qualification fields and partial-save/review behaviour are defined.
3. Status machine and plain-Thai message requirements are defined.
4. Verification and deterministic activation gates are explicit.
5. Existing owner/staff support and escalation are explicit.
6. Standard conversion/payment handoff and outcome recording are explicit.
7. Customer Order/PromptPay is separated from merchant subscription billing.
8. Product-owner approval evidence is recorded.

Out of scope: customer-facing sales conversations, automated recurring billing, cashback/refund processing, automatic customer payment approval, unrestricted cross-database reads, shared customer identity, live production activation, final Standard/Pro pricing, final Pro entitlements, non-LINE connectors, real-data model training, and resolving TWN-04 tenancy design.

## Approval evidence

- Product owner: Arriyathanasak (`arriyathanasak@gmail.com`), approved the TWN-02 decision rounds and Q90–Q92 on 2026-09-11 in the working session; final close-out approval is recorded only after review and the dated Trello approval comment.
- Duply team review: required before coding; feasibility/estimate and UX/UI review remain a handoff gate.
- Close-out: link this document and its commit in all eight TWN-02 Trello cards. The final approval card must contain a dated product-owner approval comment.
