from typing import Optional

from pydantic import BaseModel

from app.schemas.action import ActionRecord
from app.schemas.feed_item import FeedItemSummary
from app.schemas.match_candidate import MatchCandidate


class IncidentSummary(BaseModel):
    """Flat incident row used by the list + overview rail.

    Field names mirror the legacy demo_data contract so existing FE components
    keep working without CSS/JSX changes.
    """

    incident_id: str
    title: str
    severity: str            # 'verified' | 'monitor' | 'strike'
    platform: str            # derived from feed_item.source_platform
    matched_asset: str       # asset title
    confidence: str          # e.g. '97.8%'
    spread: str              # 'low' | 'moderate' | 'high'
    region: str              # derived from feed_item.source_region or incident.map_region
    summary: str             # reason_short

    # Extended fields (new) — optional so legacy consumers keep working.
    operator_status: Optional[str] = "new"
    asset_id: Optional[str] = None
    feed_item_id: Optional[str] = None
    created_at: Optional[str] = None


class IncidentListResponse(BaseModel):
    items: list[IncidentSummary]


class AssetBrief(BaseModel):
    id: str
    title: str
    asset_type: str
    event_name: Optional[str] = None
    provenance_status: str
    primary_path: Optional[str] = None
    preview_path: Optional[str] = None


class IncidentDetail(BaseModel):
    id: str
    title: str
    severity: str
    triage_label: str
    trust_score: float
    spread_score: float
    operator_status: str
    reason_short: Optional[str] = None
    reason_detailed: Optional[str] = None
    operator_copy: Optional[str] = None
    map_region: Optional[str] = None
    created_at: str
    updated_at: str

    asset: AssetBrief
    feed_item: FeedItemSummary
    candidates: list[MatchCandidate] = []
    actions: list[ActionRecord] = []
