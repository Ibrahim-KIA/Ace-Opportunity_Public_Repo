from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Ace-Opportunity API",
    description="AI copilot matching CVs to real opportunities.",
    version="0.1.0",
)

# Parse comma-separated origins; keep ["*"] behaviour when the env var is "*"
_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Liveness probe — returns ok when the service is running."""
    return {"status": "ok"}
