"""Railway / Docker entrypoint — bind to $PORT."""
from __future__ import annotations

import os
import sys


def main() -> None:
    port_raw = os.environ.get("PORT") or "8080"
    try:
        port = int(port_raw)
    except ValueError:
        print(f"[adinfra] invalid PORT={port_raw!r}, fallback 8080", flush=True)
        port = 8080

    print(f"[adinfra] python={sys.version}", flush=True)
    print(f"[adinfra] cwd={os.getcwd()}", flush=True)
    print(f"[adinfra] starting uvicorn on 0.0.0.0:{port}", flush=True)

    import uvicorn

    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level=(os.environ.get("LOG_LEVEL") or "info").lower(),
    )


if __name__ == "__main__":
    main()
