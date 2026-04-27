"""On-upload matcher.

Compares a single asset's pHash against every feed_item with a pHash in
the same org. Writes match_candidate rows for every >= threshold pair,
promotes the strong ones to incidents (with Gemini triage), and returns
a list of summaries the upload route surfaces back to the frontend.

Intentionally adapter-clean: every read goes through ``repos`` helpers,
every write goes through ``repos.insert_*``. Works identically against
SQLite and Firestore once the latter is wired.
"""

from __future__ import annotations

import logging
import random
from typing import Any

from app.core.config import get_settings
from app.services import repos, storage
from app.services.events_bus import publish
from app.services.geo import coords_for_region
from app.services.similarity import (
    compute_phash,
    confidence_band,
    derive_severity,
    hamming_distance,
    similarity_score,
    should_promote_to_incident,
)
from app.services.triage import generate_triage


log = logging.getLogger(__name__)


# Cap on how many promoted incidents trigger a Gemini call per upload.
# Beyond this we keep writing match_candidate rows but use canned text so
# we don't burst the free-tier rate limit on a single user click.
GEMINI_PROMOTE_BUDGET = 20


SYNTHETIC_PLATFORMS = [
    "piracy-mirror",
    "fan-clip-feed",
    "telegram-broadcast",
]
SYNTHETIC_REGIONS = [
    "Singapore -> London -> Dubai",
    "Bengaluru -> Berlin",
    "Cairo -> Nairobi",
]


async def match_asset_against_feeds(asset_id: str) -> list[dict[str, Any]]:
    """Run the full matcher pass for one asset. See module docstring.

    Returns a list of summary dicts. Never raises — on any unexpected
    error logs + returns the partial list (or empty).
    """

    settings = get_settings()
    threshold = settings.phash_match_threshold

    asset = repos.get_asset_detail(asset_id)
    if not asset or not asset.get("phash"):
        return []

    # ``get_asset_detail`` does not return org_id by default; fall back to
    # the demo org so the matcher works on every install.
    org_id = asset.get("org_id") or settings.demo_org_id
    asset_phash = asset["phash"]
    summaries: list[dict[str, Any]] = []
    promoted = 0

    # Pass 1 (Bundle E): asset-vs-asset duplicate detection. Runs first so
    # the duplicate is the first row in the upload toast and the operator
    # sees "you already protect this" immediately.
    try:
        duplicate = await _check_duplicate_asset(asset, org_id, settings)
    except Exception:
        log.exception("matcher: duplicate-asset pass failed for %s", asset_id)
        duplicate = None
    if duplicate:
        summaries.append(duplicate)
        if duplicate.get("incident_id"):
            promoted += 1

    # Pass 2 (existing): asset x feed_item match for repost detection.
    feed_items = repos.list_feed_items(org_id, limit=500)
    for feed in feed_items:
        feed_phash = feed.get("phash")
        if not feed_phash:
            continue
        try:
            score = similarity_score(asset_phash, feed_phash)
        except Exception:  # pragma: no cover - guard against bad hashes
            continue
        if score < threshold:
            continue
        try:
            summary = await _score_pair(
                asset=asset,
                feed=feed,
                score=score,
                promoted_so_far=promoted,
            )
        except Exception:
            log.exception("matcher: failed to score pair asset=%s feed=%s", asset_id, feed.get("id"))
            continue
        summary["kind"] = "feed"
        summaries.append(summary)
        if summary.get("incident_id"):
            promoted += 1

    if not summaries and settings.synthesize_demo_match:
        try:
            summary = await _synthesize_one_match(asset)
        except Exception:
            log.exception("matcher: synthetic fallback failed for %s", asset_id)
            summary = None
        if summary:
            summaries.append(summary)

    return summaries


