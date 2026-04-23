from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.schemas.dashboard import DashboardMetric, DashboardOverviewResponse
from app.schemas.incident import IncidentSummary
from app.services import repos
from app.services.db import get_conn
from app.services.events_bus import subscriber_count


router = APIRouter()


def _org_id(request: Request) -> str:
    return get_settings().demo_org_id


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(request: Request) -> DashboardOverviewResponse:
    org_id = _org_id(request)

    with get_conn() as conn:
        total_assets = conn.execute(
            "SELECT COUNT(*) AS n FROM assets WHERE org_id = ?", (org_id,)
        ).fetchone()["n"]
        asset_type_counts = conn.execute(
            "SELECT asset_type, COUNT(*) AS n FROM assets WHERE org_id = ? GROUP BY asset_type",
            (org_id,),
        ).fetchall()
        total_incidents_open = conn.execute(
            "SELECT COUNT(*) AS n FROM incidents "
            "  WHERE org_id = ? AND operator_status NOT IN ('resolved','ignored')",
            (org_id,),
        ).fetchone()["n"]
        strike_incidents = conn.execute(
            "SELECT COUNT(*) AS n FROM incidents "
            "  WHERE org_id = ? AND severity = 'strike' "
            "    AND operator_status NOT IN ('resolved','ignored')",
            (org_id,),
        ).fetchone()["n"]
        live_assets = conn.execute(
            "SELECT COUNT(*) AS n FROM assets WHERE org_id = ? AND asset_type = 'live_watch'",
            (org_id,),
        ).fetchone()["n"]

    type_breakdown = {r["asset_type"]: r["n"] for r in asset_type_counts}
    video_count = type_breakdown.get("video", 0) + type_breakdown.get("live_watch", 0)
    image_count = type_breakdown.get("image", 0)

    metrics = [
        DashboardMetric(
            label="Active incidents",
            value=str(total_incidents_open),
            delta=f"{strike_incidents} strike • {total_incidents_open - strike_incidents} monitor",
        ),
        DashboardMetric(
            label="Protected assets",
            value=str(total_assets),
            delta=f"{video_count} video / {image_count} image",
        ),
        DashboardMetric(
            label="Detection latency",
            value="< 1s",
            delta="pHash in-process",
        ),
        DashboardMetric(
            label="Live watch alerts",
            value=str(live_assets),
            delta=f"{subscriber_count()} streams connected",
        ),
    ]

    recent = [IncidentSummary(**row) for row in repos.list_incidents(org_id=org_id, limit=6)]

    return DashboardOverviewResponse(
        metrics=metrics,
        live_sync_status="connected",
        active_event="Championship Night",
        recent_incidents=recent,
        active_event_detail="Seeded demo scenario",
    )
