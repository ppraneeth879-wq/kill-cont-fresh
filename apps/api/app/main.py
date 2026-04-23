from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.services.authn import AuthConfigurationError, AuthError, authenticate_request_token
from app.services.db import init_db


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
media_dir = settings.media_dir_obj
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")
