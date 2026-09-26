# Ace-Opportunity — Product & Engineering Roadmap

This document outlines the technical architecture, daily milestones, and implementation roadmap for **Ace-Opportunity**.

---

## Architecture Overview

Ace-Opportunity matches candidates to real scholarships, internships, and grants using semantic vector similarity and grounded AI explanations.

```
[ Candidate CV (PDF/DOCX) ]
           │
           ▼
[ Text Extraction (pypdf / python-docx) ]
           │
           ▼
[ AI Profile Extraction (Google Gemini / Claude) ]
           │
           ├───► Stored in MongoDB Atlas (`profiles` collection)
           │
           ▼
[ Vector Embedding (sentence-transformers / all-MiniLM-L6-v2) ]
           │
           ▼
[ Cosine Similarity Matching vs. Opportunities Dataset ]
           │
           ▼
[ Grounded "Why You Fit" AI Explanations & Prep Checklists ]
           │
           ▼
[ Interactive Results Interface (React + Vite) ]
```

---

## Daily Milestones

### Phase 1: Foundation & Deploy Pipeline (Day 1)
- [x] FastAPI backend setup with health check (`GET /api/health`), CORS middleware, and environment configuration.
- [x] React + Vite frontend skeleton with basic client routing.
- [x] Production deployment pipeline: Render (backend) and Vercel (frontend).

### Phase 2: CV Ingestion & AI Profile Extraction (Day 2)
- [x] Multi-format CV upload endpoint (`POST /api/cv/upload`, accepting `.pdf` and `.docx`).
- [x] Robust document parsing with 5 MB safety limit and empty/scanned file error handling.
- [x] AI extraction into structured `Profile` model (name, email, skills, education, experience, interests, summary, raw text).
- [x] Persistence to MongoDB Atlas `profiles` collection with unique ID generation.
- [x] Interactive upload UI with drag-and-drop, loading feedback, profile card, and error handling.
- [x] Comprehensive test suite covering parsers, models, and endpoints.

### Phase 3: Opportunity Dataset & Embeddings Pipeline (Day 3)
- [x] Curate structured dataset of 20+ verified opportunities (`backend/data/opportunities.json`) across internships, scholarships, and grants.
- [x] Implement local embeddings generator using `sentence-transformers` (`all-MiniLM-L6-v2` singleton).
- [x] Create idempotent database seed script (`backend/app/core/seed.py`) to populate the `opportunities` collection in Atlas.
- [x] Expose public opportunity listing endpoint (`GET /api/opportunities`, projecting out internal vector embeddings).

### Phase 4: Semantic Matching Engine & Fit Explanations (Day 4)
- [x] Cosine similarity utility and ranking algorithm (`backend/app/core/matching.py`).
- [x] Grounded AI rationale generator (`explain_fit`), citing concrete profile skills and experience rather than generic praise.
- [x] Match endpoint (`GET /api/match/{profile_id}`): loads candidate profile, computes embedding, ranks top 5 opportunities, and generates personalized explanations.
- [x] Connect upload flow to automated match querying in frontend.

### Phase 5: Results Interface, Component Refactoring & UX (Day 5)
- [x] Refactor frontend into modular components: `UploadForm`, `LoadingState`, `MatchCard`, `MatchResults`, `ErrorMessage`.
- [x] Design visual fit score badges, type indicators, deadlines, and direct application links.
- [x] Staged progress messages during AI analysis and matching.
- [x] Responsive design verification for both desktop and mobile viewports.

### Phase 6: Actionable Prep Checklists & Hardening (Day 6)
- [ ] Tailored checklist generator (`POST /api/checklist`) detailing required documents, deadlines, and concrete prep steps per match.
- [ ] Expandable on-demand checklist drawer on match cards.
- [ ] Hardening across diverse CV formats, edge cases, and missing profile sections.

### Phase 7: Final Verification & Demo Polish (Day 7)
- [ ] End-to-end verification of production Render and Vercel deployments.
- [ ] Finalize README with UI walkthrough, architecture diagrams, and setup instructions.
- [ ] Prepare live demo script.

---

## Data Models & Collections

### 1. `profiles` Collection
```json
{
  "_id": "ObjectId(...)",
  "name": "Alex Smith",
  "email": "alex@example.com",
  "skills": ["Python", "FastAPI", "React", "Machine Learning"],
  "education": [
    {
      "institution": "Stanford University",
      "degree": "BSc",
      "field": "Computer Science",
      "start_year": "2020",
      "end_year": "2024",
      "year": "2020–2024"
    }
  ],
  "experience": [
    {
      "organisation": "Tech Lab",
      "organization": "Tech Lab",
      "role": "Software Developer Intern",
      "start_date": "Jun 2023",
      "end_date": "Sep 2023",
      "duration": "Jun 2023 – Sep 2023",
      "description": "Contributed to internal API and pipeline development."
    }
  ],
  "interests": ["Artificial Intelligence", "Robotics"],
  "summary": "Passionate developer with hands-on experience in full-stack engineering.",
  "raw_text": "Full extracted plain text of CV..."
}
```

### 2. `opportunities` Collection
```json
{
  "_id": "ObjectId(...)",
  "title": "Google Summer of Code",
  "organization": "Google",
  "type": "internship",
  "eligibility": "Students and open-source beginners aged 18+",
  "description": "Global program focused on bringing new contributors into open source software development.",
  "deadline": "2026-04-08",
  "link": "https://summerofcode.withgoogle.com/",
  "tags": ["open source", "software engineering", "python", "mentorship"],
  "embedding": [0.012, -0.045, 0.089, "... (384 floats)"]
}
```

---

## API Specification

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Liveness check |
| `POST` | `/api/cv/upload` | Upload CV (`.pdf`/`.docx`), extract profile, save to MongoDB |
| `POST` | `/api/cv/parse` | Alias to upload endpoint |
| `GET` | `/api/opportunities` | List curated opportunities (embeddings excluded) |
| `GET` | `/api/match/{profile_id}` | Calculate top 5 ranked matches with tailored fit explanations |
| `POST` | `/api/checklist` | Generate tailored application checklist for a specific match |
