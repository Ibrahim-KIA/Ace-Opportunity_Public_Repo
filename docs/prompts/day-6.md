# Day 6 — Stretch feature + hardening

## Context

You're building **NextStep**. The core flow (upload → structured profile → ranked, explained matches) is fully built and polished as of Day 5. Today: add one meaningful stretch feature, then spend real time finding and fixing edge cases by actually using the product with different inputs — not just building forward.

## Fixed tech stack

Same as prior days: FastAPI backend on Render, MongoDB Atlas, Anthropic Claude API for generation, React/Vite frontend on Vercel.

## Assumed starting state

Days 1–5 done and deployed: full polished flow works end-to-end on the live site.

## Your tasks

### 1. Stretch feature: application checklist generator

Build this one (recommended over a chat feature — it's a more natural extension of the existing product and lower-risk to get right in one day):

- `backend/app/core/llm.py`: add `generate_checklist(profile: dict, opportunity: dict) -> dict` — prompts Claude to produce, specific to this profile + opportunity pairing: a short list of documents/materials typically needed (e.g. transcript, recommendation letter, personal statement — inferred from the opportunity's type and description), the deadline restated clearly, and 2–3 concrete prep tips tailored to gaps or strengths visible in the profile relative to this opportunity. Ask for structured JSON output: `{"documents": [...], "deadline_note": "...", "tips": [...]}`.
- `backend/app/routes/checklist.py`: `POST /api/checklist` accepting `{profile_id, opportunity_id}` (or embed opportunity data directly if that's simpler given how `match.py` already has both in hand) → loads both from Mongo → calls `generate_checklist` → returns the result. Register the router.
- Frontend: add a "Get ready for this" expandable/button on each `MatchCard` that calls this endpoint on demand (not eagerly for all 5 matches on page load, to avoid unnecessary LLM calls) and renders the checklist inline when expanded.

If there's clearly time left after this is solid, a second stretch option is a simple chat box (`POST /api/chat` with `{profile_id, message}`, using the existing profile + opportunity set to answer natural-language questions like "find me opportunities in renewable energy" by re-filtering/re-ranking and responding conversationally) — but only attempt this after the checklist feature is fully working and tested, since a half-built second feature is worse than one solid one.

### 2. Hardening pass

Actually use the deployed product with **at least 3 different real CVs** (varied fields/experience levels — e.g. a CS student, a business/humanities student, someone with little formal experience) and fix whatever breaks or looks wrong, such as:
- CVs with sparse or missing sections (no listed experience, no education section) — the profile extraction and matching should degrade gracefully, not error out.
- Unusual PDF formatting (multi-column layouts, tables) that garbles extracted text — at minimum, don't crash; ideally still produce a usable profile.
- Non-English CVs, if relevant to your likely demo/judge audience — decide explicitly whether to support this or clearly reject non-English input with a helpful message, rather than silently producing garbage.
- Slow LLM responses or transient API errors — make sure the frontend shows a real error/retry state rather than hanging indefinitely.

## Acceptance criteria

- [ ] The checklist feature works end-to-end on the live site with real profile/opportunity data, and its content is genuinely specific to the pairing (not generic advice repeated across every match).
- [ ] At least 3 distinct real CVs have been run through the full live flow, with any bugs found along the way fixed and re-verified.
- [ ] No known crash paths remain for common bad inputs (empty file, wrong file type, CV with minimal content).

## Commit

Commit the checklist feature and the bugfixes as separate commits if they land at different points in the day (that's more honest to how the day actually went), e.g.:
```
Add application checklist generator for matched opportunities
Fix profile extraction for CVs with missing sections
```
Push to `main`.
