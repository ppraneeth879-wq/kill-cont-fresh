from typing import Optional

from pydantic import BaseModel


class ActionRecord(BaseModel):
    id: str
    incident_id: str
    by_user_id: str
    type: str
    notes: Optional[str] = None
    created_at: str


class ActionCreate(BaseModel):
    type: str  # 'ignore' | 'monitor' | 'escalate' | 'note' | 'reviewing'
    notes: Optional[str] = None


class IncidentStatusUpdate(BaseModel):
    status: str  # new | reviewing | monitoring | escalated | resolved | ignored
