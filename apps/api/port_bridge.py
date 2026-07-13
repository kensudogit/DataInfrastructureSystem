"""Forward common Railway domain target ports to the real listen PORT.

When Deploy Logs show Uvicorn on :8080 but the public URL still 502s,
the domain Target Port is often still 3000/8000 (Node/Next defaults).
"""
from __future__ import annotations

import socket
import threading
from typing import Iterable


def _pipe(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        try:
            src.shutdown(socket.SHUT_RD)
        except OSError:
            pass
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def _handle(client: socket.socket, target_port: int) -> None:
    upstream: socket.socket | None = None
    try:
        upstream = socket.create_connection(("127.0.0.1", target_port), timeout=5)
        t1 = threading.Thread(target=_pipe, args=(client, upstream), daemon=True)
        t2 = threading.Thread(target=_pipe, args=(upstream, client), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except OSError:
        pass
    finally:
        try:
            client.close()
        except OSError:
            pass
        if upstream is not None:
            try:
                upstream.close()
            except OSError:
                pass


def _serve(listen_port: int, target_port: int) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", listen_port))
    sock.listen(128)
    print(
        f"[adinfra] port-bridge 0.0.0.0:{listen_port} -> 127.0.0.1:{target_port}",
        flush=True,
    )
    while True:
        client, _ = sock.accept()
        threading.Thread(
            target=_handle, args=(client, target_port), daemon=True
        ).start()


def start_port_bridges(main_port: int, candidates: Iterable[int] = (3000, 8000, 8080)) -> None:
    for listen_port in candidates:
        if listen_port == main_port:
            continue
        thread = threading.Thread(
            target=_serve, args=(listen_port, main_port), daemon=True
        )
        thread.start()
