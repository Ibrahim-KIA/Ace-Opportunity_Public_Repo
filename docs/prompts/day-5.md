# Day 5 — Frontend UX pass

## Context

You're building **NextStep**. By now the full functional chain works end-to-end: upload a CV → get ranked, explained opportunity matches, live on the deployed site. Today has no new backend features — the job is to make the existing flow feel like a real product instead of a working prototype, since this is what judges actually interact with.

## Fixed tech stack

- Frontend: React + Vite, deployed on Vercel. No new backend routes today — this is a frontend-only day, calling the existing `/api/cv/upload` and `/api/match/{profile_id}` endpoints.

## Assumed starting state

Days 1–4 done and deployed: the full upload → structured profile → ranked, explained matches flow works, but the UI is functional/rough (built for correctness, not polish).

## Your tasks

### 1. Component structure

Break the current monolithic page (if it is one) into components, e.g.:
```
frontend/src/
  components/
    UploadForm.jsx
    LoadingState.jsx
    MatchCard.jsx
    MatchResults.jsx
    ErrorMessage.jsx
  App.jsx
```

### 2. `MatchCard`

For each match, display clearly: opportunity title, organization, type (as a small badge/tag — internship vs. scholarship vs. grant), a visual fit-score indicator (e.g. a percentage plus a small bar or ring, not just a bare number), the why-you-fit explanation, the deadline, and a link to the opportunity (opens in a new tab).

### 3. Loading state

The upload → match chain takes several seconds (LLM calls + embedding). Replace any bare spinner with staged messaging that reflects what's actually happening, e.g.: "Reading your CV..." → "Understanding your background..." → "Finding your best matches...". This can be a simple timed sequence of messages during the single loading period — it doesn't need to be wired to real backend progress events.

### 4. Empty / error states

- No file selected when the user clicks upload: inline validation message, no request sent.
- Upload fails (bad file type, unparseable, backend error): show the specific error message from the backend in a clearly-styled error component, with a way to try again.
- Match returns zero results (shouldn't normally happen with a seeded dataset, but handle it): a clear "no matches found" state rather than a blank screen.

### 5. Responsive layout pass

- Single-column, comfortable layout on mobile widths (~375px) as well as desktop.
- Check touch target sizes on the upload button and card links.
- Test in the browser's device toolbar or by resizing the window narrow — don't just assume desktop CSS reflows correctly.

### 6. Visual identity

- Pick a simple, consistent color palette and type scale (doesn't need to be elaborate — consistency matters more than complexity). Apply it across the upload page and results page so they read as one product.

## Acceptance criteria

- [ ] The full flow — from landing on the site, through upload, loading, to seeing ranked results — looks and feels intentional on both desktop and mobile widths.
- [ ] Every error path (bad file, backend failure, no matches) has a real, styled state — nothing renders as a blank page or an unhandled console error.
- [ ] No functional regressions versus Day 4 — the underlying data flow is unchanged, only presentation.

## Commit

```
Polish results UI, add loading/error/empty states, responsive layout pass
```
Push to `main`.
