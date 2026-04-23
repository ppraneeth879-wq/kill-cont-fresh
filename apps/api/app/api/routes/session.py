from fastapi import APIRouter, HTTPException, Request

from app.core.config import get_settings
from app.schemas.session import LoginRequest, LoginResponse, SessionResponse
from app.services.authn import AuthConfigurationError, AuthError, auth_backend, verify_firebase_id_token
from app.services import repos


router = APIRouter()


def _user_to_response(user: dict) -> SessionResponse:
    return SessionResponse(
        user_id=user["id"],
        email=user["email"],
        display_name=user["display_name"],
        organization_id=user["org_id"],
        role=user.get("role") or "admin",
    )


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    settings = get_settings()
    mode = auth_backend()

    if mode == "firebase":
        if not body.id_token:
            raise HTTPException(status_code=400, detail="firebase id_token is required")
        try:
            claims = verify_firebase_id_token(body.id_token)
        except AuthConfigurationError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except AuthError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        user_id = str(claims.get("uid") or claims.get("user_id") or claims.get("sub") or "").strip()
        if not user_id:
            raise HTTPException(status_code=401, detail="firebase token missing uid")
        email = str(claims.get("email") or body.email or "").strip() or "unknown@killcont.demo"
        display_name = str(claims.get("name") or body.display_name or "").strip() or "KillCont Operator"
        token = body.id_token
    else:
        user_id = settings.demo_default_user_id
        email = body.email
        display_name = body.display_name
        token = f"killcont-demo-{user_id}"

    user = repos.upsert_user(
        user_id=user_id,
        email=email,
        display_name=display_name,
        org_id=settings.demo_org_id,
    )

    return LoginResponse(
        token=token,
        user=_user_to_response(user),
    )


@router.get("/me", response_model=SessionResponse)
def get_session(request: Request) -> SessionResponse:
    user_id = getattr(request.state, "user_id", None) or get_settings().demo_default_user_id
    user = repos.get_user(user_id)
    if not user:
        # Auto-provision the default demo user so /me works right after a reset.
        settings = get_settings()
        user = repos.upsert_user(
            user_id=user_id,
            email="ops@killcont.demo",
            display_name="KillCont Demo Operator",
            org_id=settings.demo_org_id,
        )
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return _user_to_response(user)
