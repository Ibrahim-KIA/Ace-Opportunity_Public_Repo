# Day 4 — Matching engine

## Context

You're building **NextStep**, an AI copilot that matches a person to real opportunities based on their actual CV. So far: Day 1 shipped deploy pipeline, Day 2 shipped CV upload → structured profile (saved to Mongo `profiles`), Day 3 shipped a real, embedded opportunity dataset (saved to Mongo `opportunities`, each with a 384-dim `embedding`). Today: connect the two — given a profile, return ranked, explained matches. This is the core value of the product; take the time to make the explanations genuinely grounded in the person's actual background, not generic filler.

## Fixed tech stack

- Backend: Python, FastAPI, deployed on Render. `core/embeddings.py` (`embed_text`) and `core/llm.py` (Anthropic client + `extract_profile`) already exist.
- Database: MongoDB Atlas via `motor`, collections `profiles` and `opportunities` (with embeddings) already populated.

## Assumed starting state

Days 1–3 done and deployed: CV upload produces a saved profile; the opportunity dataset (20+ real entries) is seeded in production with embeddings.

## Your tasks

### 1. Similarity utility (`backend/app/core/matching.py`)

- `cosine_similarity(a: list[float], b: list[float]) -> float` — standard cosine similarity, no need for a heavy vector DB at this dataset size (a few dozen to a few hundred opportunities fits fine in memory).
- `rank_opportunities(profile_embedding: list[float], opportunities: list[dict], top_n: int = 5) -> list[dict]` — computes similarity against every opportunity's `embedding`, sorts descending, returns the top N with a `score` field attached (0–1, rounded to 2 decimals).

### 2. LLM "why you fit" generation (`backend/app/core/llm.py`)

Add a function `explain_fit(profile: dict, opportunity: dict) -> str`: prompts Claude with the specific overlapping details — pass the profile's skills/experience/education and the opportunity's title/description/eligibility — and ask for a 2–3 sentence explanation of why this specific person is a good fit for this specific opportunity, referencing concrete details from the profile (not "this role aligns with your background" boilerplate). Instruct the model explicitly to name at least one specific skill or experience from the profile in its answer.

### 3. Match endpoint (`backend/app/routes/match.py`)

- `GET /api/match/{profile_id}`:
  1. Load the profile from Mongo by `profile_id` (404 if not found).
  2. Build the same style of text blob used for opportunities in Day 3 (skills + experience + education + interests, joined) and embed it via `embed_text`.
  3. Load all opportunities from Mongo (including embeddings this time — this is a backend-internal query, not the public listing endpoint).
  4. Call `rank_opportunities` to get the top 5.
  5. For each of the top 5, call `explain_fit` to get the personalized explanation.
  6. Return a list of `{opportunity: {...without embedding...}, score, why_you_fit}`.
- Register this router in `main.py`.
- This endpoint chains multiple LLM calls (one per match) — it will take several seconds. That's expected; the frontend should show a clear loading state (see below), not try to make this instant.

### 4. Frontend: connect upload → match (`frontend/src/`)

- After a successful CV upload (Day 2's flow), automatically call `GET /api/match/{profile_id}` using the `profile_id` returned from the upload, and transition the UI into a "finding your matches..." loading state, then show results once they arrive.
- Results view: for each match, show title, organization, type, score (e.g. as a percentage or a simple bar), the why-you-fit text, deadline, and a link to the opportunity. (A more polished layout is Day 5's job — today just get real data rendering correctly.)

## Acceptance criteria

- [ ] Uploading a real CV end-to-end on the live site produces 5 ranked matches.
- [ ] The why-you-fit text for each match actually references something true and specific from that CV — spot check at least 2 matches manually.
- [ ] Matches are sorted by score descending, and scores are sane (semantically closer opportunities score higher — verify with a CV that's clearly aimed at one field, e.g. software engineering, and confirm software-related opportunities rank above unrelated ones like a literature scholarship, if your dataset contains a mix).
- [ ] The full chain works on the live Render/Vercel deployment.

## Commit

```
Add embedding-based matching engine with LLM-generated fit explanations
```
Push to `main`.
