"""Railway / Docker entrypoint — bind to $PORT."""
from __future__ import annotations

import os

import uvicorn


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    print(f"[adinfra] starting uvicorn on 0.0.0.0:{port}", flush=True)
    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
    )


if __name__ == "__main__":
    main()
