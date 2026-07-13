from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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


def _mount_frontend() -> None:
    if not STATIC_DIR.exists():
        @app.get("/")
        def root_fallback() -> dict[str, str]:
            return {
                "service": "DataInfrastructureSystem",
                "message": "Frontend build not found. Open /docs for API.",
                "docs": "/docs",
                "health": "/health",
            }
        return

    assets = STATIC_DIR / "_next"
    if assets.exists():
        app.mount("/_next", StaticFiles(directory=assets), name="next_assets")

    @app.get("/")
    def serve_index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str) -> FileResponse:
        candidate = STATIC_DIR / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        index = STATIC_DIR / full_path / "index.html"
        if index.is_file():
            return FileResponse(index)
        return FileResponse(STATIC_DIR / "index.html")


_mount_frontend()
