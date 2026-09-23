# Ace-Opportunity

An AI copilot that matches you to real opportunities — internships, scholarships, and grants — based on your actual CV, not keyword guessing.

## What it does

1. **Upload your CV** — an AI extracts a structured profile (skills, education, experience, interests) from your PDF or DOCX file.
2. **Match** — your profile is embedded and compared against a curated set of real opportunities using vector similarity, not keyword matching.
3. **Explain** — each match comes with a plain-language "why you fit" rationale grounded in your actual background.
4. **Act** — a tailored prep checklist for your top matches (documents, deadlines, next steps).

## Stack

- **Backend:** Python · FastAPI · deployed on Render
- **Frontend:** React · Vite · deployed on Vercel
- **Database:** MongoDB Atlas (via `motor` async driver)
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`) — runs locally in the backend, no external embeddings API
- **LLM:** Google Gemini API (`google-genai`) / Anthropic Claude API — profile extraction, fit explanations, checklists

## Repo layout

```
backend/   FastAPI app, CV parsing, profile extraction, matching engine
frontend/  React + Vite SPA
```

## Running locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in GOOGLE_API_KEY, MONGODB_URI, CORS_ORIGINS
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
| `GOOGLE_API_KEY` | backend `.env` / Render | Google Gemini API key |
| `MONGODB_URI` | backend `.env` / Render | MongoDB Atlas connection string |
| `CORS_ORIGINS` | backend `.env` / Render | Comma-separated allowed origins (set to your Vercel URL in prod) |
| `VITE_API_URL` | frontend `.env` / Vercel | Backend URL (`http://localhost:8000` for local dev) |
| `ANTHROPIC_API_KEY` | backend `.env` / Render | Optional fallback Claude API key |

## Team

- Ibrahim ([@Ibrahim-KIA](https://github.com/Ibrahim-KIA)) — Engineering & Technical Lead
- Ibukunoluwa Omidiji — Product, Strategy & Research

## License

MIT — see [LICENSE](LICENSE).
