# Day 1 — Skeleton + deploy pipeline

## Context

You're building **NextStep**, an AI copilot that matches a person to real opportunities (internships, scholarships, grants) based on their actual CV. The full flow, built across a 7-day build week, is: upload CV → LLM extracts a structured profile → profile is embedded and matched against a curated opportunity dataset via vector similarity → each match gets an LLM-generated "why you fit" explanation → user gets a tailored prep checklist.

Today you're building **only** the skeleton and deploy pipeline — no CV logic yet. The goal of the day is to prove the whole chain (browser → Vercel frontend → Render backend → response) works in production before any real feature is built on top of it.

## Fixed tech stack

- Backend: Python, FastAPI, deployed on Render as a web service.
- Database: MongoDB Atlas (free tier) via `motor` — not needed yet today, but wire the connection so it's ready.
- Frontend: React + Vite, deployed on Vercel as a static SPA.
- Repo root already contains: `README.md`, `LICENSE`, `.gitignore`, `docs/BUILD_PLAN.md`, empty `backend/` and `frontend/` folders (currently holding placeholder `.gitkeep` files — delete those once real files land).

## Assumed starting state

Repo initialized, first commit is "Project setup: README, license, structure, build plan". Nothing else exists yet.

## Your tasks

### 1. Backend skeleton (`backend/`)

Create this structure:
```
backend/
  app/
    __init__.py
    main.py
    core/
      __init__.py
      config.py
      db.py
  requirements.txt
  .env.example
```

- `core/config.py`: a `Settings` class (pydantic `BaseSettings`) reading `MONGODB_URI`, `ANTHROPIC_API_KEY`, and `CORS_ORIGINS` (comma-separated string, default `"*"` for now) from environment variables. Expose a cached `get_settings()`.
- `core/db.py`: a `motor.motor_asyncio.AsyncIOMotorClient` initialized from `settings.MONGODB_URI`, with a `get_database()` helper returning the `nextstep` database. Don't fail hard at import time if `MONGODB_URI` is unset — this file just needs to exist and be importable today.
- `main.py`: FastAPI app, CORS middleware using `CORS_ORIGINS` from settings, and one route: `GET /api/health` returning `{"status": "ok"}`.
- `requirements.txt`: `fastapi`, `uvicorn[standard]`, `motor`, `pydantic-settings`, `python-dotenv`.
- `.env.example`: list `MONGODB_URI=` and `ANTHROPIC_API_KEY=` and `CORS_ORIGINS=` with no real values.

Run it locally to confirm: `uvicorn app.main:app --reload` from inside `backend/`, then `curl localhost:8000/api/health` returns `{"status":"ok"}`.

### 2. Frontend skeleton (`frontend/`)

Scaffold with Vite: `npm create vite@latest . -- --template react` inside `frontend/` (or `frontend-tmp` then move contents in if the CLI complains about a non-empty directory — either way, end state is a normal Vite React app rooted at `frontend/`).

Replace the default starter page with a minimal app that:
- Reads the backend URL from `import.meta.env.VITE_API_URL` (fall back to `http://localhost:8000` if unset, for local dev).
- Has a single button "Check backend connection" that calls `GET {API_URL}/api/health` and displays the raw JSON response (or an error message) on the page.

Add `.env.example` in `frontend/` with `VITE_API_URL=` and no real value. Add a local `.env` (gitignored — the root `.gitignore` already covers `.env*`) with `VITE_API_URL=http://localhost:8000` for your own local testing.

Run it locally: `npm install && npm run dev`, confirm clicking the button against the local backend (running from task 1) returns `{"status":"ok"}` on screen.

### 3. Deploy the backend to Render

- Create a new Render Web Service pointed at this GitHub repo, root directory `backend`.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Runtime: Python 3
- Set environment variables in the Render dashboard: `MONGODB_URI` (Atlas connection string — create a free M0 Atlas cluster if one doesn't exist yet for this project), `ANTHROPIC_API_KEY`, `CORS_ORIGINS` (set to the Vercel frontend URL once you have it from step 4 — `*` is fine as a placeholder until then).
- Confirm `https://<your-service>.onrender.com/api/health` returns `{"status":"ok"}` in a browser.

### 4. Deploy the frontend to Vercel

- Create a new Vercel project pointed at this repo, root directory `frontend`, framework preset Vite.
- Set environment variable `VITE_API_URL` to the Render backend URL from step 3.
- Deploy, then confirm the deployed Vercel URL loads and clicking "Check backend connection" returns `{"status":"ok"}` from the live Render backend (not localhost).
- Go back to Render and set `CORS_ORIGINS` to the real Vercel URL (not `*`) now that you have it, then redeploy the backend so CORS is properly locked down.

## Acceptance criteria

- [ ] Visiting the live Vercel URL and clicking the button shows `{"status":"ok"}` sourced from the live Render backend.
- [ ] `backend/` and `frontend/` both run locally without errors.
- [ ] No secrets committed anywhere (`.env` files are gitignored; only `.env.example` files with empty values are committed).
- [ ] Placeholder `.gitkeep` files in `backend/` and `frontend/` are removed now that real files exist there.

## Commit

Stage everything, commit with a message like:
```
Add backend/frontend skeleton with health check round trip; wire Render + Vercel deploys
```
Push to `main`.
