"""Demo control endpoints.

These are what the Settings → Demo Control panel talks to.
"""

from __future__ import annotations

import asyncio
import random
from typing import Optional

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.core.config import get_settings
from app.services import repos, storage
from app.services.events_bus import publish
from app.services.seeder import seed_championship_final
from app.services.similarity import (
    confidence_band,
    derive_severity,
    hamming_distance,
    similarity_score,
    should_promote_to_incident,
)
from app.services.triage import generate_triage


router = APIRouter()


class SeedRequest(BaseModel):
    scenario: str = "championship-final"


class SimulateRequest(BaseModel):
    asset_id: Optional[str] = None
    platform: Optional[str] = None
    severity: Optional[str] = None


class LiveStartRequest(BaseModel):
    segments: int = 5
    interval_seconds: float = 2.0
    asset_id: Optional[str] = None
    platform: Optional[str] = None


def _org_id() -> str:
    return get_settings().demo_org_id


# --- Seed / reset ------------------------------------------------------------

@router.post("/seed")
async def seed(body: SeedRequest):
    counts = seed_championship_final()
    await publish("demo.seeded", counts)
    return {"ok": True, "scenario": body.scenario, **counts}


@router.post("/reset")
async def reset():
    counts = seed_championship_final()
    await publish("demo.reset", counts)
    return {"ok": True, **counts}


# --- Simulate a new repost incident -----------------------------------------

SIMULATED_PLATFORMS = [
    "piracy-mirror",
    "youtube",
    "reddit",
    "fan-clip-feed",
    "telegram-broadcast",
]

SIMULATED_REGIONS = [
    "Singapore -> London -> Dubai",
    "Bengaluru -> Berlin",
    "Cairo -> Nairobi",
    "Lisbon -> São Paulo",
    "Seoul -> Tokyo",
    "Jakarta -> Manila",
]


def _pick_asset(asset_id: Optional[str]) -> Optional[dict]:
    rows = repos.get_all_assets_with_phash(_org_id())
    if not rows:
        return None
    if asset_id:
        for row in rows:
            if row["id"] == asset_id:
                return row
    return random.choice(rows)


@router.post("/simulate-incident")
async def simulate_incident(body: SimulateRequest):
    settings = get_settings()
    asset = _pick_asset(body.asset_id)
    if not asset:
        return {"ok": False, "error": "no assets available — run /demo/seed first"}

    asset_full = repos.get_asset_detail(asset["id"]) or {}
    platform = body.platform or random.choice(SIMULATED_PLATFORMS)
    region = random.choice(SIMULATED_REGIONS)

    # Create a mutated feed-item image from the asset's primary.
    feed_id = repos.new_feed_id()
    folder = storage.feed_dir(feed_id)
    media_target = folder / "media.jpg"
    primary_rel = asset_full.get("primary_path") or ""
    primary_path = settings.media_dir_obj / primary_rel
    if not primary_path.exists():
        # Fall back to a generated placeholder so the endpoint never hard-fails.
        storage.generate_placeholder_image(
            primary_path,
            (80, 80, 80),
            f"Seed replacement for {asset['id']}",
        )
    storage.derive_repost(primary_path, media_target, label=platform.upper())
    preview_target = folder / "preview.jpg"
    storage.make_preview(media_target, preview_target)
    try:
        from app.services.similarity import compute_phash
        feed_phash = compute_phash(media_target)
    except Exception:
        feed_phash = asset["phash"]

    repos.insert_feed_item(
        {
            "id": feed_id,
            "org_id": _org_id(),
            "source_type": "simulated",
            "source_platform": platform,
            "source_url": f"https://{platform}.example/{feed_id}",
            "source_author": f"@sim-{random.randint(100, 999)}",
            "source_region": region,
            "caption": f"Simulated repost against {asset['id']}",
            "content_type": "image",
            "media_path": storage.relpath(media_target),
            "preview_path": storage.relpath(preview_target),
            "phash": feed_phash,
        }
    )

    # Score + candidate row.
    distance = hamming_distance(asset["phash"], feed_phash)
    score = similarity_score(asset["phash"], feed_phash)
    provenance_gap = 1 if asset["provenance_status"] in ("verified", "present") else 0
    cand_id = repos.new_candidate_id()
    repos.insert_match_candidate(
        {
            "id": cand_id,
            "feed_item_id": feed_id,
            "asset_id": asset["id"],
            "similarity_score": score,
            "hamming_distance": distance,
            "confidence_band": confidence_band(score),
            "provenance_gap": provenance_gap,
        }
    )

    # Force promotion so the demo moment never misses — the scoring still shows
    # on the detail page and judges see the severity badge.
    spread = 0.75
    severity = body.severity or derive_severity(score, spread, bool(provenance_gap))
    if not should_promote_to_incident(score, bool(provenance_gap), settings.phash_match_threshold):
        severity = severity or "monitor"

    triage_text = await generate_triage(asset_full, repos.get_feed_item(feed_id) or {}, score, severity)
    # Capture immediately — these are module-level globals on triage.py and
    # mutate on every generate_triage() call.
    from app.services.triage import LAST_GEMINI_LATENCY_MS, LAST_GEMINI_SOURCE
    triage_source = LAST_GEMINI_SOURCE
    triage_model = settings.gemini_model if triage_source == "gemini" else None
    triage_latency = LAST_GEMINI_LATENCY_MS if triage_source == "gemini" else None

    incident_id = repos.new_incident_id()
    from app.services.geo import coords_for_region
    coords = coords_for_region(region)
    lat, lng = coords if coords else (None, None)
    repos.insert_incident(
        {
            "id": incident_id,
            "org_id": _org_id(),
            "asset_id": asset["id"],
            "feed_item_id": feed_id,
            "title": f"{platform.title()} repost detected for '{asset['title']}'",
            "severity": severity,
            "triage_label": severity,
            "trust_score": score,
            "spread_score": spread,
            "operator_status": "new",
            "reason_short": triage_text["reason_short"],
            "reason_detailed": triage_text["reason_detailed"],
            "operator_copy": triage_text["operator_copy"],
            "map_region": region,
            "map_lat": lat,
            "map_lng": lng,
            "asset_title": asset["title"],
            "source_platform": platform,
            "source_region": region,
            "triage_source": triage_source,
            "triage_model": triage_model,
            "triage_latency_ms": triage_latency,
        }
    )

    detail = repos.get_incident_detail(incident_id)

    # Announce to SSE clients.
    await publish(
        "incident.created",
        {"incident_id": incident_id, "severity": severity, "asset_id": asset["id"]},
    )

    return {"ok": True, "incident": detail}


