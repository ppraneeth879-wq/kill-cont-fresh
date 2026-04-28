import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fastapi.responses import RedirectResponse

from app.api.router import api_router
from app.core.config import API_ROOT, get_settings
from app.services import storage
from app.services.authn import AuthConfigurationError, AuthError, authenticate_request_token
from app.services.db import init_db


_log = logging.getLogger("killcont.startup")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    summary="KillCont backend for rights protection workflows.",
)

# --- CORS (explicit allowlist) ---------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# --- Auth middleware ------------------------------------------------------

PUBLIC_PATHS = (
    "/api/v1/session/login",
    "/api/v1/health",
)


@app.middleware("http")
async def app_auth(request: Request, call_next):
    path = request.url.path

    # CORS preflight: browsers send OPTIONS without Authorization. CORSMiddleware
    # (registered above) will short-circuit and answer with the right headers,
    # but middleware order means our auth check still runs unless we exempt
    # OPTIONS explicitly. Without this, every cross-origin POST/PATCH/DELETE
    # fails with "Failed to fetch" because the preflight gets 401.
    if request.method == "OPTIONS":
        return await call_next(request)

    # Only guard /api/v1 paths that aren't on the explicit public list.
    if path.startswith("/api/v1") and not path.startswith(PUBLIC_PATHS):
        token = request.headers.get("authorization") or ""
        # EventSource can't set headers, so honour ?token=... too.
        if not token and request.url.query:
            query_token = request.query_params.get("token")
            if query_token:
                token = f"Bearer {query_token}"
        try:
            identity = authenticate_request_token(token)
            request.state.user_id = identity.user_id
        except AuthConfigurationError:
            return JSONResponse({"error": "auth backend misconfigured"}, status_code=500)
        except AuthError:
            return JSONResponse({"error": "unauthorized"}, status_code=401)

    return await call_next(request)


# --- Startup / shutdown ----------------------------------------------------

@app.on_event("startup")
def _startup() -> None:
    settings.media_dir_obj.mkdir(parents=True, exist_ok=True)
    init_db()
    _verify_auth_config()


def _verify_auth_config() -> None:
    """Bundle F: print a clear status line on startup so a misconfigured
    Firebase setup is obvious in stdout/log files instead of silently
    failing on the first sign-in attempt. Uses print() rather than
    logging because uvicorn's default log config doesn't surface custom
    INFO loggers reliably."""
    if settings.auth_backend == "firebase":
        if settings.firebase_credentials_path:
            path = Path(settings.firebase_credentials_path)
            if not path.is_absolute():
                path = API_ROOT / path
            if path.exists():
                print(f"[killcont.startup] AUTH_BACKEND=firebase using credentials at {path}")
            else:
                print(
                    f"[killcont.startup] WARNING: AUTH_BACKEND=firebase but "
                    f"FIREBASE_CREDENTIALS_PATH={settings.firebase_credentials_path} "
                    f"does not exist - sign-in will fail until this is fixed",
                    flush=True,
                )
        else:
            print("[killcont.startup] AUTH_BACKEND=firebase using Application Default Credentials")
    else:
        print(
            f"[killcont.startup] AUTH_BACKEND={settings.auth_backend} "
            f"(demo mode - anyone can sign in with email+name)"
        )


# --- Root + routers --------------------------------------------------------

@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "environment": settings.app_env,
        "status": "ready",
    }


app.include_router(api_router, prefix="/api/v1")

# Expose uploaded media so the FE can <img src="/media/...">.
# Local profile: serve directly from disk.
# Public profile: 302-redirect every /media/* to the GCS object URL so
# the FE keeps using the same relative paths.
media_dir = settings.media_dir_obj
media_dir.mkdir(parents=True, exist_ok=True)

if storage.is_cloud_backend():

    @app.get("/media/{path:path}", tags=["media"])
    def media_redirect(path: str):
        return RedirectResponse(url=storage.public_url_for(path), status_code=302)

else:
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")
