from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings


class AuthError(Exception):
    pass


class AuthConfigurationError(AuthError):
    pass


@dataclass
class AuthIdentity:
    user_id: str
    email: str | None = None
    display_name: str | None = None


def auth_backend() -> str:
    return (get_settings().auth_backend or "demo").strip().lower()


def _extract_bearer_raw(token: str) -> str:
    if not token or not token.startswith("Bearer "):
        raise AuthError("missing bearer token")
    raw = token.removeprefix("Bearer ").strip()
    if not raw:
        raise AuthError("empty bearer token")
    return raw


def verify_demo_bearer(token: str) -> AuthIdentity:
    if not token.startswith("Bearer killcont-demo-"):
        raise AuthError("invalid demo token")
    user_id = token.removeprefix("Bearer killcont-demo-") or get_settings().demo_default_user_id
    return AuthIdentity(user_id=user_id)


def verify_firebase_bearer(token: str) -> AuthIdentity:
    raw = _extract_bearer_raw(token)
    claims = verify_firebase_id_token(raw)
    user_id = str(claims.get("uid") or claims.get("user_id") or claims.get("sub") or "").strip()
    if not user_id:
        raise AuthError("firebase token missing uid")
    return AuthIdentity(
        user_id=user_id,
        email=str(claims.get("email") or "").strip() or None,
        display_name=str(claims.get("name") or "").strip() or None,
    )


def verify_firebase_id_token(id_token: str) -> dict[str, Any]:
    settings = get_settings()

    try:
        import firebase_admin
        from firebase_admin import auth, credentials
    except ImportError as exc:
        raise AuthConfigurationError(
            "firebase auth backend requires firebase-admin package"
        ) from exc

    app = None
    try:
        app = firebase_admin.get_app()
    except ValueError:
        if settings.firebase_credentials_path:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            app = firebase_admin.initialize_app(cred)
        else:
            app = firebase_admin.initialize_app()

    try:
        return auth.verify_id_token(id_token, app=app)
    except Exception as exc:
        raise AuthError("invalid firebase id token") from exc


def authenticate_request_token(token: str) -> AuthIdentity:
    mode = auth_backend()
    if mode == "firebase":
        return verify_firebase_bearer(token)
    return verify_demo_bearer(token)
