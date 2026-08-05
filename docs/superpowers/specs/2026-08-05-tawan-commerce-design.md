# Tawan (ตะวัน) — Commerce Archetype, Phase 1 Design

**Status:** Draft — pending user review
**Owner:** arriyathanasak@gmail.com
**Scope:** Phase 1 of 4 (catalog + dual-role sales chat + checkout). Phases 2–4 (escalation loop, learning pipeline, cross-store dashboard) are separate future specs.

---

## 1. Background

Duply is a platform for building **Duples** — AI products with an isolated Postgres schema, a dedicated LINE OA, and a shared persona/behavior split (`public.duply_duples.persona` = character, `{schema}.agent_profiles.system_prompt` = per-agent operational behavior). Existing Duples: Thay and Khun (finance archetype), Dom (lifestyle archetype). `archetype: commerce` is already reserved in `register/_template.yaml` but nothing has been built for it — no commerce tool pack, no commerce schema tables. This spec is the reference implementation.

Tawan is both: (a) a working product for one store, and (b) the reference implementation other SMEs get provisioned from under the commerce archetype, the same way Thay is finance's reference.

**Core platform rule that applies throughout:** LLM proposes → Python decides → DB writes. The model never writes to Supabase directly; every mutation goes through a validated Python tool.

---

## 2. Product goal

Tawan is a single AI persona that plays two roles depending on who's messaging the store's LINE OA:

- **เซลส์ (salesperson)** — to customers: catalog Q&A, order intake, checkout, payment verification, 24/7
- **เลขา (secretary)** — to store staff: internal lookups (stock, sales figures), inventory/price mutation, payment slip review

One store = one Tawan instance = one Duple (own schema, own LINE OA), following the existing per-Duple isolation pattern exactly. Each new SME onboarding gets its own instance provisioned from this same archetype.

---

## 3. Persona

Shared character (`public.duply_duples.persona`), operational tone split per agent:

> **ตะวัน**: พลังงานแบบแดดเช้า — สดใส กระตือรือร้น แต่ไม่จ้าจนแสบตา เชื่อถือได้เหมือนพระอาทิตย์ขึ้นทุกวัน ไม่มีวันลา ไม่มีวันหยุด จำรายละเอียดร้านได้แม่น ไม่มโนไม่เดา — ถ้าไม่รู้ จะบอกตรงๆ แล้วไปหาคำตอบมาให้ ให้ความรู้สึกเหมือนมีคนที่แคร์ร้านนี้จริงๆ อยู่เคียงข้างตลอด 24 ชม.

- **`chat.reply` (เซลส์ mode, default)** — warm, consultative, patient. Understands the need before pitching, honest about stock/delivery, closes when the customer is ready, never pressures.
- **`chat.staff` (เลขา mode)** — efficient, proactive, data-forward. Surfaces what staff need before they ask ("สต็อกสีแดงเหลือ 3 ชิ้น", "เดือนนี้ตัวนี้ขายดีสุด").

"Never makes things up — says so and goes to find out" is a core character trait, not a bolted-on feature. It's the seam Phase 2's escalation loop plugs into.

---

## 4. Architecture decisions

Decided in brainstorming, with rationale:

| Decision | Choice | Why |
|---|---|---|
| Deployment model | One Duple per store, provisioned from a shared "commerce" archetype | Matches existing Thay/Khun/Dom isolation pattern exactly — no data leak risk between stores, no new infra class needed |
| Staff vs. customer on one LINE OA | Same OA; staff pre-registered by the owner, tagged via `user_profiles.roles` | Extends the platform's existing `roles`/`gate_roles` primitive directly — no second OA/webhook to maintain per store |
| Persona switching | **Two separate agent profiles** (`chat.reply` vs `chat.staff`), not one agent branching by role | Cleaner separation of tools and prompt; user's explicit choice over the lighter single-agent option. **Requires a platform-level change** — see §8 |
| Catalog data | SQL for hard facts (price/stock/SKU), RAG (`knowledge_entries`) for soft facts (policies, brand story, sales scripts) | Hard facts must never be hallucinated; soft facts benefit from flexible retrieval. Knowledge domain already exists — no new infra |
| Checkout | Full checkout + payment, not just order handoff to staff | User's explicit requirement |
| Payment mechanism | PromptPay QR generation + customer-submitted slip + AI (vision) verification, staff fallback for mismatches | Standard pattern for Thai SME LINE commerce. No payment gateway account, no KYC, no per-transaction fees — appropriate for SME scale and speed to launch |
| Cross-store identity | `duply_id` (already platform-issued via LIFF auth) is the top tier; each store's `duple_id` is the tenant tier; a (duply_id, duple_id) pair is a per-store customer relationship | No new identity system needed now. A shared analytics layer for cross-store insight (Phase 4) is a **deliberate, narrowly-scoped exception** to per-Duple schema isolation — analytics only, never operational data (catalog/orders stay isolated per store) |

