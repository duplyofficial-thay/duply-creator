---
name: duply-platform-brief
description: Brand brief for Duply (the platform itself) — positioning, audience, and honesty guardrails. Load before writing any Duply-platform-facing marketing content (as opposed to content for a specific Duple like Thay).
---

# Duply Platform Brand Brief

Source: `README.md`, `guide/01-concepts.md` (as of 2026-08-04).

## What Duply is

Duply is the platform layer — shared infrastructure (identity, auth, routing, memory engine, tool registry) that powers "Duples": individual AI products/chatbots built on top of it. Users talk to Duples via LINE. Each Duple has its own persona, tools, and memory, isolated from every other Duple at the database level.

Thay (US-stock finance companion) is the flagship example of a Duple built on Duply.

## Audience for Duply-platform marketing

**Potential Duple creators** — people who might want to build their own LINE-based AI product: developers, indie builders, small teams, or businesses with an idea for an AI chatbot product but who don't want to build chat infra, memory, auth, and tool-calling from scratch.

This is NOT end-users of Thay or any other Duple — those people only ever interact with the individual Duple (e.g. "Thay"), not with "Duply" as a brand. Don't write Duply-platform copy aimed at consumers; it's a builder/creator pitch.

## Positioning

- The pitch: register a Duple, get a provisioned schema + scaffold, build your persona and tools, ship on LINE — without building the platform underneath it yourself.
- Differentiator: schema isolation (your data is genuinely isolated per Duple), a real tool/card/routing framework already built, and prompts you can edit live in Supabase without redeploying.

## Honesty guardrail (hard rule, not a style preference)

Duply is genuinely early-stage — a small number of live Duples (Thay is the flagship; others are in earlier stages), not a mature multi-tenant platform with thousands of builders. Marketing copy must not:
- Imply a large existing creator community that doesn't exist yet
- Use "trusted by X creators" or similar social-proof framing that isn't true
- Overstate platform maturity, uptime guarantees, or feature completeness

Safe framing: honest early-stage/builder-focused language — "come build early," "shape what this becomes," concrete details about what's actually live (schema isolation, the tool/card framework, live-editable prompts) rather than vague scale claims.
