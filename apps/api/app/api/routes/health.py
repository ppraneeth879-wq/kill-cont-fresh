from typing import Any

from fastapi import APIRouter

from app.core.config import get_settings
from app.services import triage


router = APIRouter()


@router.get("")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/profile")
def health_profile() -> dict[str, Any]:
    settings = get_settings()
    return {
        "runtime_profile": settings.runtime_profile,
        "metadata_backend": settings.metadata_backend,
        "media_backend": settings.media_backend,
        "auth_backend": settings.auth_backend,
        "app_version": settings.app_version,
        "sse_state": "ready",
        "gemini": triage.current_gemini_snapshot(),
        "phash_threshold": settings.phash_match_threshold,
        "public_web_origin": settings.public_web_origin or None,
        "allowed_origins": settings.allowed_origins_list,
    }
