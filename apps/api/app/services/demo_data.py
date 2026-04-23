"""Legacy hardcoded demo data (pre-MVP).

This module is retained as a compatibility shim only. All live data now flows
through SQLite via ``app.services.repos`` and ``app.services.seeder``. Prefer
those going forward. This file can be removed once the frontend no longer
references any legacy shape.
"""

from app.schemas.asset import AssetSummary
from app.schemas.dashboard import DashboardMetric, DashboardOverviewResponse
from app.schemas.incident import IncidentSummary


def build_dashboard_overview() -> DashboardOverviewResponse:  # pragma: no cover
    return DashboardOverviewResponse(
        metrics=[
            DashboardMetric(label="Active incidents", value="0", delta="seed the demo"),
        ],
        live_sync_status="disconnected",
        active_event="Unseeded",
    )


def build_assets() -> list[AssetSummary]:  # pragma: no cover
    return []


def build_incidents() -> list[IncidentSummary]:  # pragma: no cover
    return []
