# NextStep

An AI copilot that matches you to real opportunities — internships, scholarships, and grants — based on your actual CV, not keyword guessing.

## What it does

1. **Upload your CV** — an LLM extracts a structured profile (skills, education, experience, interests).
2. **Match** — your profile is embedded and compared against a curated set of real opportunities using vector similarity, not simple keyword matching.
3. **Explain** — each match comes with a plain-language "why you fit" rationale generated from your actual background.
4. **Act** — a tailored checklist of what to prepare for your top matches (documents, deadlines, next steps).

## Status

🚧 Pre-build. This repo currently holds project structure and planning only — active development starts with StacStart Build Week (Sept 22–28, 2026). See [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) for the day-by-day plan.

## Stack (planned)

- **Backend:** FastAPI (Python)
- **Frontend:** React
- **Database:** MongoDB
- **Vector search:** embeddings-based similarity for CV-to-opportunity matching
- **Deploy:** frontend on Vercel, backend on Render

## Repo layout

```
backend/   API, CV parsing, matching engine
frontend/  Web UI
docs/      Planning and design notes
```

## Team

- Ibrahim (Ibrahim-KIA)

## License

MIT — see [LICENSE](LICENSE).
