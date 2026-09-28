# Ace-Opportunity — Live Demo Script (60–90 Seconds)

**Presenter:** Engineering / Product Lead  
**Audience:** Judges, Evaluators, and Fellowship Applicants  
**Time Limit:** ~75–90 seconds  
**Live URL:** Production Web Application (Vercel Frontend + Render Backend)

---

## The Pitch & Problem (0:00 – 0:15)

> *"Finding real internships, scholarships, and grants is broken. Traditional job boards rely on rigid keyword matching, forcing students to guess buzzwords while missing life-changing opportunities that actually fit their unique background."*
>
> *"We built **Ace-Opportunity** — an AI copilot that reads a candidate's actual CV, projects it into semantic vector space, ranks top opportunities using dense cosine similarity, and synthesizes grounded fit explanations and actionable preparation checklists."*

---

## The Walkthrough Beat-by-Beat (0:15 – 1:05)

### Beat 1: CV Ingestion & Extraction (0:15 – 0:30)
- **Action:** Open the home page. Drag and drop a real student CV (PDF or DOCX) into the drop zone (or click the sample test button: *"⚡ Test with sample CS & Robotics CV"*).
- **Spoken:**
  > *"Watch this in action. We upload a student CV — here, a computer science and robotics undergraduate with projects in Python and FastAPI. In seconds, our pipeline extracts a structured profile: verified skills, education, and career experience."*

### Beat 2: Real-time Semantic Matching & Radar Scanner (0:30 – 0:45)
- **Action:** The screen transitions to the multi-stage radar scanner (`LoadingState`) showing progress:
  - *Reading & parsing document text...*
  - *Extracting skills and career experience...*
  - *Computing dense 384-dimensional embeddings...*
  - *Scanning 25+ verified global opportunities...*
  - *Synthesizing tailored AI fit rationales...*
- **Spoken:**
  > *"Under the hood, we run local vector embeddings using `all-MiniLM-L6-v2`. Instead of naive keyword matching, our vector engine calculates cosine similarity against our curated Atlas database of scholarships, fellowships, and grants, ranking the top 5 matches."*

### Beat 3: Ranked Results & Grounded Fit Rationales (0:45 – 1:05)
- **Action:** The results view loads (`MatchResults`). Point out the candidate summary badge, then scroll to the top matches (e.g., CodePath Tech Fellowship, Bloomberg Women in Tech, NASA, DeepMind Scholarship).
- **Spoken:**
  > *"Here are the ranked results with visual semantic fit scores. Notice the callout: 'Why You Fit'. This isn't generic boilerplate. The AI specifically cites her hands-on work with Python and FastAPI, directly linking her coursework and internship to CodePath's technical placement requirements."*

### Beat 4: Actionable Preparation Checklist (1:05 – 1:20)
- **Action:** Click **"📋 Actionable Prep Checklist ✨"** on the top match card to expand the interactive drawer.
- **Spoken:**
  > *"When an applicant finds an opportunity they love, they don't have to wonder how to apply. Clicking 'Prep Checklist' generates tailored application materials with interactive checkboxes — reminding them to highlight specific projects, note rolling deadlines, and secure recommendation letters early."*
- **Action:** Check off a document item to show the interactive strike-through.

---

## Closing & Technical Highlight (1:20 – 1:30)

> *"Ace-Opportunity is fully live in production. It features a FastAPI backend on Render, React + Vite frontend on Vercel, MongoDB Atlas persistence, and zero-latency local embeddings combined with Google Gemini Flash. We bridge the gap between candidate potential and real global opportunities."*

---

## Technical Q&A Cheat Sheet (If Judges Ask)

| Question | Short Answer |
|---|---|
| **How does matching work?** | We compose structured text from candidate skills, education, and experience, embed it via `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions), and compute cosine similarity against pre-computed embeddings of our 25+ verified opportunities. |
| **How are the explanations grounded?** | The prompt passes the candidate's exact profile fields (skills, roles, degrees) and mandates citing at least one specific concrete background detail rather than generic praise. |
| **Why not just keyword search?** | Keyword search misses cross-disciplinary fits (e.g., a "robotics" student matching an "embedded autonomous systems" fellowship). Vector embeddings capture semantic intent. |
| **How does it scale?** | Embeddings are calculated locally in Python without per-token vector API costs. For larger opportunity catalogs, MongoDB Atlas Vector Search or FAISS can be dropped in seamlessly. |
