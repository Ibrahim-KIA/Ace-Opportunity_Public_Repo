# Day 2 — CV ingestion + profile extraction

## Context

You're building **NextStep**, an AI copilot that matches a person to real opportunities (internships, scholarships, grants) based on their actual CV. Full flow: upload CV → LLM extracts a structured profile → profile is embedded and matched against a curated opportunity dataset via vector similarity → each match gets an LLM-generated "why you fit" explanation → user gets a tailored prep checklist.

Today: the first real feature. A user uploads a CV file and gets back a structured profile, extracted by an LLM and saved to the database.

## Fixed tech stack

- Backend: Python, FastAPI, deployed on Render. Repo root `backend/app/` with `main.py`, `core/config.py`, `core/db.py` already in place.
- Database: MongoDB Atlas via `motor`, database name `nextstep`.
- LLM: Anthropic Claude API (`anthropic` Python SDK), key in `ANTHROPIC_API_KEY` env var, already configured on Render.
- File parsing: `pdfplumber` for PDF, `python-docx` for DOCX.
- Frontend: React + Vite, deployed on Vercel, calling the backend via `VITE_API_URL`.

## Assumed starting state

Day 1 is done and deployed: health-check round trip works live between Vercel and Render, Mongo connection is wired (not yet used), CORS is locked to the real frontend origin.

## Your tasks

### 1. Profile schema (`backend/app/models/profile.py`)

Define a pydantic model `Profile` with fields:
```
name: str | None
email: str | None
skills: list[str]
education: list[dict]   # each: {institution, degree, field, year}
experience: list[dict]  # each: {organization, role, description, duration}
interests: list[str]
raw_text: str            # the original extracted CV text, kept for later embedding use
```

### 2. LLM extraction (`backend/app/core/llm.py`)

- Initialize an `anthropic.Anthropic` client using `settings.ANTHROPIC_API_KEY`.
- Function `extract_profile(cv_text: str) -> dict`: sends `cv_text` to Claude with a prompt instructing it to return **only** a JSON object matching the `Profile` schema above (no markdown fences, no commentary). Parse the response as JSON; if parsing fails, strip common wrapping (```json fences) and retry once before raising a clear error.
- Keep the prompt explicit about the exact field names and types so the output is parseable every time.

### 3. File text extraction (`backend/app/core/parsing.py`)

- `extract_text(filename: str, file_bytes: bytes) -> str`: dispatch on file extension — `.pdf` via `pdfplumber`, `.docx` via `python-docx`. Raise a clear `ValueError` for unsupported extensions.
- If a PDF yields little or no extractable text (e.g. it's a scanned image), raise a clear error rather than silently proceeding — this case gets surfaced to the user, not swallowed.

### 4. Upload endpoint (`backend/app/routes/cv.py`)

- `POST /api/cv/upload`, accepts `multipart/form-data` with a `file` field.
- Flow: extract text → call `extract_profile` → build a `Profile` → insert into Mongo collection `profiles` (via `get_database()`) → return `{"profile_id": str(inserted_id), "profile": {...}}`.
- Handle and return clear 4xx errors for: unsupported file type, empty/unparseable file, LLM extraction failure. Don't let any of these come back as a raw 500 with a stack trace.
- Register this router in `main.py`.

### 5. Dependencies

Add to `backend/requirements.txt`: `anthropic`, `pdfplumber`, `python-docx`, `python-multipart` (needed for FastAPI file uploads).

### 6. Frontend upload flow (`frontend/src/`)

- Replace the Day 1 "check backend" button with a real upload page: file input (accept `.pdf,.docx`), an "Upload" button, a loading state while the request is in flight (this call can take several seconds — say so in the UI, e.g. "Reading your CV...").
- On success, render the returned profile: name, skills as tags/chips, education list, experience list, interests.
- On error, show the backend's error message plainly (not a generic "something went wrong").

## Acceptance criteria

- [ ] Uploading a real PDF or DOCX CV through the deployed frontend returns a structured profile that's actually accurate to that CV (spot-check name, at least a few real skills, at least one real education/experience entry).
- [ ] The profile document exists in the `profiles` collection in Atlas after upload (check via Atlas UI or a quick script).
- [ ] Uploading an unsupported file type (e.g. `.txt`) or a garbage file returns a clear error, not a crash.
- [ ] Both new endpoints and the frontend flow work against the live Render/Vercel deployment, not just localhost.

## Commit

```
Add CV upload endpoint with LLM-based profile extraction, persisted to MongoDB
```
Push to `main`.