# --- Live watch segment emitter ---------------------------------------------

LIVE_SEGMENT_STATUSES = [
    "Segment clean",
    "Signal match",
    "Segment clean",
    "Restream suspected",
    "Segment clean",
]


# Bundle C1: any segment whose status sits in this set produces a real
# incident. Both "Restream suspected" (i % 5 == 3) and "Signal match"
# (i % 5 == 1) qualify, so an 8-segment run promotes ~3 incidents instead
# of the previous 1 — the Fresh-from-matcher rail visibly cycles.
PROMOTING_STATUSES = {"Restream suspected", "Signal match"}


async def _live_emitter(
    segments: int,
    interval: float,
    asset_id: Optional[str] = None,
    platform: Optional[str] = None,
) -> None:
    total = max(1, segments)
    minute_base = random.randint(68, 88)
    promotion_idx = 0
    for i in range(total):
        await asyncio.sleep(interval)
        status = LIVE_SEGMENT_STATUSES[i % len(LIVE_SEGMENT_STATUSES)]
        payload = {
            "index": i + 1,
            "total": total,
            "minute": f"{minute_base}:{(18 + i * 6) % 60:02d}",
            "source": random.choice([
                "Primary feed A",
                "Short relay node",
                "Mirror ingest",
                "Dubai relay",
                "Nairobi edge",
                "Lisbon CDN",
            ]),
            "status": status,
            "latency_seconds": random.randint(28, 58),
        }
        await publish("live.segment", payload)

        # Bundle C1: rotate the platform per promoted incident so consecutive
        # rail rows look distinct (piracy-mirror -> youtube -> reddit -> ...).
        # If the operator pinned a specific platform on /live/start we honor
        # that and skip the rotation.
        if status in PROMOTING_STATUSES:
            chosen_platform = (
                platform
                if platform
                else SIMULATED_PLATFORMS[promotion_idx % len(SIMULATED_PLATFORMS)]
            )
            promotion_idx += 1
            try:
                await simulate_incident(
                    SimulateRequest(
                        asset_id=asset_id,
                        platform=chosen_platform,
                    )
                )
            except Exception:
                pass

    await publish("live.complete", {"segments": total})


@router.post("/live/start")
async def start_live(body: LiveStartRequest, background: BackgroundTasks):
    background.add_task(
        _live_emitter,
        body.segments,
        body.interval_seconds,
        body.asset_id,
        body.platform,
    )
    await publish(
        "live.started",
        {"segments": body.segments, "asset_id": body.asset_id},
    )
    return {
        "ok": True,
        "segments": body.segments,
        "interval_seconds": body.interval_seconds,
        "asset_id": body.asset_id,
    }
