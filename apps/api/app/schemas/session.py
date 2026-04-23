from typing import Optional

from pydantic import BaseModel


class SessionResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    organization_id: str
    role: str


class LoginRequest(BaseModel):
    email: str = "ops@killcont.demo"
    display_name: str = "KillCont Demo Operator"
    id_token: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    user: SessionResponse
