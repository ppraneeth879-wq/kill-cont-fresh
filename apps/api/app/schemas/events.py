from typing import Any

from pydantic import BaseModel


class LiveEvent(BaseModel):
    type: str  # e.g. 'incident.created', 'incident.updated', 'live.segment', 'feed.ingested'
    data: dict[str, Any]
