# TWN-09 — Admin Dashboard

**Status:** Approved for documentation and implementation planning (2026-09-17)
**Phase:** 1 minimal operational dashboard; Pro expands automation and analysis
**Depends on:** TWN-04 Workspace/access, TWN-07 Orders, TWN-08 Privacy/consent

## Product outcome

The dashboard gives each Store Workspace one clear daily operating surface. It
shows what needs attention, who may act, the evidence behind the item, and the
next accountable action. It is Thai-first with a user-selectable English option.
Duply is the full dashboard; LINE provides alerts and quick actions for work that
is safe to complete conversationally.

## Home view and priority

The Store Owner and authorised staff see the same operational structure, filtered
to their Store Workspace and individual Capabilities. The home view is ordered:

1. Low Stock
2. Morning Confirmation
3. Orders and Payments
4. Customers and Follow-up
5. Tasks and Approvals
6. Catalog / Store Brain
7. Settings and Access

Within operational alerts, high-value opportunities, payment review, urgent
approvals, unanswered customers, and overdue follow-up follow low-stock work.
Every card includes status, age, owner, evidence, risk/impact, and a next-action
button. Charts are secondary and never replace a queue or decision.

### Low-stock card

Each card shows product, current stock, Owner-approved safe selling limit,
overnight allowance, number of waiting customers, restock date if known, age of
the alert, and the recommended next action. A daily LINE draft can be reviewed
and sent by the responsible staff member. Pro may ask Tawan to draft the
customer statement and show the current status; the Owner-approved policy still
controls the final action.

### Morning Confirmation

Morning Confirmation is a required daily routine. It lists paid orders and
overnight reservations awaiting stock/fulfilment confirmation. Staff record one
of: confirm and fulfil; contact customer and prepare a refund request; communicate a specific
restock date; or escalate to the Store Owner. Every outcome creates an Order,
Task, or customer-contact record with a due time.

## Screens and permitted actions

| Area | Staff default | Owner |
| --- | --- | --- |
| Today / alerts | View assigned queues; complete permitted actions | View all; assign and override |
| Low Stock / Catalog | View and update assigned stock workflow | Configure limits, schedules, catalog, and access |
| Morning Confirmation / Orders and Payments | Confirm stock, inspect evidence, prepare/recommend payment decision, prepare an authorised refund request, contact customer | Final Phase 1 payment decision, refund completion/exception approval, and all Owner actions |
| Customers / Follow-up | View workspace customer details permitted by Capability; reply and complete follow-up | Full workspace view, assignment, export approval |
| Tasks / Approvals | Complete or prepare assigned work | Approve, reassign, override, close |
| Customer Memory / consent | Intake and prepare permitted service requests only | Approve exports/deletion and policy changes |
| Store Brain | Read or update assigned operational content | Manage source content and publication |
| Settings / Access | No Duply-level changes; only personal language/preferences | Manage staff Capabilities, subscription, Duply settings |

`workspace_admin` is a distinct workspace role: it may coordinate routine
operations and assigned staff work, but cannot self-grant access, transfer
ownership, approve final Phase 1 payment, approve legal/retention changes,
approve exports/deletion exceptions, change subscriptions, discounts, or bypass
RLS/entitlement. `store_owner` retains those owner-only controls.

Payment-review staff and workspace admins may inspect evidence, confirm stock,
prepare a recommendation, and contact the customer. Only the Store Owner may
make the final Phase 1 paid/rejected decision. This rule applies in the UI,
management LINE, backend service, and direct API; it is tested as a negative
authorization case.

Refunds are never executed by Tawan or a quick action. A permitted human may
prepare a refund request with Order, amount, reason, customer-safe message, and
idempotency key. The Store Owner or separately authorised human completes it in
the approved payment workflow; duplicate/replayed requests are rejected and the
final result is audited. Amount limits and any exception approval are configured
per workspace and cannot be widened by staff.

The Owner can grant or remove area-level Capabilities per staff member. Cost,
exports, deletion, subscription, Duply settings, discounts, and other commercial
exceptions are explicitly permissioned. No role can read another Store
Workspace. RLS and backend authorization remain the enforcement layer; hiding a
button is not security.

## LINE quick actions

LINE sends concise alerts and supports safe quick actions such as viewing low
stock, confirming stock, inspecting payment evidence, preparing a payment
recommendation, starting a refund request, communicating a restock date, and
escalating to the Owner. It does not finalize payment or execute a refund. If a menu is too
large, numbered commands are supported (for example, `1` for Low Stock and `2`
for Morning Confirmation). Destructive or ambiguous actions require a summary
and confirmation. Every command rechecks authenticated management-LINE binding,
workspace, current Capability, current state, confirmation, and idempotency at
execution. Customer-facing LINE OA can never invoke staff-management actions;
the full evidence and audit trail remain in Duply.

The “daily LINE draft” is an internal management draft by default. Customer-
facing transactional messages are sent only through the approved Order/consent
policy and are logged; Phase 1 does not send proactive sales campaigns.

## Time, freshness, and aggregation

The merchant selects country/location during setup. All cutoffs, overnight
windows, morning routines, due times, and business-day totals use that store
timezone. Operational queues update as events arrive. Hourly aggregates may be
slightly delayed and display their `last_updated_at`; stale data is never shown
as current. A daily close is store-local and does not silently alter source
orders.

## State handling in plain Thai

Every screen has explicit loading, empty, error, stale, and insufficient-data
states. Each state says what happened, when data was last updated, what the user
can do next, and how to contact the Owner/Duply when needed. Example empty copy:
“ตอนนี้ยังไม่มีรายการที่ต้องดำเนินการค่ะ” (There are no items requiring action
right now.) Error and stale states must not invite duplicate payment or order
actions.

## Audit and investigation

Material actions record Store Workspace, actor, Capability, timestamp in store
timezone and UTC, action, previous value, new value, reason, related customer/
order/task, and result. This includes Owner decisions, staff actions, exports,
deletion requests, support access, refunds, payment decisions, and permission
changes. Operational logs are retained for at least 30 days for investigation,
subject to TWN-08 legal/retention approval; sensitive values are minimised or
redacted. Audit records are append-only/tamper-evident where practical.

## Wireframe requirements approved for Phase 1

The first representative wireframe must include: Today, Low Stock, Morning
Confirmation, Orders and Payments, Customers and Follow-up, Tasks and
Approvals, Catalog/Store Brain, and Settings/Access. It must show Owner versus
Staff capability differences, Thai/English switching, store timezone, stale
timestamp, next-action controls, confirmation for risky actions, and an audit
link. Pro-only automation and richer dashboards are visibly separated.

## Acceptance gates

- Store and staff isolation passes positive and negative authorization tests.
- Staff/workspace-admin payment approval, refund execution, export/deletion, and
  discount attempts fail in UI, management LINE, backend, and direct API paths;
  only the Store Owner can finalize Phase 1 payment decisions.
- Each dashboard action creates or updates a traceable Task/Order/Approval/
  customer-contact record.
- Overnight paid orders appear in Morning Confirmation and cannot disappear
  without a recorded outcome.
- Low-stock and stale-state tests show correct limits, timestamps, and next steps.
- Owner Capability changes take effect on backend authorization, not only UI.
- Thai/English labels and all empty/error states are reviewed before build.
- TWN-08 privacy, retention, export, deletion, and consent boundaries remain
  enforced in every dashboard view.

## Out of scope

Advanced Pro campaigns, autonomous discounts, cross-store staff views, external
marketplace control panels, custom BI, and silent background changes to a store's
commercial state.
