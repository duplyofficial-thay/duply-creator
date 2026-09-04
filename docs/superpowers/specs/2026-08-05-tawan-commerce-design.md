# Tawan (ตะวัน) — Commerce Archetype, Phase 1 Design

**Status:** Draft v3 — 2026-08-27 (multi-tenant single-schema model, replaces per-store-Duple assumption in v2)
**Owner:** arriyathanasak@gmail.com
**Scope:** Phase 1 (catalog + dual-role sales chat + checkout). Phases 2–4 are separate future specs.

---

## 1. Background

Duply is a platform for building **Duples** — AI products with an isolated Postgres schema, a dedicated LINE OA, and a shared persona/behavior split (`public.duply_duples.persona` = character, `{schema}.agent_profiles.system_prompt` = per-agent operational behavior). Existing Duples: Thay and Khun (finance archetype), Dom (lifestyle archetype). `archetype: commerce` is already reserved in `register/_template.yaml` but nothing has been built for it — no commerce tool pack, no commerce schema tables. This spec is the reference implementation.

Tawan is a **multi-tenant** commerce AI: one `tawan` Duple, one `tawan_ai` schema, serving multiple stores simultaneously. Each store is a row in `tawan_ai.stores`, not a separate Duple instance. This differs from Thay/Khun (one Duple per finance product) — Tawan acts more like a SaaS product where many SMEs are tenants inside a single schema.

**Core platform rule that applies throughout:** LLM proposes → Python decides → DB writes. The model never writes to Supabase directly; every mutation goes through a validated Python tool.

---

## 2. Taxonomy

Terms used throughout this doc and all related specs. Use these exactly — do not invent synonyms.

