from pydantic import BaseModel


class MatchCandidate(BaseModel):
    id: str
    feed_item_id: str
    asset_id: str
    similarity_score: float
    hamming_distance: int
    confidence_band: str
    provenance_gap: int
    created_at: str