async def _score_pair(
    *,
    asset: dict[str, Any],
    feed: dict[str, Any],
    score: float,
    promoted_so_far: int,
    synthetic: bool = False,
) -> dict[str, Any]:
    """Insert a match_candidate, promote to incident when warranted, and
    return the FE-facing summary. Honors ``GEMINI_PROMOTE_BUDGET``."""

    settings = get_settings()
    threshold = settings.phash_match_threshold

    distance = hamming_distance(asset["phash"], feed["phash"])
    band = confidence_band(score)
    provenance_gap = 1 if asset.get("provenance_status") in ("verified", "present") else 0

    cand_id = repos.new_candidate_id()
    repos.insert_match_candidate(
        {
            "id": cand_id,
            "feed_item_id": feed["id"],
            "asset_id": asset["id"],
            "similarity_score": score,
            "hamming_distance": distance,
            "confidence_band": band,
            "provenance_gap": provenance_gap,
        }
    )

    severity = derive_severity(score, 0.6, bool(provenance_gap))
    incident_id: str | None = None
    triage_source: str | None = None

    if should_promote_to_incident(score, bool(provenance_gap), threshold):
        if promoted_so_far < GEMINI_PROMOTE_BUDGET:
            triage = await generate_triage(asset, feed, score, severity)
            # Capture the module-level snapshot immediately after the call.
            from app.services.triage import LAST_GEMINI_LATENCY_MS, LAST_GEMINI_SOURCE

            triage_source = LAST_GEMINI_SOURCE
            triage_model = settings.gemini_model if triage_source == "gemini" else None
            triage_latency = LAST_GEMINI_LATENCY_MS if triage_source == "gemini" else None
        else:
            # Throttled: keep the canned text but never call Gemini.
            from app.services.triage import _canned

            triage = _canned(severity)
            triage_source = "fallback"
            triage_model = None
            triage_latency = None

        incident_id = repos.new_incident_id()
        region = feed.get("source_region") or random.choice(SYNTHETIC_REGIONS)
        coords = coords_for_region(region)
        lat, lng = coords if coords else (None, None)
        platform = feed.get("source_platform") or "unknown"
        repos.insert_incident(
            {
                "id": incident_id,
                "org_id": asset.get("org_id") or settings.demo_org_id,
                "asset_id": asset["id"],
                "feed_item_id": feed["id"],
                "title": f"{platform.title()} repost detected for '{asset['title']}'",
                "severity": severity,
                "triage_label": severity,
                "trust_score": score,
                "spread_score": 0.6,
                "operator_status": "new",
                "reason_short": triage["reason_short"],
                "reason_detailed": triage["reason_detailed"],
                "operator_copy": triage["operator_copy"],
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
        await publish(
            "incident.created",
            {
                "incident_id": incident_id,
                "severity": severity,
                "asset_id": asset["id"],
            },
        )

    return {
        "feed_item_id": feed["id"],
        "similarity_score": score,
        "confidence_band": band,
        "severity": severity,
        "incident_id": incident_id,
        "triage_source": triage_source,
        "synthetic": synthetic,
    }


async def _synthesize_one_match(asset: dict[str, Any]) -> dict[str, Any] | None:
    """Demo-only path. Generate a derived feed item from the asset's
    primary so an upload always produces at least one visible incident.

    Gated by ``Settings.synthesize_demo_match`` (default True; off in
    public deployments).
    """

    settings = get_settings()
    if not asset.get("primary_path"):
        return None

    feed_id = repos.new_feed_id()
    folder = storage.feed_dir(feed_id)
    media_target = folder / "media.jpg"
    primary_path = settings.media_dir_obj / asset["primary_path"]
    if not primary_path.exists():
        return None

    platform = random.choice(SYNTHETIC_PLATFORMS)
    region = random.choice(SYNTHETIC_REGIONS)
    storage.derive_repost(primary_path, media_target, label=platform.upper())
    preview_target = folder / "preview.jpg"
    storage.make_preview(media_target, preview_target)
    try:
        feed_phash = compute_phash(media_target)
    except Exception:
        feed_phash = asset["phash"]

    repos.insert_feed_item(
        {
            "id": feed_id,
            "org_id": asset.get("org_id") or settings.demo_org_id,
            "source_type": "synthetic",
            "source_platform": platform,
            "source_url": f"https://{platform}.example/{feed_id}",
            "source_author": f"@sim-{random.randint(100, 999)}",
            "source_region": region,
            "caption": f"Synthetic repost generated on upload of {asset['id']}",
            "content_type": "image",
            "media_path": storage.relpath(media_target),
            "preview_path": storage.relpath(preview_target),
            "phash": feed_phash,
        }
    )

    feed_full = repos.get_feed_item(feed_id) or {}
    score = similarity_score(asset["phash"], feed_phash)
    summary = await _score_pair(
        asset=asset,
        feed=feed_full,
        score=max(score, settings.phash_match_threshold + 0.05),
        promoted_so_far=0,
        synthetic=True,
    )
    summary["kind"] = "feed"
    return summary


async def _check_duplicate_asset(
    new_asset: dict[str, Any],
    org_id: str,
    settings: Any,
) -> dict[str, Any] | None:
    """Pass 1: detect re-registration of the same image (Bundle E).

    Compares ``new_asset.phash`` against every other asset in the same org.
    On a hit at ``settings.phash_duplicate_threshold`` or above, synthesizes
    a feed_item from the new asset's pixels (so the cascade reaches Monitor
    visually), then routes through ``_score_pair`` so an incident is
    persisted with full Gemini triage.

    Returns the FE-facing summary or None if no duplicate was found.
    """

    threshold = settings.phash_duplicate_threshold
    new_phash = new_asset.get("phash")
    if not new_phash:
        return None

    best_match: dict[str, Any] | None = None
    best_score = -1.0
    for candidate in repos.get_all_assets_with_phash(org_id):
        if candidate["id"] == new_asset["id"]:
            continue
        cand_phash = candidate.get("phash")
        if not cand_phash:
            continue
        try:
            score = similarity_score(new_phash, cand_phash)
        except Exception:
            continue
        if score >= threshold and score > best_score:
            best_match = candidate
            best_score = score

    if not best_match:
        return None

    # Synthesize a feed_item that represents the duplicate registration.
    # Reuse the new asset's pixels so the Monitor row + Evidence comparison
    # render the actual re-uploaded image.
    feed_id = repos.new_feed_id()
    repos.insert_feed_item(
        {
            "id": feed_id,
            "org_id": org_id,
            "source_type": "self_duplicate",
            "source_platform": "killcont:duplicate-registration",
            "source_url": None,
            "source_author": None,
            "source_region": "Internal",
            "caption": (
                f"Duplicate registration of '{best_match['title']}' as {new_asset['id']}"
            ),
            "content_type": "image",
            "media_path": new_asset.get("primary_path"),
            "preview_path": new_asset.get("preview_path"),
            "phash": new_phash,
        }
    )
    await publish("feed.ingested", {"feed_item_id": feed_id})

    feed_full = repos.get_feed_item(feed_id) or {}
    summary = await _score_pair(
        # The "official" side of the case is the older (already-protected)
        # asset; the new asset's pixels live in the synthetic feed.
        asset=best_match,
        feed=feed_full,
        score=best_score,
        promoted_so_far=0,
        synthetic=True,
    )
    summary["kind"] = "duplicate"

    # Bundle E: a duplicate-registration is a workflow event, not piracy.
    # Force severity to 'monitor' regardless of the score-derived value so
    # the operator queue treats this differently from a real repost.
    if summary.get("incident_id"):
        repos.update_incident_severity(summary["incident_id"], "monitor")
        summary["severity"] = "monitor"

    return summary
