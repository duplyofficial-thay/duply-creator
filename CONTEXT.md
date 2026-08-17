# Duply Creator Kit Context

The canonical language for Duply products and the Tawan commerce domain. Product and implementation documents should use these terms consistently.

## Platform

**Duply**:
The shared platform for identity, routing, agent execution, memory, knowledge, messaging, and infrastructure.
_Avoid_: Tawan platform, chatbot platform

**Duple**:
One isolated AI product registered on Duply, with its own persona, configuration, data schema, and channel identity.
_Avoid_: Bot, assistant account

**Agent**:
A named capability inside a Duple, such as `chat.reply`, `memory.noter`, or `knowledge.extract`.
_Avoid_: Duple, bot

**Tawan**:
Duply's standard shared commerce product and archetype implementation. Stores use separate Tawan Instances rather than sharing operational data.
_Avoid_: Store, tenant, universal customer brain

**Tawan Instance**:
A separately provisioned commerce Duple for exactly one Store Workspace, with a unique `duple_id`, schema, role, and channel identity while reusing the shared Tawan implementation.
_Avoid_: Code fork, multi-store schema

**Store Workspace**:
One business's isolated environment inside a Tawan Instance, including its schema, configuration, staff access, knowledge, customer data, and channel connections.
_Avoid_: Shared tenant, Tawan database

**Store Context**:
The verified identity and authorization of the Store Workspace for one operation. Every store-scoped action must receive or derive it before accessing data.
_Avoid_: Untrusted `store_id`, prompt instruction

## People And Access

**Customer**:
A natural person interacting with one Store Workspace through an authorized channel. The same person in another Store Workspace is a separate customer relationship.
_Avoid_: Global customer, universal profile, user

**Platform Administrator**:
A Duply operator permitted to support more than one Store Workspace through controlled, time-limited, audited access.
_Avoid_: Store owner, unrestricted superuser

**Store Owner**:
The person accountable for a Store Workspace's commercial rules, staff permissions, knowledge publication, campaigns, and exceptional approvals.
_Avoid_: Platform administrator

**Store Staff**:
A person authorized by a Store Owner to work in one Store Workspace. Capabilities such as sales, fulfilment, marketing, and knowledge editing are granted separately.
_Avoid_: Employee role as universal permission

**Capability**:
A specific permission granted to Store Staff, such as `sales`, `fulfilment`, `marketing`, `manager`, `knowledge_editor`, or `payment_review`. A Capability does not grant owner-only final approval.
_Avoid_: Job title, all-access staff role

Canonical role identifiers are `platform_admin`, `store_owner`, `store_staff`, and `customer`.

## Commerce

**Sales Journey**:
A customer's structured commercial progress from an expressed need through an outcome. It may exist without producing a Transaction.
_Avoid_: Conversation, order, task

**Transaction**:
The shared commercial record produced by a Sales Journey. A business module specializes it as an Order, Booking, Quotation, Project, Reservation, or Rental.
_Avoid_: Order when the business outcome is not an order

**Order**:
A Transaction for goods or prepared items that records confirmed line items, price snapshots, payment, and fulfilment.
_Avoid_: Cart, quotation, sales journey

**Booking**:
A Transaction reserving a service, resource, staff member, and time.
_Avoid_: Order, appointment request

**Quotation**:
A versioned commercial offer awaiting acceptance, often with quantity pricing, scope, validity, and approval history.
_Avoid_: Order, estimate after acceptance

**Project**:
An accepted construction or project-based Transaction with milestones, change orders, costs, progress payments, and delivery status.
_Avoid_: Long-running order

**Task**:
Actionable work requiring a person or Tawan to reach a tracked resolution. Messages and events are not Tasks unless they require action.
_Avoid_: Message, notification, conversation log

**Approval**:
An auditable authorization for a controlled change or action, including price exceptions, campaigns, payments, knowledge, and staff access.
_Avoid_: Chat confirmation without a record

**Catalog Item**:
A store offering that may be sold, prepared, booked, quoted, or reserved, such as a product, menu item, service, or material.
_Avoid_: Product when the offering is not a physical product

## Knowledge And Memory

**Store Knowledge**:
Approved facts and guidance about one business, such as catalog, prices, policies, hours, promotions, and operating rules.
_Avoid_: Customer memory, raw upload

**Knowledge Candidate**:
A proposed Store Knowledge change extracted from supplied material or unresolved work. It is not available to customer-facing answers until approved.
_Avoid_: Published knowledge, permanent memory

**Customer Memory**:
Structured information about one Customer within one Store Workspace, with source, confidence, validity, and confirmation metadata.
_Avoid_: Raw transcript, cross-store profile

**Interaction Event**:
A structured record of meaningful progress or action during a customer relationship, such as product interest, quotation, consent change, or transaction outcome.
_Avoid_: Full message archive

## Growth And Analytics

**Customer Tier**:
A transparent store-specific classification such as Standard, Regular, VIP, or Wholesale, produced by configured rules or an audited owner override.
_Avoid_: Hidden AI score

**Campaign**:
An owner-approved promotion with fixed products or services, commercial terms, audience rules, channels, dates, and contact limits.
_Avoid_: Autonomous AI promotion

**Store Analytics**:
Operational and business measures calculated for one Store Workspace from its own data.
_Avoid_: Cross-store customer analytics

**Anonymous Benchmark**:
An aggregate measure across Store Workspaces that cannot reasonably identify or be joined back to a Customer or individual store where confidentiality requires suppression.
_Avoid_: Hashed customer profile, pseudonymous benchmark

## Channels

**Channel**:
An authorized customer communication or commerce system, beginning with LINE OA.
_Avoid_: LINE-specific field in the shared commerce model

**Channel Adapter**:
The implementation that translates one Channel's identities, messages, media, and delivery results into Tawan's shared channel interface.
_Avoid_: Universal assumption that all channels support the same actions
