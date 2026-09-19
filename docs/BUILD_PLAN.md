# Build Plan — StacStart Build Week (Sept 22–28, 2026)

Scope is deliberately narrow: one clean flow (CV → structured profile → matched opportunities → why-you-fit → checklist), built and deployed for real, rather than a wide feature set half-working. Each day below is meant to end in a working, committed, deployed increment — not one commit dump at the end.

## Day 1 — Tue Sept 22: Skeleton + deploy pipeline
- FastAPI backend skeleton: health check route, CORS, project structure (`routes/`, `core/`, `models/`).
- React frontend skeleton: basic shell, upload page stub.
- Wire up deploys early: backend → Render, frontend → Vercel. Confirm the two talk to each other in prod before building features on top.
- Commit: scaffold + working "hello world" round trip frontend → backend → response.

## Day 2 — Wed Sept 23: CV ingestion + profile extraction
- CV upload endpoint (PDF/DOCX → text extraction).
- LLM prompt that turns raw CV text into a structured JSON profile (skills, education, experience, interests).
- Persist profile to MongoDB.
- Commit: upload → parsed profile visible in the UI.

## Day 3 — Thu Sept 24: Opportunity dataset
- Curate a real, focused dataset of opportunities (scholarships/internships/grants) — structured fields: title, org, eligibility, deadline, description, link.
- Store in MongoDB.
- Generate embeddings for each opportunity.
- Commit: seeded, embedded opportunity set + a basic listing endpoint.

## Day 4 — Fri Sept 25: Matching engine
- Embed the user's structured profile.
- Vector similarity search against opportunity embeddings, ranked.
- LLM call to generate a short "why you fit" explanation per top match, grounded in the actual profile fields (not generic text).
- Commit: end-to-end match results returned from the API.

## Day 5 — Sat Sept 26: Frontend UX pass
- Results page: match cards (title, org, fit score, why-you-fit, deadline, link).
- Loading/empty/error states for upload and matching.
- Basic responsive styling pass.
- Commit: usable, demoable UI for the full flow.

## Day 6 — Sun Sept 27: Stretch feature + hardening
- Pick one stretch based on remaining time: (a) per-match application checklist generator, or (b) simple chat box for "find me opportunities in X."
- Fix rough edges found while dogfooding the flow end-to-end.
- Commit: stretch feature + bugfixes.

## Day 7 — Mon Sept 28: Polish + submission
- Final bug pass, deployed URL matches repo state.
- README finalized with real screenshots/GIF and setup instructions.
- Record demo video/script.
- Submit via the Build Submission Form.

## Working rules
- Commit at each meaningful checkpoint, not once at the end — history should read as the build actually happening.
- Keep `main` deployable at the end of every day.
- Real dataset, real API calls — no mocked "fake AI" responses in the demo path.
