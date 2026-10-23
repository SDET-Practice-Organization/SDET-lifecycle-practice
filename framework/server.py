import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_healthy(base_url: str, proc: subprocess.Popen, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"App process exited early with code {proc.returncode}")
        try:
            if requests.get(f"{base_url}/health", timeout=1).ok:
                return
        except requests.ConnectionError:
            pass
        time.sleep(0.2)
    raise TimeoutError(f"App at {base_url} not healthy after {timeout}s")


@contextmanager
def running_app(startup_timeout: float = 15.0) -> Iterator[str]:
    """Start TaskApp with uvicorn on a free port and yield its base URL.

    The child inherits the environment, so TASKAPP_BUGS / TASKAPP_API_KEY apply.
    """
    port = _free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=PROJECT_ROOT,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        _wait_until_healthy(base_url, proc, startup_timeout)
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
