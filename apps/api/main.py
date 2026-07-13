from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

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
_RESERVED = {
    "api",
    "docs",
    "redoc",
    "openapi.json",
    "health",
    "docs/oauth2-redirect",
}


def _safe_file(rel: str) -> Path | None:
    if not STATIC_DIR.is_dir():
        return None
    candidate = (STATIC_DIR / rel).resolve()
    try:
        candidate.relative_to(STATIC_DIR.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


@app.get("/", response_model=None)
def root():
    index = _safe_file("index.html")
    if index is not None:
        return FileResponse(index)
    return JSONResponse(
        {
            "service": "DataInfrastructureSystem",
            "status": "ok",
            "docs": "/docs",
            "health": "/health",
        }
    )


@app.get("/{full_path:path}", response_model=None)
def spa_and_static(full_path: str):
    first = full_path.split("/", 1)[0]
    if first in _RESERVED or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")

    direct = _safe_file(full_path)
    if direct is not None:
        return FileResponse(direct)

    nested = _safe_file(f"{full_path.rstrip('/')}/index.html")
    if nested is not None:
        return FileResponse(nested)

    index = _safe_file("index.html")
    if index is not None:
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Not Found")
