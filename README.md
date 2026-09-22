# NextStep

An AI copilot that matches you to real opportunities — internships, scholarships, and grants — based on your actual CV, not keyword guessing.

## What it does

1. **Upload your CV** — an LLM extracts a structured profile (skills, education, experience, interests).
2. **Match** — your profile is embedded and compared against a curated set of real opportunities using vector similarity, not keyword matching.
3. **Explain** — each match comes with a plain-language "why you fit" rationale grounded in your actual background.
4. **Act** — a tailored prep checklist for your top matches (documents, deadlines, next steps).

## Stack

- **Backend:** Python · FastAPI · deployed on Render
- **Frontend:** React · Vite · deployed on Vercel
- **Database:** MongoDB Atlas (via `motor` async driver)
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`) — runs locally in the backend, no external embeddings API
- **LLM:** Anthropic Claude API — profile extraction, fit explanations, checklists

## Repo layout

```
backend/   FastAPI app, CV parsing, matching engine
frontend/  React + Vite SPA
```

## Running locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in MONGODB_URI, ANTHROPIC_API_KEY, CORS_ORIGINS
uvicorn app.main:app --reload
# → http://localhost:8000/api/health
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env          # set VITE_API_URL=http://localhost:8000
npm run dev
# → http://localhost:5173
```

## Environment variables

| Variable | Where | Purpose |
|---|---|---|
| `MONGODB_URI` | backend `.env` / Render | MongoDB Atlas connection string |
| `ANTHROPIC_API_KEY` | backend `.env` / Render | Claude API key |
| `CORS_ORIGINS` | backend `.env` / Render | Comma-separated allowed origins (set to your Vercel URL in prod) |
| `VITE_API_URL` | frontend `.env` / Vercel | Backend URL (`http://localhost:8000` for local dev) |

## Team

- Ibrahim (Ibrahim-KIA)

## License

MIT — see [LICENSE](LICENSE).
