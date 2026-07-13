from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routers import ai, health, metrics

app = FastAPI(
    title="Ad Data Infrastructure API",
    description="Multi-platform advertising metrics, reports, and AI optimization",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