---

## 5. Data model

New schema block in `{duple_id}_ai` (e.g. `tawan_ai`), following the existing `-- BEGIN FINANCE ... END FINANCE` convention:

```sql
-- BEGIN COMMERCE

CREATE TABLE __SCHEMA__.products (
    id                   UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    sku                  TEXT NOT NULL UNIQUE,
    name                 TEXT NOT NULL,
    description          TEXT,
    category             TEXT,
    price                NUMERIC NOT NULL,
    wholesale_price      NUMERIC,
    stock_qty            INTEGER NOT NULL DEFAULT 0,
    low_stock_threshold  INTEGER DEFAULT 5,
    variants             JSONB DEFAULT '[]',   -- [{name, sku_suffix, price_delta, stock_qty}]
    images               JSONB DEFAULT '[]',
    status               TEXT NOT NULL DEFAULT 'active',  -- active | discontinued
    created_at           TIMESTAMPTZ DEFAULT now(),
    updated_at           TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE __SCHEMA__.orders (
    id                UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    duply_id          TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'pending',
        -- pending -> awaiting_payment -> paid -> fulfilled -> cancelled -> expired
    items             JSONB NOT NULL,   -- snapshot: [{product_id, sku, name, variant, qty, unit_price, line_total}]
    subtotal          NUMERIC NOT NULL,
    total             NUMERIC NOT NULL,
    shipping_address  JSONB,
    payment_status    TEXT NOT NULL DEFAULT 'unpaid',  -- unpaid | pending_verification | paid | failed
    created_by        TEXT NOT NULL,   -- 'chat.reply' | 'chat.staff' | staff duply_id
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_at        TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_orders_duply ON __SCHEMA__.orders (duply_id, status);

CREATE TABLE __SCHEMA__.payment_slips (
    id             UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    order_id       UUID NOT NULL REFERENCES __SCHEMA__.orders(id),
    image_url      TEXT NOT NULL,
    parsed_amount  NUMERIC,
    parsed_ref     TEXT,
    parsed_bank    TEXT,
    match_status   TEXT NOT NULL DEFAULT 'pending',  -- pending | matched | mismatch | manual_review
    verified_by    TEXT,   -- 'tawan_ai' | staff duply_id
    submitted_at   TIMESTAMPTZ DEFAULT now(),
    verified_at    TIMESTAMPTZ
);
CREATE INDEX idx_payment_slips_order ON __SCHEMA__.payment_slips (order_id);

-- END COMMERCE
```

Order `items` is a snapshot (not a live join to `products`) so historical orders remain accurate after price changes.

---

## 6. Tool packs (commerce archetype)

New entries in `data/tool_catalog.yaml`, following the existing pack convention:

**`commerce.generic` pack** (both agents):
| Tool | Purpose |
|---|---|
| `search_catalog(query, category?)` | Keyword/category product search |
| `get_product(sku_or_name)` | Full product detail: price, stock, variants, images |
| `check_stock(sku_or_name, variant?)` | Quick stock check |
| `create_order(items, customer_info)` | Action tool — Python validates stock at write time, then writes `orders` row |
| `get_order_status(order_id)` | Look up an existing order |

**`commerce.staff` pack** (`chat.staff` only, gated by `employee` role):
| Tool | Purpose |
|---|---|
| `get_low_stock()` | Products below `low_stock_threshold` |
| `get_sales_summary(period)` | Sales figures for day/week/month |
| `update_stock(sku, delta_or_new_qty)` | Action tool — inventory adjustment |
| `update_price(sku, new_price)` | Action tool — price change |
| `verify_payment_slip(slip_id, decision)` | Manual confirm/reject for `manual_review` slips |

---

## 7. Agent architecture

| | `chat.reply` (default) | `chat.staff` (new) |
|---|---|---|
| Persona mode | เซลส์ | เลขา |
| Reached by | anyone without `employee` in `roles` | anyone with `employee` in `roles` |
| Tool packs | `generic` + `commerce.generic` | `generic` + `commerce.generic` + `commerce.staff` |
| Context builder | `duples/tawan/chat/reply/context_builder.py` — customer profile, order history | `duples/tawan/chat/staff/context_builder.py` — today's low-stock, pending manual-review slips |

**Staff onboarding (self-serve, two-step):** an owner realistically doesn't know a staff member's raw LINE user ID, so onboarding can't be a one-shot `STAFF ADD <line_id>` command. Instead:
1. Staff member sends a fixed phrase (e.g. `สมัครพนักงาน`) to the store's LINE OA → Tawan sets their `roles` to `pending_staff` and sends the owner a direct push naming them (LINE display name)
2. Owner replies `STAFF APPROVE <name>` (new `router_config.yaml` service route, owner-only via `roles` containing `owner`) → `pending_staff` swapped to `employee`

