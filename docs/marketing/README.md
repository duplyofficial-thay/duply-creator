# marketing/

Reference playbook + output folder for the Thay + Duply "AI marketing team." `team/` and `brand/` hold plain markdown playbooks — **not** live-wired Claude agents or skills. This environment's `Agent`/`Skill` tools only recognize a fixed built-in set and don't auto-discover project-level `.claude/agents/*.md` or `.claude/skills/*/SKILL.md` files (confirmed via a fresh-session test, 2026-08-04 — both `marketing-lead` and `copywriter` came back "Agent type not found"). If you're using local Claude Code CLI elsewhere, these files are **not** drop-ins for `.claude/agents/`/`.claude/skills/` as-is — agents require YAML frontmatter (`name`/`description`) that none of these files have, and skills require a `<name>/SKILL.md` directory layout rather than a flat file. Both would need that structure added first before porting.

## How to use

Ask a Claude Code session in this repo for marketing help — e.g. "act as the marketing lead in `marketing/team/marketing-lead.md` and draft a launch post for Thay's new earnings calendar feature." The session `Read`s that file and follows it: for a single small request it does the work directly in the same conversation; for a multi-specialist request it dispatches `general-purpose` subagents, pasting the relevant `team/<specialist>.md` file's content as each one's instructions. See `team/marketing-lead.md` for the exact decision process.

You can also point directly at one specialist playbook if you only want one piece (e.g. "follow `marketing/team/copywriter.md` and write...").

## Folders

- `team/` — the 5 role playbooks: `marketing-lead.md` (orchestrator), `content-strategist.md`, `copywriter.md`, `social-media-manager.md`, `growth-marketer.md`
- `brand/` — `thay-brand-brief.md`, `duply-platform-brief.md` — read before writing anything for either product, referenced by every playbook
- `briefs/` — content-strategist's strategy briefs (angle, audience, pillars)
- `copy/` — copywriter's drafts (LINE broadcasts, ads, landing/app copy, email)
- `social/` — social-media-manager's platform-specific post ideas
- `growth/` — growth-marketer's acquisition/funnel/experiment ideas
- `campaigns/` — marketing-lead's assembled final packages — start here to see what a request produced end-to-end

## Everything here is a draft

Nothing in this folder has been posted, sent, or published. Review before publishing anything.
