from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.schemas.dashboard import DashboardMetric, DashboardOverviewResponse
from app.schemas.incident import IncidentSummary
from app.services import repos
from app.services.events_bus import subscriber_count


router = APIRouter()


# Bundle G: dashboard counts now go through the adapter (was raw SQL via
# get_conn() which only worked in sqlite-local — would have shown all-zero
# KPIs in cloud profile).


def _org_id(request: Request) -> str:
    return get_settings().demo_org_id


_RESOLVED_STATUSES = ("resolved", "ignored")


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(request: Request) -> DashboardOverviewResponse:
    org_id = _org_id(request)

    asset_type_counts = repos.count_assets_by_type(org_id)
    total_assets = sum(asset_type_counts.values())

    # Pull a window of incidents and bucket in Python — keeps the adapter
    # surface narrow (no need for severity-aware count helpers).
    all_incidents = repos.list_incidents(org_id=org_id, limit=500)

    def _is_open(row: dict) -> bool:
        return (row.get("operator_status") or "new") not in _RESOLVED_STATUSES

    open_incidents = [row for row in all_incidents if _is_open(row)]
    total_incidents_open = len(open_incidents)
    strike_incidents = sum(1 for row in open_incidents if row.get("severity") == "strike")

    video_count = (
        asset_type_counts.get("video", 0) + asset_type_counts.get("live_watch", 0)
    )
    image_count = asset_type_counts.get("image", 0)
    live_assets = asset_type_counts.get("live_watch", 0)

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

    recent = [IncidentSummary(**row) for row in all_incidents[:6]]

    return DashboardOverviewResponse(
        metrics=metrics,
        live_sync_status="connected",
        active_event="Championship Night",
        recent_incidents=recent,
        active_event_detail="Seeded demo scenario",
    )
