from typing import Optional

from pydantic import BaseModel


class AssetSummary(BaseModel):
    asset_id: str
    title: str
    asset_type: str
    event_name: str
    status: str
    provenance_status: str
    incident_count: int
    preview_path: Optional[str] = None


class AssetListResponse(BaseModel):
    items: list[AssetSummary]


class AssetCreateRequest(BaseModel):
    title: str
    asset_type: str = "image"
    event_name: Optional[str] = None
    sport: Optional[str] = None
    rights_owner: Optional[str] = None
    description: Optional[str] = None
    provenance_status: str = "present"


class AssetCreateResponse(BaseModel):
    id: str
    upload_url: str


class AssetDetail(BaseModel):
    id: str
    title: str
    asset_type: str
    event_name: Optional[str] = None
    sport: Optional[str] = None
    rights_owner: Optional[str] = None
    description: Optional[str] = None
    status: str
    provenance_status: str
    primary_path: Optional[str] = None
    preview_path: Optional[str] = None
    phash: Optional[str] = None
    created_at: str
    incident_count: int
