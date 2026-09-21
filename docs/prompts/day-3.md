# Day 3 — Opportunity dataset + embeddings

## Context

You're building **NextStep**, an AI copilot that matches a person to real opportunities (internships, scholarships, grants) based on their actual CV. Day 1 shipped the deploy pipeline; Day 2 shipped CV upload → structured profile, persisted to MongoDB. Today you build the other half of what gets matched against: a real dataset of opportunities, each with a vector embedding, so tomorrow's matching engine has something real to compare a profile against.

## Fixed tech stack

- Backend: Python, FastAPI, deployed on Render. `backend/app/` has `main.py`, `core/config.py`, `core/db.py`, `core/llm.py`, `core/parsing.py`, `models/profile.py`, `routes/cv.py` already in place.
- Database: MongoDB Atlas via `motor`, database `nextstep`, collection `profiles` already in use.
- Embeddings: `sentence-transformers`, model `all-MiniLM-L6-v2`, run locally in the backend process — no external embeddings API or extra API key needed.

## Assumed starting state

Day 2 is done and deployed: uploading a CV returns a structured, LLM-extracted profile and saves it to Mongo.

## Your tasks

### 1. Curate a real opportunity dataset (`backend/data/opportunities.json`)

Compile **at least 20 real, currently-relevant opportunities** — a mix of internships, scholarships, and grants relevant to students/early-career people (skew toward tech/STEM/general professional development, or narrow further if you want a sharper niche). Use real organizations and real (or realistically-typical) eligibility/deadline info — don't invent fictional programs; this dataset is part of what makes the demo credible.

Each entry:
```json
{
  "title": "string",
  "organization": "string",
  "type": "internship | scholarship | grant",
  "eligibility": "string — who can apply",
  "description": "string — 2-4 sentences",
  "deadline": "YYYY-MM-DD or 'rolling'",
  "link": "string — real URL",
  "tags": ["string", "..."]
}
```

### 2. Embeddings module (`backend/app/core/embeddings.py`)

- Load `sentence-transformers` model `all-MiniLM-L6-v2` once as a module-level singleton (loading it per-request is too slow).
- `embed_text(text: str) -> list[float]`: returns the embedding as a plain Python list (so it's JSON/Mongo-serializable).
- Add `sentence-transformers` to `backend/requirements.txt`. Note: this pulls in `torch`; if the Render build is slow or hits memory limits on the free/starter plan, that's expected — let it run, it's a one-time model download cached in the build.

### 3. Seed script (`backend/app/core/seed.py`)

- A standalone async function (and a `if __name__ == "__main__":` entrypoint so it's runnable directly) that: reads `data/opportunities.json`, for each entry builds a single text blob from `title + organization + description + eligibility + " ".join(tags)`, embeds it via `embed_text`, and upserts the full document (original fields + `embedding: list[float]`) into the Mongo `opportunities` collection, keyed by `title` (so re-running the seed is safe and just updates existing entries rather than duplicating).
- Run this once against the **production** Atlas database (point your local `.env` at the same `MONGODB_URI` Render uses, then run `python -m app.core.seed` from `backend/`) so the live deployment has real seeded data, not just your local dev database.

### 4. Listing endpoint (`backend/app/routes/opportunities.py`)

- `GET /api/opportunities`: returns all opportunities from Mongo **excluding the `embedding` field** (it's large and not needed by the frontend) — project it out in the Mongo query.
- Register this router in `main.py`.

### 5. Frontend (optional but recommended today)

- Add a simple "Browse opportunities" view that calls `GET /api/opportunities` and lists them (title, org, type, deadline) — mainly so you have a quick visual way to confirm the dataset seeded correctly on the live site. This can be replaced or removed once Day 4's match results page exists.

## Acceptance criteria

- [ ] `data/opportunities.json` has at least 20 real entries with all required fields filled in accurately.
- [ ] Running the seed script against production populates the `opportunities` collection in Atlas, each document including a non-empty `embedding` array (384 floats, since `all-MiniLM-L6-v2` has 384 dimensions).
- [ ] `GET /api/opportunities` on the live Render backend returns the seeded list, with no `embedding` field in the response payload.
- [ ] Re-running the seed script doesn't create duplicates (same 20+ documents before and after a second run).

## Commit

```
Add curated opportunity dataset, embeddings pipeline, and listing endpoint
```
Push to `main`. (The dataset JSON and the seed script are committed; the *result* of running the seed script — the Mongo documents — lives in Atlas, not in git.)
