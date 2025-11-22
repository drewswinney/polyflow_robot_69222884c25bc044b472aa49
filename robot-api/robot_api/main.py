import os
import secrets
import subprocess
from pathlib import Path
from typing import Iterable, Optional, Set

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import WifiRequest, WifiStatus
from .tasks import write_wifi_conf, clear_wifi_conf, run_switch, read_wifi_conf


def load_or_create_token(path: Path) -> str:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        token = secrets.token_hex(32)
        path.write_text(token)
        return token
    return path.read_text().strip()


def build_allowed_origins(raw: Optional[str]) -> Set[str]:
    if not raw:
        return set()
    return {o.strip() for o in raw.split(",") if o.strip()}


def require_auth(required_token: str):
    # Allow unauthenticated requests from trusted local subnets (loopback, hotspot)
    def _is_trusted_host(host: str) -> bool:
        return (
            host in {"127.0.0.1", "::1", "localhost"}
            or host.startswith("10.42.")  # NetworkManager shared/hotspot default
        )

    async def _auth(request: Request):
        # Allow unauthenticated health checks
        if request.url.path == "/health":
            return
        # Allow loopback/hotspot without token
        client_host = request.client.host if request.client else ""
        if _is_trusted_host(client_host):
          return
        header = request.headers.get("authorization", "")
        if not header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        token = header.removeprefix("Bearer ").strip()
        if token != required_token:
            raise HTTPException(status_code=403, detail="invalid token")
    return _auth


def create_app() -> FastAPI:
    token_path = Path(os.environ.get("ROBOT_API_TOKEN_PATH", "/var/lib/polyflow/api_token"))
    token = load_or_create_token(token_path)
    allowed_origins = build_allowed_origins(os.environ.get("ROBOT_API_ALLOWED_ORIGINS"))

    app = FastAPI()

    if allowed_origins:
        app.add_middleware(
          CORSMiddleware,
          allow_origins=list(allowed_origins),
          allow_methods=["*"],
          allow_headers=["*"],
        )

    auth_dep = Depends(require_auth(token))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/wifi", response_model=WifiStatus, dependencies=[auth_dep])
    def get_wifi():
        return WifiStatus(**read_wifi_conf())

    @app.post("/wifi", dependencies=[auth_dep])
    def set_wifi(body: WifiRequest):
        try:
            write_wifi_conf(body.ssid, body.psk)
            run_switch()
        except subprocess.CalledProcessError as exc:
            raise HTTPException(status_code=500, detail=f"wifi switch failed: {exc}")
        return {"status": "ok"}

    @app.post("/wifi/clear", dependencies=[auth_dep])
    def clear_wifi():
        try:
            clear_wifi_conf()
            run_switch()
        except subprocess.CalledProcessError as exc:
            raise HTTPException(status_code=500, detail=f"wifi switch failed: {exc}")
        return {"status": "ok"}

    return app


def main():
    import uvicorn
    uvicorn.run(
        create_app(),
        host="0.0.0.0",
        port=int(os.environ.get("ROBOT_API_PORT", "8082")),
    )


if __name__ == "__main__":
    main()
