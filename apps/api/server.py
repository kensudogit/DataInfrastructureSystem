"""Railway / Docker entrypoint — MUST use Railway-injected PORT."""
from __future__ import annotations

import os
import sys


def main() -> None:
    # Railway always injects PORT. Never hardcode a listen port.
    port_raw = os.environ.get("PORT")
    if not port_raw:
        print(
            "[adinfra] WARNING: PORT is unset. "
            "On Railway this usually causes 502. Falling back to 8080 for local only.",
            flush=True,
        )
        port_raw = "8080"
    port = int(port_raw)

    print(f"[adinfra] python={sys.version.split()[0]}", flush=True)
    print(f"[adinfra] cwd={os.getcwd()}", flush=True)
    print(f"[adinfra] env.PORT={os.environ.get('PORT')!r}", flush=True)
    print(f"[adinfra] binding 0.0.0.0:{port}", flush=True)

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
