from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chat import router as chat_router
from app.routes.job_fit import router as job_fit_router
from app.routes.summary import router as summary_router


app = FastAPI(title="AI Portfolio Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(job_fit_router, prefix="/job-fit", tags=["job-fit"])
app.include_router(summary_router, prefix="/profile-summary", tags=["summary"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
