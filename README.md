# AI Portfolio Agent - Bilingual Recruiter Copilot

A bilingual AI portfolio assistant (English/French) that answers recruiter questions about your profile with citations and analyzes job descriptions with fit scoring.

## Why this project stands out
- Real conversational UX (chat with memory)
- Grounded answers from your own documents and structured profile data
- Bilingual support (FR/EN)
- Job-fit analysis with strengths, gaps, and relevant projects
- Source citations in every answer

## Core features
1. **Conversational About-Me Chat**
- Chat-style interaction (not simple Q&A)
- Recent conversation turns are sent to backend for continuity
- Answers stay grounded in retrieved evidence

2. **Job Fit Analyzer**
- Extracts and matches skills from job description
- Produces fit score + label
- Lists matched skills, missing skills, and relevant projects

3. **Bilingual behavior**
- Input in French or English
- Output follows selected language

4. **Evidence panel**
- Every answer includes source snippets
- Makes responses auditable and recruiter-trustworthy

## Tech stack
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS
- **Backend:** FastAPI, Pydantic
- **LLM:** OpenAI Responses API (with fallback mode)
- **Retrieval:** keyword + optional embeddings-based semantic retrieval (cached locally)

## Project structure
```text
AI-Portfolio-Agent/
├── frontend/
├── backend/
├── docs/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Local setup

### 1) Clone and move into repo
```bash
git clone <your-repo-url>
cd AI-Portfolio-Agent
```

### 2) Configure environment
Create a `.env` file at **project root**:
```env
OPENAI_API_KEY=your_key_here
OPENAI_CHAT_MODEL=gpt-4.1
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TOP_K=5
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

You can copy from template:
```bash
cp .env.example .env
```

### 3) Run backend
```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4) Run frontend
```bash
cd frontend
npm install
npm run dev
```

Open:
- Frontend: `http://localhost:3000`
- Backend docs: `http://127.0.0.1:8000/docs`

## API endpoints
- `POST /chat`
- `POST /job-fit`
- `GET /profile-summary`
- `GET /health`

### Example: `/chat`
Request:
```json
{
  "message": "What are his strongest AI engineering skills?",
  "language": "en",
  "history": [
    { "role": "user", "content": "Who are you?" },
    { "role": "assistant", "content": "..." }
  ]
}
```

### Example: `/job-fit`
Request:
```json
{
  "job_description": "We are hiring an AI Engineer with FastAPI, LLM, and RAG experience.",
  "language": "en"
}
```

## Data you should customize
Update these with your real profile:
- `backend/data/raw/bio_en.md`
- `backend/data/raw/bio_fr.md`
- `backend/data/raw/resume_en.md`
- `backend/data/raw/resume_fr.md`
- `backend/data/raw/projects/*.md`
- `backend/data/structured/skills.json`
- `backend/data/structured/projects.json`
- `backend/data/structured/preferences.json`

## Performance and quality notes
- Embeddings are cached in `backend/data/vector_store/embedding_cache.json`.
- If OpenAI key is missing or request fails, backend falls back to local grounded generation.
- Keep responses factual by maintaining accurate docs and structured files.

## GitHub safety checklist
- `.env` is ignored by `.gitignore`.
- Use `.env.example` for shared config template.
- Never commit real API keys.
- If a key was ever committed, rotate it immediately.

## Demo script (for recruiters)
1. Ask in English: "What kind of AI engineer is he?"
2. Ask in French: "Quels sont ses meilleurs projets en IA ?"
3. Paste a job description in `/job-fit`
4. Show fit score + gaps + cited sources

## Future improvements
- Streaming responses in chat
- Better multilingual skill normalization
- FAISS/Chroma dedicated index for larger corpora
- Evaluation benchmark (`docs/evaluation.md`) with FR/EN test set

## License
MIT
