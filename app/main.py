from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import call_center
from app.core.config import get_settings

app = FastAPI(
    title="Call Center AI Analysis Platform",
    description="Multi-agent call center analysis with transcription, summarization, quality scoring, and routing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(call_center.router, prefix="/api/v1/call-center", tags=["Call Center"])


@app.get("/health")
async def health_check():
    settings = get_settings()
    return {"status": "healthy", "env": settings.app_env}