| Term | Definition |
|------|------------|
| **Duply User** | A person registered in the Duply platform via LIFF auth. Has a `duply_id`. Typically a store owner or staff member using Channel 1. |
| `duply_id` | Platform-issued user ID (e.g. `A0002`). Unique per person across all Duples. Primary key in `user_profiles`. |
| **Store** | A business entity using Tawan. Has a `store_id`. Shares `tawan_ai` schema with all other stores — tenant isolation is row-level by `store_id`, not schema-level. |
| `store_id` | Stable identifier for a store (e.g. `papaya_fashion`). Primary key in `tawan_ai.stores`. Foreign key on all commerce tables. |
| **Store Owner** | A Duply User with `owner` in `user_profiles.roles` linked to a store. |
| **Store Staff** | A Duply User with `employee` in `user_profiles.roles` linked to a store. |
| **Store Customer** | A person who contacts the store via Channel 2 (store's own LINE OA, Shopee, etc.). Does **not** need a `duply_id`. Identified by `store_id` + `platform_user_id` + `platform_type` in `store_customers`. |
| **Channel 1** | Tawan Official LINE OA (Duply-owned). Store owners and staff use this to manage their store — approve knowledge, review analytics, handle staff access. Uses standard Duply domain stack. |
| **Channel 2** | Store-owned channels (LINE OA, Shopee, etc.). Store customers use these for sales interactions. Tawan runs on behalf of the store on these channels. Each store registers its own credentials in `tawan_ai.stores`. |
| **Store Resolver** | Middleware that maps an inbound Channel 2 request (by `platform_type` + `channel_id`) to the correct `store_id` within `tawan_ai`. No schema switching needed — always `tawan_ai`. |
| **Tawan Brain** | A store's knowledge base — products (structured in `products`), policies/brand story (RAG via `knowledge_entries`). Per-store, scoped by `store_id`. |

---

## 3. Product goal

Tawan is a single AI persona operating across two channels, serving many stores inside one schema:

**Channel 1 — Tawan Official OA (management plane)**
Store owners and staff talk to Tawan here. Same architecture as Thay/Khun — Duply-owned OA, standard `duply_id`-based identity, full Duply domain stack (memory, reach, knowledge). The persona acts as **เลขา (secretary)** to internal users: operational queries, inventory commands, analytics lookups, knowledge approval.

**Channel 2 — Store's own channels (commerce plane)**
Store customers talk to Tawan here via the store's own LINE OA, Shopee account, or other platforms. Tawan acts as **เซลส์ (salesperson)**: catalog Q&A, order intake, checkout, payment verification, 24/7. Each store registers its credentials in `tawan_ai.stores`; the Store Resolver loads them at request time.

One `tawan` Duple serves all stores. A new store onboards by inserting a row in `tawan_ai.stores` — no new Duple, no new schema, no new container.

---

## 4. Persona

Shared character (`public.duply_duples.persona`), tone split per channel:

> **ตะวัน**: พลังงานแบบแดดเช้า — สดใส กระตือรือร้น แต่ไม่จ้าจนแสบตา เชื่อถือได้เหมือนพระอาทิตย์ขึ้นทุกวัน ไม่มีวันลา ไม่มีวันหยุด จำรายละเอียดร้านได้แม่น ไม่มโนไม่เดา — ถ้าไม่รู้ จะบอกตรงๆ แล้วไปหาคำตอบมาให้ ให้ความรู้สึกเหมือนมีคนที่แคร์ร้านนี้จริงๆ อยู่เคียงข้างตลอด 24 ชม.

- **Channel 1 / `chat.staff`** — efficient, proactive, data-forward. Surfaces what owner/staff need before they ask.
- **Channel 2 / `chat.reply`** — warm, consultative, patient. Honest about stock/delivery, closes when the customer is ready, never pressures.

"Never makes things up — says so and goes to find out" is a core character trait, not a bolted-on feature.

---

## 5. Architecture decisions

| Decision | Choice | Why |
|---|---|---|
| Deployment model | One `tawan` Duple, one `tawan_ai` schema, multiple stores as rows (`store_id`) | SaaS model — onboarding a new store = one DB row, not a new container+schema. Simpler ops. |
| Tenant isolation | Row-level by `store_id` FK on all commerce tables | Schema-per-store is overengineering at SME scale; `store_id` + application-layer enforcement is sufficient |
| Channel 1 identity | `duply_id` via standard LIFF auth | Store owners are Duply Users — reuse existing identity |
| Channel 2 identity | `store_id` + `platform_user_id` + `platform_type` in `store_customers` (not `duply_id`) | Store customers have no Duply account; LINE `userId` is stable per OA |
| Channel 2 credentials | Stored per-store in `tawan_ai.stores` (encrypted), not in `.env` | Can't scale to N stores with env files; Store Resolver fetches at request time |
| Channel 2 routing | Single shared endpoint; Store Resolver maps `channel_id` → `store_id` within `tawan_ai` | No schema switching needed — always `tawan_ai` |
| Agent dispatch | Role-check before context_builder: `duply_id` → `user_profiles.roles` for Ch1; `store_customers.roles` for Ch2 | Two profiles (`chat.staff` vs `chat.reply`) selected by caller's role, not channel directly |
| Memory — Channel 1 | Standard noter/dream pipeline (same as Thay) | Owner/staff interactions need rich memory — investment in relationship over time |
| Memory — Channel 2 | In-loop `update_memory` tool (parallel with `reply_user`) — no noter process | Commerce facts are explicit ("ไซส์ M", "สีแดง") — no LLM extraction pass needed; parallel tool calls eliminate extra loop |
| Catalog data | `products` (SQL, hard facts) + `knowledge_entries` (RAG, soft facts) | Hard facts must never be hallucinated; soft facts benefit from flexible retrieval |
| Checkout | Full checkout + payment (not just handoff) | User requirement |
| Payment | PromptPay QR + slip + vision verify + staff fallback | Standard Thai SME pattern; no payment gateway KYC needed at SME scale |

---

## 6. Data model

### Standard Duply tables (provisioned automatically — unchanged)

`user_profiles` — Channel 1 users only (store owner + staff, keyed by `duply_id`)
`user_memories`, `interact_log`, `agent_profiles`, `knowledge_entries` — same as all Duples

### Commerce tables (new, designed by store owner — schema TBD by creator)

The exact column design for commerce tables below is **pending the store owner's input** — they are deciding what data to track per store/customer/product/order. The structure below is a reference skeleton; final columns may differ.

```sql
-- BEGIN COMMERCE

-- Store registry — one row per store, holds Channel 2 credentials
CREATE TABLE tawan_ai.stores (
    store_id             TEXT NOT NULL PRIMARY KEY,
    name                 TEXT NOT NULL,
    platform_type        TEXT NOT NULL DEFAULT 'line',
    channel_id           TEXT NOT NULL,               -- LINE destination / Shopee shop ID
    channel_secret_enc   TEXT NOT NULL,               -- encrypted LINE_CHANNEL_SECRET
    channel_token_enc    TEXT NOT NULL,               -- encrypted LINE_CHANNEL_ACCESS_TOKEN
    status               TEXT NOT NULL DEFAULT 'active',
    created_at           TIMESTAMPTZ DEFAULT now()
);
CREATE UNIQUE INDEX idx_stores_channel ON tawan_ai.stores (platform_type, channel_id);

-- Channel 2 customers — NOT Duply Users, no duply_id
-- Unique per store: same LINE userId on two different stores = two separate rows
CREATE TABLE tawan_ai.store_customers (
    id               UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    store_id         TEXT NOT NULL REFERENCES tawan_ai.stores(store_id),
    platform_type    TEXT NOT NULL,                    -- 'line' | 'shopee' | ...
    platform_user_id TEXT NOT NULL,                    -- LINE userId, Shopee buyerId, etc.
    display_name     TEXT,
    roles            TEXT[] DEFAULT '{}',              -- 'customer' | 'employee' | 'owner'
    preferences      JSONB DEFAULT '{}',
    tier             TEXT DEFAULT 'standard',
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (store_id, platform_type, platform_user_id)
);

CREATE TABLE tawan_ai.customer_memories (
    id               UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    store_id         TEXT NOT NULL REFERENCES tawan_ai.stores(store_id),
    customer_id      UUID NOT NULL REFERENCES tawan_ai.store_customers(id),
    topic            TEXT NOT NULL,
    summary          TEXT NOT NULL,
    importance       INTEGER DEFAULT 5,
    status           TEXT NOT NULL DEFAULT 'active',
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

-- Products — schema TBD by store owner
CREATE TABLE tawan_ai.products (
    id                   UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    store_id             TEXT NOT NULL REFERENCES tawan_ai.stores(store_id),
    sku                  TEXT NOT NULL,
    name                 TEXT NOT NULL,
    -- ... columns TBD by creator ...
    UNIQUE (store_id, sku)
);

-- Orders — schema TBD by store owner
CREATE TABLE tawan_ai.orders (
    id               UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    store_id         TEXT NOT NULL REFERENCES tawan_ai.stores(store_id),
    customer_id      UUID NOT NULL REFERENCES tawan_ai.store_customers(id),
    -- ... columns TBD by creator ...
);

CREATE TABLE tawan_ai.payment_slips (
    id             UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    store_id       TEXT NOT NULL REFERENCES tawan_ai.stores(store_id),
    order_id       UUID NOT NULL REFERENCES tawan_ai.orders(id),
    -- ... columns TBD by creator ...
);

-- END COMMERCE
```

> **Note:** `store_id` FK on every commerce table is non-negotiable — it is the tenant boundary. All queries must include `WHERE store_id = ?` enforced at the tool layer, never relying on caller-supplied trust.

---

## 7. Tool packs (commerce archetype)

**`commerce.generic` pack** — available to both agents:
| Tool | Purpose |
|---|---|
| `search_catalog(query, category?)` | Keyword/category product search, scoped to caller's `store_id` |
| `get_product(sku_or_name)` | Full product detail: price, stock, variants, images |
| `check_stock(sku_or_name, variant?)` | Quick stock check |
| `create_order(items, customer_info)` | Python validates stock at write time, writes `orders` row |
| `get_order_status(order_id)` | Look up an existing order |
| `reply_user(message)` | Send reply to user and terminate loop (Channel 2 only) |
| `update_memory(field, value)` | Write to `store_customers.preferences` or `customer_memories` in-loop (Channel 2) |

**`commerce.staff` pack** — `chat.staff` only, gated by `employee`/`owner` role:
| Tool | Purpose |
|---|---|
| `get_low_stock()` | Products below `low_stock_threshold`, scoped to store |
| `get_sales_summary(period)` | Sales figures for day/week/month |
| `update_stock(sku, delta_or_new_qty)` | Inventory adjustment |
| `update_price(sku, new_price)` | Price change |
| `verify_payment_slip(slip_id, decision)` | Manual confirm/reject for `manual_review` slips |

All tools receive `store_id` from context, never from the LLM — the model cannot switch stores.

---

## 8. Agent architecture

| | `chat.reply` (Channel 2 default) | `chat.staff` (Channel 1 + Ch2 employee) |
|---|---|---|
| Persona mode | เซลส์ | เลขา |
| Reached by | Store customers (any `store_customers.roles`) | Duply Users via Ch1; or Ch2 users with `employee`/`owner` role |
| Tool packs | `generic` + `commerce.generic` | `generic` + `commerce.generic` + `commerce.staff` |
| Memory pipeline | In-loop `update_memory` (parallel with `reply_user`) — no noter | Standard noter/dream (Channel 1 management interactions) |
| Context builder | `duples/tawan/chat/reply/context_builder.py` — customer profile, order history | `duples/tawan/chat/staff/context_builder.py` — today's low-stock, pending manual-review slips |
| Identity key | `store_customers.id` (via `store_id` + `platform_user_id`) | `duply_id` |

### Channel 2 agent loop (commerce turn)

```
inbound (LINE webhook / Shopee event)
  ↓ Store Resolver: channel_id → store_id (query tawan_ai.stores), decrypt credentials
  ↓ verify signature (store's secret, fetched from stores row)
  ↓ lookup/create store_customers row (store_id + platform_user_id)
  ↓ role-check → chat.reply or chat.staff
  ↓ context_builder: customer profile + order history + active memories + catalog context
  ↓ agent_loop (store_id injected into every tool call):
       [get_product / check_stock / create_order / ...]  ← tool calls
       [reply_user("...") + update_memory(...)]          ← parallel final step
  ↓ reply sent, memories written — turn complete, no noter needed
```

### Staff onboarding (Channel 2, self-serve)

1. Staff sends fixed phrase (`สมัครพนักงาน`) → Tawan sets `store_customers.roles = ['pending_staff']`, pushes owner notification via Channel 1
2. Owner replies `STAFF APPROVE <name>` on Channel 1 → `pending_staff` swapped to `employee`

---

## 9. Platform dependencies (blocking — Duply team)

| # | What | Why blocking |
|---|------|-------------|
| 1 | **Store Resolver** — new shared middleware | Channel 2 can't route without it |
| 2 | **`tawan_ai.stores` migration** | Credentials must be in DB before Store Resolver can work |
| 3 | **Role-check dispatch** in `reply_flow.py` before context_builder | Channel 2 must select `chat.reply` vs `chat.staff` by role; today reply_flow routes to one fixed agent_id |
| 4 | **`reply_user` tool + loop termination** | Agent loop currently terminates on natural output; `reply_user` as terminating tool call is a new loop variant |
| 5 | **Parallel tool call support** for `update_memory` | `reply_user` + `update_memory` must fire in the same generation step; confirmed: Claude ✅, GPT ✅, Gemini ✅ |

**Commerce table schema** (`products`, `orders`, `payment_slips`, `store_customers` detail columns) — pending store owner input. `tawan_ai.stores` and the `store_id` FK skeleton above are not blocked.

---

## 10. Sales conversation flow

**Channel 2 / เซลส์ mode:**
1. Customer asks → `search_catalog`/`get_product` → real price/stock, never a guess
2. Customer commits → `create_order` (Python re-checks `stock_qty` at write time)
3. `reply_user(order_summary + PromptPay QR)` + `update_memory(last_order_context)` — parallel
4. Customer sends payment slip → vision reads amount/ref/bank → matched against pending order
5. Clean match → `orders.status = paid`, staff notified. No match → `manual_review`, customer told to wait

**Channel 1 / เลขา mode:**
- "วันนี้ขายไปเท่าไหร่" → `get_sales_summary`
- "อะไรใกล้หมด" → `get_low_stock`
- "มีสลิปที่ต้องเช็คไหม" → lists `manual_review` rows → `verify_payment_slip`

**Order expiry:** orders left `awaiting_payment` past 24h auto-expire via lightweight cron (same pattern as `reach_cron`).

---

## 11. Error handling & edge cases

- **Stock race condition**: `create_order`'s Python validation is the single source of truth; second request rejected cleanly
- **Slip verification failures**: blurry image, wrong amount, duplicate slip → all route to `manual_review`
- **Unregistered staff**: claiming to be staff without the role is always treated as customer — no privilege escalation via conversation alone
- **Store Resolver miss**: unknown `channel_id` → reject with 200 OK (LINE expects 200), log and alert
- **Cross-store tool call**: `store_id` is injected by context, never by LLM — model cannot query another store's data even if it tries

---

## 12. Testing plan

- Seed test store's `products`/`orders`, exercise full เซลส์ flow (search → order → QR → slip → paid) via LINE against `gate_roles: creator`
- Exercise เลขา flow with test account tagged `employee` — confirm tool access boundary
- Verify row-level isolation: tool calls for store A cannot return store B data even with identical SKUs
- Register two test stores in `tawan_ai.stores`, verify Store Resolver routes each `channel_id` to the correct `store_id`
- Verify `reply_user` + `update_memory` execute in parallel (check `agent_call_log.tool_calls_detail`)

---

## 13. Forward-compat (Phases 2–4)

- **Phase 2 (escalation)**: `interact_log.meta` tags unanswered turns `{"escalation": true}`. Phase 2 builds queue + owner notification via `reach.alert`
- **Phase 3 (learning pipeline)**: reads Phase 2 resolved escalations → consolidates into `knowledge_entries`. Same nightly shape as `memory.dream`
- **Phase 4 (cross-store analytics)**: `store_id` on all commerce tables enables per-store and aggregate analytics without schema changes

---

## 14. Open items

1. Encryption scheme for `channel_secret_enc` / `channel_token_enc` in `tawan_ai.stores` — Supabase Vault vs application-layer AES
2. Shopee webhook format + `channel_id` equivalent (LINE has `destination`, Shopee TBD)
3. `reply_user` streaming behavior — not needed for LINE (complete message units), but noted for future web channel
4. Dashboard repo location (Astro new route vs separate repo)
5. PDPA processing inventory + Thai counsel review (Phase 1J, pre-pilot)
6. Commerce table detail columns (`products`, `orders`, `payment_slips`) — pending store owner design
