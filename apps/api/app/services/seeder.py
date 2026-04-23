"""Demo seeder: plants a ready-to-demo dataset into SQLite.

Generates placeholder image assets (or copies real files from
``assets/demo-media/championship-final/`` if present), computes pHashes,
writes the full 3-asset / 8-feed / 4-incident scenario. Designed to run in
well under a second.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.services import repos, storage
from app.services.db import get_conn, reset_db
from app.services.similarity import (
    compute_phash,
    confidence_band,
    derive_severity,
    hamming_distance,
    similarity_score,
)
from app.services.triage import CANNED_BY_SEVERITY


# --- Real media (optional override) -----------------------------------------

# If the operator drops real images into this folder they will be used
# verbatim; otherwise we synthesise placeholder JPEGs.
DEMO_MEDIA_ROOT = Path(__file__).resolve().parents[3] / "assets" / "demo-media" / "championship-final"

ASSET_SOURCES = [
    {
        "id": "AST-201",
        "title": "Final whistle broadcast clip",
        "asset_type": "video",
        "event_name": "Championship Night",
        "sport": "Football",
        "rights_owner": "KillCont Sports",
        "description": "Broadcast cut of the final whistle and trophy handoff.",
        "provenance_status": "verified",
        "file": "official-highlight.jpg",
        "color": (52, 91, 196),
    },
    {
        "id": "AST-188",
        "title": "Official trophy lift image",
        "asset_type": "image",
        "event_name": "Championship Night",
        "sport": "Football",
        "rights_owner": "KillCont Sports",
        "description": "Photographer's official trophy-lift frame.",
        "provenance_status": "present",
        "file": "trophy-lift.jpg",
        "color": (196, 139, 44),
    },
    {
        "id": "AST-172",
        "title": "Live tunnel cam watch",
        "asset_type": "live_watch",
        "event_name": "Semifinal Stream",
        "sport": "Football",
        "rights_owner": "KillCont Sports",
        "description": "Live tunnel camera feed tracked for relays.",
        "provenance_status": "pending",
        "file": "tunnel-cam.jpg",
        "color": (44, 136, 120),
    },
]

# Each feed item references one of the assets above by index. ``mutate`` makes
# it a derived (repost) image; otherwise we keep the pHash identical so the
# scenario always shows a clean strike.
FEED_SOURCES = [
    {
        "platform": "piracy-mirror",
        "region": "Singapore -> London -> Dubai",
        "author": "@mirror-feed",
        "caption": "Final whistle full clip",
        "asset_idx": 0,
        "mutate": True,
        "severity": "strike",
    },
    {
        "platform": "reddit",
        "region": "Bengaluru -> Berlin",
        "author": "u/sideline",
        "caption": "Edited trophy-lift share",
        "asset_idx": 1,
        "mutate": True,
        "severity": "monitor",
    },
    {
        "platform": "fan-clip-feed",
        "region": "Mumbai",
        "author": "@fanclip",
        "caption": "Celebration tunnel moment",
        "asset_idx": 2,
        "mutate": True,
        "severity": "verified",
    },
    {
        "platform": "youtube",
        "region": "Jakarta -> Manila",
        "author": "@broadcast-copy",
        "caption": "Rebroadcast highlight",
        "asset_idx": 0,
        "mutate": True,
        "severity": "strike",
    },
    {
        "platform": "piracy-mirror",
        "region": "Istanbul",
        "author": "@unknown",
        "caption": "Full-match compilation",
        "asset_idx": 0,
        "mutate": True,
        "severity": "monitor",
    },
    {
        "platform": "reddit",
        "region": "Toronto",
        "author": "u/fanpov",
        "caption": "Cropped trophy moment",
        "asset_idx": 1,
        "mutate": True,
        "severity": "monitor",
    },
    {
        "platform": "fan-clip-feed",
        "region": "Sydney",
        "author": "@funnyedits",
        "caption": "Meme from the broadcast",
        "asset_idx": 2,
        "mutate": True,
        "severity": "verified",
    },
    {
        "platform": "live-relay",
        "region": "Dubai",
        "author": "@relay-node-3",
        "caption": "Suspect relay segment",
        "asset_idx": 2,
        "mutate": True,
        "severity": "monitor",
    },
]

# How many of the seeded feed items should be promoted to incidents at seed
# time. Remaining feed items sit on the Monitor page as watched-but-not-yet
# -escalated rows.
INCIDENT_COUNT = 4


# ----------------------------------------------------------------------------

def _copy_or_generate_asset_source(cfg: dict, dest: Path) -> Path:
    src = DEMO_MEDIA_ROOT / cfg["file"]
    if src.exists():
        return storage.copy_file(src, dest)
    return storage.generate_placeholder_image(dest, cfg["color"], cfg["title"])


def _make_feed_media(source_asset_path: Path, feed_cfg: dict, feed_id: str) -> Path:
    target = storage.feed_dir(feed_id) / "media.jpg"
    if feed_cfg["mutate"]:
        out = storage.derive_repost(source_asset_path, target, label=feed_cfg["platform"].upper())
        if out is not None:
            return out
    # Fallback: just copy the asset image.
    return storage.copy_file(source_asset_path, target)


def _spread_score_from_severity(severity: str) -> float:
    return {"strike": 0.82, "monitor": 0.48, "verified": 0.22}.get(severity, 0.35)


def seed_championship_final(org_id: Optional[str] = None) -> dict:
    """Wipe + repopulate the DB with the championship-final scenario.

    Returns counts so the /demo/seed endpoint can echo them back.
    """

    settings = get_settings()
    org = org_id or settings.demo_org_id

    reset_db()

    # Ensure the default user exists.
    repos.upsert_user(
        user_id=settings.demo_default_user_id,
        email="ops@killcont.demo",
        display_name="KillCont Demo Operator",
        org_id=org,
    )

    asset_records: list[dict] = []
    for cfg in ASSET_SOURCES:
        asset_id = cfg["id"]
        asset_folder = storage.asset_dir(asset_id)
        primary = asset_folder / "original.jpg"
        _copy_or_generate_asset_source(cfg, primary)
        preview = asset_folder / "preview.jpg"
        storage.make_preview(primary, preview)
        storage.make_frame_strip(primary, asset_folder / "frames")
        phash = compute_phash(primary)

        with get_conn() as conn:
            conn.execute(
                "INSERT INTO assets (id, org_id, title, asset_type, event_name, sport, "
                "   rights_owner, description, status, provenance_status, primary_path, "
                "   preview_path, phash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'watching', ?, ?, ?, ?)",
                (
                    asset_id,
                    org,
                    cfg["title"],
                    cfg["asset_type"],
                    cfg["event_name"],
                    cfg["sport"],
                    cfg["rights_owner"],
                    cfg["description"],
                    cfg["provenance_status"],
                    storage.relpath(primary),
                    storage.relpath(preview),
                    phash,
                ),
            )
        asset_records.append(
            {
                "id": asset_id,
                "primary_path": primary,
                "phash": phash,
                "provenance_status": cfg["provenance_status"],
                "title": cfg["title"],
            }
        )

    # Build feed items + candidates + incidents.
    feed_count = 0
    incident_count = 0
    for i, feed_cfg in enumerate(FEED_SOURCES):
        asset = asset_records[feed_cfg["asset_idx"]]
        feed_id = f"FEED-{1001 + i}"
        feed_path = _make_feed_media(asset["primary_path"], feed_cfg, feed_id)
        feed_preview = storage.feed_dir(feed_id) / "preview.jpg"
        storage.make_preview(feed_path, feed_preview)
        feed_phash = compute_phash(feed_path)

        with get_conn() as conn:
            conn.execute(
                "INSERT INTO feed_items (id, org_id, source_type, source_platform, source_url, "
                "   source_author, source_region, caption, content_type, media_path, preview_path, phash) "
                "VALUES (?, ?, 'simulated', ?, ?, ?, ?, ?, 'image', ?, ?, ?)",
                (
                    feed_id,
                    org,
                    feed_cfg["platform"],
                    f"https://{feed_cfg['platform']}.example/{feed_id}",
                    feed_cfg["author"],
                    feed_cfg["region"],
                    feed_cfg["caption"],
                    storage.relpath(feed_path),
                    storage.relpath(feed_preview),
                    feed_phash,
                ),
            )
        feed_count += 1

        # Always record a match candidate for this feed item.
        distance = hamming_distance(asset["phash"], feed_phash)
        score = similarity_score(asset["phash"], feed_phash)
        provenance_gap = 1 if asset["provenance_status"] in ("verified", "present") else 0
        cand_id = repos.new_candidate_id()
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO match_candidates (id, feed_item_id, asset_id, similarity_score, "
                "   hamming_distance, confidence_band, provenance_gap) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    cand_id,
                    feed_id,
                    asset["id"],
                    score,
                    distance,
                    confidence_band(score),
                    provenance_gap,
                ),
            )

        # Promote the first N feed items to incidents.
        if i < INCIDENT_COUNT:
            severity = feed_cfg["severity"]
            spread = _spread_score_from_severity(severity)
            reason_short, reason_detailed, operator_copy = CANNED_BY_SEVERITY[severity]
            incident_id = f"INC-{1040 + i}"
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO incidents (id, org_id, asset_id, feed_item_id, title, severity, "
                    "   triage_label, trust_score, spread_score, operator_status, reason_short, "
                    "   reason_detailed, operator_copy, map_region) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?, ?, ?)",
                    (
                        incident_id,
                        org,
                        asset["id"],
                        feed_id,
                        _incident_title(severity, asset["title"]),
                        severity,
                        severity,  # triage_label == severity for MVP
                        score,
                        spread,
                        reason_short,
                        reason_detailed,
                        operator_copy,
                        feed_cfg["region"],
                    ),
                )
            incident_count += 1

    return {
        "org_id": org,
        "assets": len(asset_records),
        "feed_items": feed_count,
        "incidents": incident_count,
    }


def _incident_title(severity: str, asset_title: str) -> str:
    if severity == "strike":
        return f"Unauthorized repost of '{asset_title}' detected"
    if severity == "monitor":
        return f"Edited derivative of '{asset_title}' circulating"
    return f"Fan derivative referencing '{asset_title}'"
