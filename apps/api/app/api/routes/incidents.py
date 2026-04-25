from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

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


@router.get("/{incident_id}/notice", response_class=PlainTextResponse)
def download_notice(incident_id: str) -> PlainTextResponse:
    """Generate a Markdown takedown notice for an incident."""
    detail = repos.get_incident_detail(incident_id)
    if not detail:
        raise HTTPException(status_code=404, detail="incident not found")

    asset = detail.get("asset", {}) or {}
    feed = detail.get("feed_item", {}) or {}
    candidates = detail.get("candidates", []) or []
    top = candidates[0] if candidates else {}

    severity = (detail.get("severity") or "monitor").upper()
    trust = detail.get("trust_score") or 0
    spread = detail.get("spread_score") or 0
    sim = top.get("similarity_score") or 0
    ham = top.get("hamming_distance")
    band = top.get("confidence_band") or "unknown"
    provenance = (asset.get("provenance_status") or "unknown").replace("_", " ").title()
    platform = feed.get("source_platform") or "unknown platform"
    region = feed.get("source_region") or detail.get("map_region") or "unknown region"
    author = feed.get("source_author") or "unknown author"
    source_url = feed.get("source_url") or "(not captured)"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Takedown Notice — Incident {incident_id}",
        "",
        f"**Generated:** {generated_at}",
        f"**Severity:** {severity}",
        f"**Operator status:** {detail.get('operator_status', 'open')}",
        "",
        "## 1. Protected asset (rights holder)",
        "",
        f"- **Title:** {asset.get('title', '—')}",
        f"- **Asset ID:** {asset.get('id', '—')}",
        f"- **Type:** {asset.get('asset_type', '—')}",
        f"- **Event:** {asset.get('event_name', '—')}",
        f"- **Provenance:** {provenance}",
        "",
        "## 2. Infringing upload",
        "",
        f"- **Platform:** {platform}",
        f"- **Author handle:** {author}",
        f"- **Region:** {region}",
        f"- **Source URL:** {source_url}",
        f"- **Ingested:** {feed.get('ingest_time', '—')}",
        f"- **Caption:** {feed.get('caption') or '(none captured)'}",
        "",
        "## 3. Match evidence",
        "",
        f"- **Perceptual-hash similarity:** {sim * 100:.1f}%",
        f"- **Hamming distance (64-bit pHash):** {ham if ham is not None else '—'}",
        f"- **Confidence band:** {band}",
        f"- **Trust score:** {trust * 100:.0f}%",
        f"- **Spread score:** {spread * 100:.0f}%",
        "",
        "## 4. Why this is a match",
        "",
        detail.get("reason_detailed") or detail.get("reason_short") or "(no reason recorded)",
        "",
        "## 5. Operator recommendation",
        "",
        detail.get("operator_copy") or "(no recommendation recorded)",
        "",
        "## 6. Requested action",
        "",
        "The rights holder requests immediate removal of the infringing upload above",
        "under applicable platform policy and copyright law. This notice is generated",
        "from automated perceptual-hash matching against a registered protected asset;",
        "the full evidence pack — including candidate frames and match ledger — is",
        "available on request.",
        "",
        f"— KillCont evidence system · incident {incident_id}",
        "",
    ]

    body = "\n".join(lines)
    filename = f"killcont-notice-{incident_id}.md"
    return PlainTextResponse(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
