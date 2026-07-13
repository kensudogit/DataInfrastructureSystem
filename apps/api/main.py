"""FastAPI app — keep import-time deps minimal so Railway can boot."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

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

STATIC_DIR = Path(__file__).resolve().parents[1] / "web" / "out"


def _safe_file(rel: str) -> Path | None:
    if not STATIC_DIR.is_dir():
        return None
    candidate = (STATIC_DIR / rel).resolve()
    try:
        candidate.relative_to(STATIC_DIR.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "DataInfrastructureSystem"}


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


def _register_api_routes() -> None:
    """Import heavy routers only after the process is alive."""
    from apps.api.routers import ai, metrics

    app.include_router(metrics.router, prefix="/api/v1")
    app.include_router(ai.router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    try:
        _register_api_routes()
        print("[adinfra] API routes registered", flush=True)
    except Exception as exc:  # noqa: BLE001 — keep process alive on Railway
        print(f"[adinfra] WARNING: API routes failed to load: {exc!r}", flush=True)


@app.get("/{full_path:path}", response_model=None)
def spa_and_static(full_path: str):
    # Never 404 the health alias if routing order differs by platform.
    if full_path == "health":
        return health()

    # Do not swallow API/docs — return JSON 404 for reserved prefixes.
    first = full_path.split("/", 1)[0]
    if first in {"api", "docs", "redoc", "openapi.json"} or full_path.startswith("api/"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    direct = _safe_file(full_path)
    if direct is not None:
        return FileResponse(direct)

    nested = _safe_file(f"{full_path.rstrip('/')}/index.html")
    if nested is not None:
        return FileResponse(nested)

    index = _safe_file("index.html")
    if index is not None:
        return FileResponse(index)
    return JSONResponse({"detail": "Not Found"}, status_code=404)
