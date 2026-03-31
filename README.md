# Joseph AI Portfolio Agent

A bilingual AI recruiter copilot that presents Joseph Elias Al Khoury through conversational Q&A and role-fit analysis.

## Project Overview
This project is an AI portfolio experience designed for hiring teams. Instead of reading a static CV, recruiters can interact with a conversational assistant, explore evidence-backed experience, and run job-fit checks against real role descriptions.

The product is built to answer one practical question fast:
**"Is this profile relevant for this role, and why?"**

## What the Product Does
- **Conversational profile assistant (EN/FR):** Ask questions about experience, projects, strengths, education, and positioning.
- **Job-fit analyzer:** Paste a job description and get a structured fit synthesis with matched skills, gaps, and project alignment.
- **Profile links hub:** Direct access to CVs, GitHub, LinkedIn, and technical portfolio.

## Why It Stands Out
- **Interactive instead of static:** Recruiters can explore the profile dynamically.
- **Grounded responses:** Answers are tied to profile/project evidence, not generic claims.
- **Bilingual by design:** Full English/French flow for broader hiring contexts.
- **Recruiter-oriented output:** Job-fit results are structured for decision-making, not just model text.

## Experience Signals Highlighted in the Assistant
- AI Engineer & Co-founder at **SISSI** (LLM pipelines, semantic retrieval, product integration)
- Data Scientist in Medical Imaging at **Institut Curie** (multimodal modeling, radiomics, reproducible pipelines)
- Contributions connected to **LIFEx**, research workflows, and production-oriented AI delivery

## Job-Fit Output Format
The analyzer returns a synthesis in a clear structure:
- Verdict
- Evidence from real experience
- Skill alignment
- Gaps / risks
- Positioning advice

## Tech Stack
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Pydantic
- **LLM:** OpenAI Responses API (with controlled fallback behavior)
- **Retrieval:** profile/project-aware retrieval with optional embedding cache

## Architecture (High Level)
- Frontend collects recruiter queries and role descriptions
- Backend retrieves relevant profile/project evidence
- Composer generates bilingual responses with consistency guardrails
- Job-fit service computes matching + scoring and returns structured synthesis

## Demo Flow (Recommended)
1. Start in chat and ask: "What kind of AI engineer is he?"
2. Switch language and ask the same in French.
3. Open **Job Fit**, paste a real JD, and review the verdict + alignment.
4. Open the profile links page and access CV/GitHub/LinkedIn.

## Repository Structure
```text
AI-Portfolio-Agent/
├── frontend/
├── backend/
├── docs/
├── .env.example
└── README.md
```

## Minimal Local Run
```bash
# Backend
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## License
MIT
