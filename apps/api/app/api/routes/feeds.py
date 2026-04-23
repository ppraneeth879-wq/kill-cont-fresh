from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from app.core.config import get_settings
from app.schemas.feed_item import FeedItemListResponse, FeedItemSummary
from app.services import repos, storage
from app.services.db import get_conn
from app.services.events_bus import publish
from app.services.similarity import (
    compute_phash,
    confidence_band,
    derive_severity,
    hamming_distance,
    similarity_score,
    should_promote_to_incident,
)
from app.services.triage import CANNED_BY_SEVERITY, generate_triage


router = APIRouter()


def _org_id() -> str:
    return get_settings().demo_org_id


@router.get("", response_model=FeedItemListResponse)
def list_feeds(limit: int = Query(default=50, ge=1, le=200)) -> FeedItemListResponse:
    rows = repos.list_feed_items(_org_id(), limit=limit)
    return FeedItemListResponse(items=[FeedItemSummary(**r) for r in rows])


@router.get("/{feed_item_id}", response_model=FeedItemSummary)
def get_feed_item(feed_item_id: str) -> FeedItemSummary:
    row = repos.get_feed_item(feed_item_id)
    if not row:
        raise HTTPException(status_code=404, detail="feed item not found")
    return FeedItemSummary(**row)


@router.post("/ingest")
async def ingest_feed(
    source_platform: str = Form(default="unknown"),
    source_author: str = Form(default="@unknown"),
    source_region: str = Form(default=""),
    caption: str = Form(default=""),
    content_type: str = Form(default="image"),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Ingest an external feed item, run pHash match, optionally promote to incident."""

    settings = get_settings()
    feed_id = repos.new_feed_id()
    folder = storage.feed_dir(feed_id)
    ext = Path(file.filename or "upload.jpg").suffix.lower() or ".jpg"
    media = folder / f"media{ext}"
    storage.save_bytes(media, await file.read())
    preview = folder / "preview.jpg"
    storage.make_preview(media, preview)
    try:
        feed_phash = compute_phash(media)
    except Exception:
        feed_phash = None

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO feed_items (id, org_id, source_type, source_platform, "
            "   source_url, source_author, source_region, caption, content_type, "
            "   media_path, preview_path, phash) "
            "VALUES (?, ?, 'real', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                feed_id,
                _org_id(),
                source_platform,
                f"ingest://{feed_id}",
                source_author,
                source_region,
                caption,
                content_type,
                storage.relpath(media),
                storage.relpath(preview),
                feed_phash,
            ),
        )
    feed_row = repos.get_feed_item(feed_id) or {}

    # Match against all known asset pHashes.
    candidates: list[dict] = []
    incident_payload = None

    if feed_phash:
        asset_rows = repos.get_all_assets_with_phash(_org_id())
        for asset in asset_rows:
            dist = hamming_distance(feed_phash, asset["phash"])
            score = similarity_score(feed_phash, asset["phash"])
            provenance_gap = 1 if asset["provenance_status"] in ("verified", "present") else 0
            cand_id = repos.new_candidate_id()
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO match_candidates (id, feed_item_id, asset_id, "
                    "   similarity_score, hamming_distance, confidence_band, provenance_gap) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (cand_id, feed_id, asset["id"], score, dist, confidence_band(score), provenance_gap),
                )
            candidates.append(
                {
                    "asset_id": asset["id"],
                    "asset_title": asset["title"],
                    "similarity_score": score,
                    "hamming_distance": dist,
                    "provenance_gap": provenance_gap,
                }
            )

        # Best-scoring candidate drives incident promotion.
        candidates.sort(key=lambda c: c["similarity_score"], reverse=True)
        best = candidates[0] if candidates else None
        if best and should_promote_to_incident(
            best["similarity_score"],
            bool(best["provenance_gap"]),
            settings.phash_match_threshold,
        ):
            severity = derive_severity(
                best["similarity_score"], 0.5, bool(best["provenance_gap"])
            )
            triage_text = await generate_triage(
                asset={"title": best["asset_title"], "asset_type": "image",
                       "provenance_status": "verified" if best["provenance_gap"] else "unknown"},
                feed_item=feed_row,
                score=best["similarity_score"],
                severity=severity,
            )
            incident_id = repos.new_incident_id()
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO incidents (id, org_id, asset_id, feed_item_id, title, severity, "
                    "   triage_label, trust_score, spread_score, operator_status, reason_short, "
                    "   reason_detailed, operator_copy, map_region) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?, ?, ?)",
                    (
                        incident_id,
                        _org_id(),
                        best["asset_id"],
                        feed_id,
                        f"Repost detected for '{best['asset_title']}'",
                        severity,
                        severity,
                        best["similarity_score"],
                        0.5,
                        triage_text["reason_short"],
                        triage_text["reason_detailed"],
                        triage_text["operator_copy"],
                        source_region,
                    ),
                )
            incident_payload = repos.get_incident_detail(incident_id)
            await publish(
                "incident.created",
                {"incident_id": incident_id, "severity": severity},
            )

    await publish("feed.ingested", {"feed_item_id": feed_id})

    return {
        "feed_item": feed_row,
        "candidates": candidates,
        "incident": incident_payload,
    }
