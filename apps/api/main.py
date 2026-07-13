from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

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

STATIC_DIR = Path(__file__).resolve().parents[1] / "web" / "out"


@app.get("/", response_model=None)
def root():
    index = STATIC_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return JSONResponse(
        {
            "service": "DataInfrastructureSystem",
            "message": "Frontend build not found. Open /docs for API.",
            "docs": "/docs",
            "health": "/health",
        }
    )


if STATIC_DIR.is_dir():
    next_dir = STATIC_DIR / "_next"
    if next_dir.is_dir():
        app.mount("/_next", StaticFiles(directory=str(next_dir)), name="next_assets")
    # html=True serves index.html for directory paths; registered after API routes.
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="frontend")
