# Build Prompts

One file per build day (`day-1.md` … `day-7.md`). Each file is self-contained — it repeats the project context, the tech stack decisions, and what's assumed done already — so it works even if it's the only thing handed to an AI coding session, with no other memory of this repo.

## How to use

1. Open a coding session (Claude Code, Cursor, or any agentic coding AI) with this repo (`NextStep/`) as the working directory.
2. Paste the entire contents of that day's file as your first message.
3. Let it build, review the diff, run it locally if possible, then push.
4. Only start day N+1 after day N is committed and (for days with a deploy step) actually deployed — each prompt assumes the previous day's work is live on `main`.

## Fixed technical decisions (same across all days)

Repeating these in every file is intentional — don't let an agent improvise a different stack mid-week.

- **Backend:** Python, FastAPI, deployed on Render as a web service.
- **Database:** MongoDB (Atlas free tier), accessed via `motor` (async driver).
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`), run locally in the backend — no external embeddings API, no extra API key.
- **Text generation** (CV → structured profile, "why you fit" explanations, checklists): Anthropic Claude API (`anthropic` Python SDK), model `claude-sonnet-5` (or whatever the latest small/fast Sonnet model is at build time — check `plugin:claude-api` docs if unsure).
- **Frontend:** React + Vite, deployed on Vercel as a static SPA that calls the backend over REST.
- **File parsing:** `pdfplumber` for PDF, `python-docx` for DOCX.
- **Repo layout:** `backend/app/...`, `frontend/src/...`, `docs/...` — see root `README.md`.

## Secrets (never commit these)

- `MONGODB_URI` — Atlas connection string
- `ANTHROPIC_API_KEY` — Claude API key

Set both in Render's environment variable settings for the backend service. The frontend only needs `VITE_API_URL` pointing at the deployed backend URL, set in Vercel's environment variable settings.

## Working rules for every day

- Commit at meaningful checkpoints during the day, not one dump at the end — the point is that the history reflects real incremental work.
- Keep `main` deployable at the end of each day.
- Use real data and real API calls in the demo path — no mocked/fake responses standing in for the actual AI calls.
- Write a commit message that says what changed, in the imperative mood (e.g. "Add CV upload endpoint with LLM profile extraction").
