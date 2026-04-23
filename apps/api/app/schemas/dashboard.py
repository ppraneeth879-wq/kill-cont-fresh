from typing import Optional

from pydantic import BaseModel

from app.schemas.incident import IncidentSummary


class DashboardMetric(BaseModel):
    label: str
    value: str
    delta: str


class DashboardOverviewResponse(BaseModel):
    metrics: list[DashboardMetric]
    live_sync_status: str
    active_event: str
    recent_incidents: list[IncidentSummary] = []
    active_event_detail: Optional[str] = None
