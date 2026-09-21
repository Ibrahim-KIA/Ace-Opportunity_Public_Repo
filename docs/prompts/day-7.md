# Day 7 — Polish + submission

## Context

You're building **NextStep**. This is the last build day. The product is functionally complete and hardened as of Day 6. Today is about making sure it presents well, the repo matches the live deployment exactly, and the submission actually gets in — no new features.

## Assumed starting state

Days 1–6 done and deployed: full flow (upload → profile → matches with explanations → per-match checklist) works reliably on the live site, tested against multiple real CVs.

## Your tasks

### 1. Final deploy verification

- Redeploy both the Render backend and the Vercel frontend from the current `main` branch tip, so there's no drift between what's committed and what's live.
- Walk the entire flow on the live URLs one more time, start to finish: upload → matches → checklist. Confirm nothing regressed.
- Confirm the deployed frontend URL and backend URL are both reachable **without login** (this matters — judges need to open it directly).

### 2. README finalization (`README.md`)

- Update the "Status" section — this is no longer pre-build; describe what the product actually does now, accurately.
- Add real screenshots or a short GIF of the actual live product (upload screen, results screen with a real match, the checklist expanded). Save images under `docs/images/` and embed with `![description](docs/images/filename.png)`.
- Add a "Live demo" section with the actual deployed frontend URL.
- Add a "Running locally" section with real, tested setup steps (clone, install backend deps, install frontend deps, required env vars referencing `.env.example` files, how to run both, how to run the seed script from Day 3).
- List the real tech stack used (don't just copy the "planned" stack from the original README if anything changed during the week).

### 3. Env examples check

- Confirm `backend/.env.example` and `frontend/.env.example` list every environment variable the app actually needs now (should include anything added since Day 1 — double check nothing new was introduced in Days 2–6 without updating these files).
- Confirm no real secrets exist anywhere in git history. If a `.env` was ever accidentally committed earlier in the week, remove it and rotate any exposed keys — don't just delete the file going forward.

### 4. Demo script

Write a short (60–90 second) spoken demo script into `docs/DEMO_SCRIPT.md`:
- One sentence on the problem (generic resume/job matching is keyword-based and shallow).
- One sentence on the approach (embeddings-based semantic matching + LLM-grounded explanations, not keyword search).
- A beat-by-beat of what to click/show during a live demo, timed roughly to fit the window.
- One specific technical detail worth calling out if asked (e.g. "matches are ranked by cosine similarity over sentence embeddings, and each explanation is generated fresh from the actual profile fields, not templated").

### 5. Submit

- Complete the Build Submission Form with the repo URL and live deployed URL once everything above is verified.
- Double check the repo is public and requires no login to view.

## Acceptance criteria

- [ ] Live site and repo are both publicly accessible with no login.
- [ ] README accurately describes the finished product, includes real screenshots, and its "running locally" steps actually work if followed from a clean clone.
- [ ] No secrets present anywhere in the repo or its history.
- [ ] Demo script exists and fits the actual allotted demo time.
- [ ] Submission form completed.

## Commit

```
Finalize README with screenshots and live demo link, add demo script, submission polish
```
Push to `main`.
