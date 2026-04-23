from typing import Optional

from pydantic import BaseModel


class FeedItemSummary(BaseModel):
    id: str
    source_type: str
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    source_author: Optional[str] = None
    source_region: Optional[str] = None
    caption: Optional[str] = None
    content_type: str
    media_path: Optional[str] = None
    preview_path: Optional[str] = None
    phash: Optional[str] = None
    ingest_time: str


class FeedItemListResponse(BaseModel):
    items: list[FeedItemSummary]


class FeedItemIngestRequest(BaseModel):
    source_type: str = "simulated"
    source_platform: Optional[str] = None
    source_url: Optional[str] = None
    source_author: Optional[str] = None
    source_region: Optional[str] = None
    caption: Optional[str] = None
    content_type: str = "image"
    # For ingest-by-url / seeded flows a pre-computed hash can be supplied.
    phash: Optional[str] = None