No new table needed — both states live in the existing `user_profiles.roles`.

---

## 8. Platform dependency (blocking — needs Duply team)

Today, a Duple's LINE webhook always resolves to one fixed `agent_id`. Running two full agent profiles (`chat.reply` vs `chat.staff`) selected by the sender's `roles` requires a role-check-then-dispatch step added to the platform's shared reply flow, before context is built. This is not achievable purely within `duples/tawan/` — it needs to be scoped and built by the Duply team, same category as any other platform-tier change described in `guide/05-extending.md`.

---

## 9. Sales conversation flow

**เซลส์ mode:**
1. Customer asks about a product → `search_catalog`/`get_product` → real price/stock, never a guess
2. Follow-ups (material, fit, delivery) → soft facts from `knowledge_entries` if ingested, otherwise natural conversation within persona
3. Customer commits → Tawan collects item(s)/qty/variant/address → `create_order`. Python re-checks `stock_qty` at write time (not the number quoted earlier — stock can move between quote and commit)
4. Tawan replies with order summary + total + generated PromptPay QR
5. Customer sends a payment slip photo → vision reads amount/ref/bank → matched against the pending order by amount + time window
6. Clean match → `orders.status = paid`, customer confirmed, staff notified for fulfillment. No match → `payment_slips.match_status = manual_review`, customer told to wait, staff picks it up via `chat.staff`

**เลขา mode:**
- "วันนี้ขายไปเท่าไหร่" → `get_sales_summary`; "อะไรใกล้หมด" → `get_low_stock`
- Direct conversational mutation ("เพิ่มสต็อกเสื้อแดง 20 ตัว") → `update_stock`
- "มีสลิปที่ต้องเช็คไหม" → lists `manual_review` rows → `verify_payment_slip`

**Order expiry:** orders left `awaiting_payment` past 24h auto-expire and release held stock — a lightweight cron addition, reusing the platform's existing cron infrastructure pattern (same shape as `reach_cron`).

---

## 10. Error handling & edge cases

- **Stock race condition**: two customers order the last unit near-simultaneously — `create_order`'s Python validation is the single source of truth; the second request is rejected with a clear "just sold out" message, not a silent overcommit.
- **Slip verification failure modes**: blurry image, wrong amount, no matching pending order, duplicate slip reuse — all route to `manual_review`, never auto-reject or auto-confirm on uncertain input.
- **Tool/DB failures**: every tool follows the existing platform contract — never raises, returns `"[ERROR] ..."` string, model relays a graceful message rather than failing silently.
- **Unregistered "staff"**: someone claiming to be staff without the `employee` role is always treated as a customer — no privilege escalation via conversation alone, only via the `STAFF ADD` owner-gated route.

---

## 11. Testing plan

- Seed a test store's `products`/`orders` tables, exercise the full เซลส์ flow (search → order → QR → slip → paid) via LINE against `gate_roles: creator`
- Exercise เลขา flow with a test account tagged `employee` — confirm tool access boundary (customer account must never reach `commerce.staff` tools even if it guesses the tool name)
- Verify schema isolation: confirm `tawan_role` cannot read any other Duple's schema (same check `provision_duple.py` already runs for every new Duple)
- Check `agent_call_log` and `interact_log` are written correctly per turn, consistent with existing Duples

---

## 12. Forward-compat notes for Phases 2–4 (not built now)

- **Phase 2 (escalation loop)**: `interact_log.meta` (JSONB) tags unanswered turns `{"escalation": true, "category": "product"|"store"}`. Phase 2 builds the queue + owner notification on top, reusing `reach.alert`'s existing trigger mechanism.
- **Phase 3 (learning pipeline)**: reads Phase 2's resolved escalations, consolidates into `knowledge_entries`. Same nightly shape as `memory.dream`; could mirror its `dream_log`/`dream_observations` audit pattern.
- **Phase 4 (dashboard + cross-store insight)**: `orders`/`products` already carry `duply_id` consistently, so an ETL into a shared analytics schema later (tagged by each store's `duple_id`) doesn't require touching Phase 1 tables.

---

## 13. Open items for the Duply team (not the user)

1. Scope and build role-based agent dispatch in the shared chat reply flow (§8)
2. Confirm port/webhook/Cloudflare provisioning steps are unchanged for the commerce archetype (per `guide/03-domains.md` team post-provisioning checklist)
3. Register `commerce.generic` and `commerce.staff` packs in `platform/tools/registry.py` + `data/tool_catalog.yaml`, run `scripts/gen_tool_catalog.py`
