"""FastAPI app — API routes must be registered BEFORE the SPA catch-all."""
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


# Register API routers BEFORE /{full_path:path}, otherwise the catch-all
# matches /api/v1/* first and returns {"detail":"Not Found"}.
try:
    from apps.api.routers import ai, metrics

    app.include_router(metrics.router, prefix="/api/v1")
    app.include_router(ai.router, prefix="/api/v1")
    print("[adinfra] API routes registered at import", flush=True)
except Exception as exc:  # noqa: BLE001
    print(f"[adinfra] WARNING: API routes failed to load: {exc!r}", flush=True)


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


def _seed_demo_data() -> None:
    """Ensure demo curated files exist so the UI is not empty on Railway."""
    from datetime import date

    from packages.collectors.registry import get_all_collectors
    from packages.common.config import get_settings
    from packages.transformers.pipeline import transform_day

    day = date(2026, 7, 13)
    settings = get_settings()
    marker = settings.curated_dir / day.isoformat() / "daily_media_summary.parquet"
    if marker.exists():
        return
    for collector in get_all_collectors():
        collector.collect(day)
    transform_day(day, settings)
    print(f"[adinfra] seeded demo data for {day.isoformat()}", flush=True)


@app.on_event("startup")
async def on_startup() -> None:
    try:
        _seed_demo_data()
    except Exception as exc:  # noqa: BLE001
        print(f"[adinfra] demo seed skipped: {exc!r}", flush=True)


@app.get("/{full_path:path}", response_model=None)
def spa_and_static(full_path: str):
    if full_path == "health":
        return health()

    # API/docs are registered above; if we reach here they truly don't exist.
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
