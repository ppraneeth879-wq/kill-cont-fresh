from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from app.core.config import get_settings
from app.schemas.action import ActionCreate, ActionRecord, IncidentStatusUpdate
from app.schemas.incident import IncidentDetail, IncidentListResponse, IncidentSummary
from app.services import repos
from app.services.events_bus import publish


router = APIRouter()


def _org_id() -> str:
    return get_settings().demo_org_id


# --- Status transition triggered by action types ----------------------------

STATUS_FROM_ACTION = {
    "escalate": "escalated",
    "monitor": "monitoring",
    "ignore": "ignored",
    "reviewing": "reviewing",
}


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> IncidentListResponse:
    rows = repos.list_incidents(_org_id(), status=status, severity=severity, limit=limit)
    return IncidentListResponse(items=[IncidentSummary(**r) for r in rows])


@router.get("/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: str) -> IncidentDetail:
    detail = repos.get_incident_detail(incident_id)
    if not detail:
        raise HTTPException(status_code=404, detail="incident not found")
    return IncidentDetail(**detail)


@router.post("/{incident_id}/status", response_model=IncidentDetail)
async def update_status(incident_id: str, body: IncidentStatusUpdate) -> IncidentDetail:
    row = repos.update_incident_status(incident_id, body.status)
    if not row:
        raise HTTPException(status_code=404, detail="incident not found")
    detail = repos.get_incident_detail(incident_id)
    await publish("incident.updated", {"incident_id": incident_id, "status": body.status})
    return IncidentDetail(**detail)


@router.post("/{incident_id}/action", response_model=ActionRecord)
async def record_action(
    incident_id: str,
    body: ActionCreate,
    request: Request,
) -> ActionRecord:
    user_id = (
        getattr(request.state, "user_id", None) or get_settings().demo_default_user_id
    )
    detail = repos.get_incident_detail(incident_id)
    if not detail:
        raise HTTPException(status_code=404, detail="incident not found")

    action = repos.insert_action(
        incident_id=incident_id,
        by_user_id=user_id,
        action_type=body.type,
        notes=body.notes,
    )

    next_status = STATUS_FROM_ACTION.get(body.type)
    if next_status:
        repos.update_incident_status(incident_id, next_status)

    await publish(
        "incident.updated",
        {
            "incident_id": incident_id,
            "action": body.type,
            "status": next_status or detail["operator_status"],
        },
    )

    return ActionRecord(**action)
