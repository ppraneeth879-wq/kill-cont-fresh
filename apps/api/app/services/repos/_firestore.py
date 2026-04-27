"""Firestore metadata adapter — public-profile implementation.

Mirrors the SQLite adapter's response shapes so the FE never sees a
backend swap. Initialization reuses the shared ``firebase-admin`` app from
``app.services.authn`` so we do not initialize the SDK twice.

Collection layout (per ``docs/architecture.md`` lines 276–290, denormalized
where it removes a join from a hot read path):

* ``users/{user_id}``
* ``assets/{asset_id}`` — fields include ``org_id``, ``phash`` for the matcher.
* ``feedItems/{feed_item_id}``
* ``matchCandidates/{candidate_id}`` — keyed by ``feed_item_id`` / ``asset_id``.
* ``incidents/{incident_id}`` — denormalizes ``asset_title``,
  ``source_platform``, ``source_region``, plus a numeric ``severity_rank``
  so list reads are a single composite-index query.
* ``actions/{action_id}`` — keyed by ``incident_id``.

Composite indexes the read path needs are tracked in
``infra/google-cloud/firestore.indexes.json``.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import get_settings

from ._common import (
    incident_to_summary,
    new_action_id,
    new_asset_id,  # noqa: F401  (re-exported via package __init__)
    new_candidate_id,  # noqa: F401
    new_feed_id,  # noqa: F401
    new_incident_id,  # noqa: F401
)


# ---------- Client init ----------

_SEVERITY_RANK = {"strike": 0, "monitor": 1, "verified": 2}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_admin_app():
    """Reuse the firebase-admin app initialized in ``authn`` (or initialize)."""

    import firebase_admin
    from firebase_admin import credentials

    try:
        return firebase_admin.get_app()
    except ValueError:
        settings = get_settings()
        if settings.firebase_credentials_path:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            return firebase_admin.initialize_app(
                cred,
                {"projectId": settings.firebase_project_id or settings.gcp_project_id},
            )
        return firebase_admin.initialize_app(
            options={"projectId": settings.firebase_project_id or settings.gcp_project_id},
        )


def _client():
    """Return a Firestore client tied to the shared firebase-admin app."""

    from firebase_admin import firestore  # type: ignore[attr-defined]

    return firestore.client(_ensure_admin_app())


# ---------- Helpers ----------

def _doc_to_dict(snap) -> dict:
    if not snap.exists:
        return {}
    data = snap.to_dict() or {}
    data["id"] = snap.id
    return data


def _norm_incident_doc(data: dict) -> dict:
    """Promote `id` (the doc id) and ensure all expected keys exist."""

    return {
        "id": data.get("id"),
        "org_id": data.get("org_id"),
        "asset_id": data.get("asset_id"),
        "feed_item_id": data.get("feed_item_id"),
        "title": data.get("title") or "",
        "severity": data.get("severity") or "monitor",
        "triage_label": data.get("triage_label") or data.get("severity") or "monitor",
        "trust_score": float(data.get("trust_score") or 0.0),
        "spread_score": float(data.get("spread_score") or 0.0),
        "operator_status": data.get("operator_status") or "new",
        "reason_short": data.get("reason_short"),
        "reason_detailed": data.get("reason_detailed"),
        "operator_copy": data.get("operator_copy"),
        "map_region": data.get("map_region"),
        "map_lat": data.get("map_lat"),
        "map_lng": data.get("map_lng"),
        "asset_title": data.get("asset_title") or "",
        "source_platform": data.get("source_platform"),
        "source_region": data.get("source_region"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }


def _severity_sort_key(row: dict) -> tuple:
    rank = _SEVERITY_RANK.get((row.get("severity") or "").lower(), 9)
    created = row.get("created_at") or ""
    # Reverse the timestamp by negating its hash isn't reliable; instead, sort
    # by (rank ASC, created DESC) using a tuple of (rank, neg_iso_timestamp).
    return (rank, _neg_iso(created))


def _neg_iso(s: str) -> str:
    """Return a string that sorts inversely to an ISO timestamp."""

    if not s:
        return chr(0x10FFFF)  # missing timestamps last
    # Map each character to its complement so DESC sort emerges from default ASC.
    return "".join(chr(0x10FFFF - ord(c)) for c in s)


# ---------- Read surface ----------

def list_incidents(
    org_id: str,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    db = _client()
    query = db.collection("incidents").where("org_id", "==", org_id)
    if status:
        query = query.where("operator_status", "==", status)
    if severity:
        query = query.where("severity", "==", severity)
    # Fetch a generous window then sort/trim in-process: Firestore cannot order
    # by the custom severity rank without a composite index on every filter.
    # ``limit * 4`` is a safe upper bound for hackathon-scale incident counts.
    docs = list(query.limit(max(limit * 4, 200)).stream())
    rows = [_norm_incident_doc(_doc_to_dict(d)) for d in docs]
    rows.sort(key=_severity_sort_key)
    return [incident_to_summary(r) for r in rows[:limit]]


def get_incident_detail(incident_id: str) -> Optional[dict]:
    db = _client()
    inc_snap = db.collection("incidents").document(incident_id).get()
    if not inc_snap.exists:
        return None
    incident = _norm_incident_doc(_doc_to_dict(inc_snap))

    asset = {}
    if incident.get("asset_id"):
        asset_snap = db.collection("assets").document(incident["asset_id"]).get()
        asset = _doc_to_dict(asset_snap)

    feed = {}
    if incident.get("feed_item_id"):
        feed_snap = db.collection("feedItems").document(incident["feed_item_id"]).get()
        feed = _doc_to_dict(feed_snap)

    candidates: list[dict] = []
    if incident.get("feed_item_id"):
        cand_docs = (
            db.collection("matchCandidates")
            .where("feed_item_id", "==", incident["feed_item_id"])
            .stream()
        )
        candidates = [_doc_to_dict(d) for d in cand_docs]
        candidates.sort(key=lambda r: -float(r.get("similarity_score") or 0.0))

    action_docs = (
        db.collection("actions").where("incident_id", "==", incident_id).stream()
    )
    actions = [_doc_to_dict(d) for d in action_docs]
    actions.sort(key=lambda r: r.get("created_at") or "", reverse=True)

    return {
        "id": incident["id"],
        "title": incident["title"],
        "severity": incident["severity"],
        "triage_label": incident["triage_label"],
        "trust_score": incident["trust_score"],
        "spread_score": incident["spread_score"],
        "operator_status": incident["operator_status"],
        "reason_short": incident.get("reason_short"),
        "reason_detailed": incident.get("reason_detailed"),
        "operator_copy": incident.get("operator_copy"),
        "map_region": incident.get("map_region"),
        "map_lat": incident.get("map_lat"),
        "map_lng": incident.get("map_lng"),
        "created_at": incident["created_at"],
        "updated_at": incident.get("updated_at"),
        "asset": {
            "id": asset.get("id"),
            "title": asset.get("title"),
            "asset_type": asset.get("asset_type"),
            "event_name": asset.get("event_name"),
            "provenance_status": asset.get("provenance_status"),
            "primary_path": asset.get("primary_path"),
            "preview_path": asset.get("preview_path"),
        },
        "feed_item": feed,
        "candidates": candidates,
        "actions": actions,
    }


def list_assets(org_id: str) -> list[dict]:
    db = _client()
    asset_docs = list(db.collection("assets").where("org_id", "==", org_id).stream())
    rows = [_doc_to_dict(d) for d in asset_docs]
    rows.sort(key=lambda r: r.get("created_at") or "", reverse=True)

    incidents_per_asset: dict[str, int] = {}
    inc_docs = db.collection("incidents").where("org_id", "==", org_id).stream()
    for d in inc_docs:
        data = d.to_dict() or {}
        aid = data.get("asset_id")
        if aid:
            incidents_per_asset[aid] = incidents_per_asset.get(aid, 0) + 1

    return [
        {
            "asset_id": r.get("id"),
            "title": r.get("title") or "",
            "asset_type": r.get("asset_type") or "image",
            "event_name": r.get("event_name") or "",
            "status": r.get("status") or "processing",
            "provenance_status": r.get("provenance_status") or "unknown",
            "incident_count": incidents_per_asset.get(r.get("id"), 0),
            "preview_path": r.get("preview_path"),
        }
        for r in rows
    ]


def get_asset_detail(asset_id: str) -> Optional[dict]:
    db = _client()
    snap = db.collection("assets").document(asset_id).get()
    if not snap.exists:
        return None
    row = _doc_to_dict(snap)
    inc_count = sum(
        1
        for _ in db.collection("incidents").where("asset_id", "==", asset_id).stream()
    )
    return {
        "id": row.get("id"),
        "title": row.get("title") or "",
        "asset_type": row.get("asset_type") or "image",
        "event_name": row.get("event_name"),
        "sport": row.get("sport"),
        "rights_owner": row.get("rights_owner"),
        "description": row.get("description"),
        "status": row.get("status") or "processing",
        "provenance_status": row.get("provenance_status") or "unknown",
        "primary_path": row.get("primary_path"),
        "preview_path": row.get("preview_path"),
        "phash": row.get("phash"),
        "created_at": row.get("created_at"),
        "incident_count": inc_count,
    }


def list_feed_items(org_id: str, limit: int = 50) -> list[dict]:
    db = _client()
    docs = list(
        db.collection("feedItems")
        .where("org_id", "==", org_id)
        .limit(max(limit * 2, 100))
        .stream()
    )
    rows = [_doc_to_dict(d) for d in docs]
    rows.sort(key=lambda r: r.get("ingest_time") or "", reverse=True)
    return rows[:limit]


def get_feed_item(feed_item_id: str) -> Optional[dict]:
    db = _client()
    snap = db.collection("feedItems").document(feed_item_id).get()
    if not snap.exists:
        return None
    return _doc_to_dict(snap)


def count_incidents_by_status(org_id: str) -> dict[str, int]:
    db = _client()
    out: dict[str, int] = {}
    for d in db.collection("incidents").where("org_id", "==", org_id).stream():
        data = d.to_dict() or {}
        key = data.get("operator_status") or "new"
        out[key] = out.get(key, 0) + 1
    return out


def count_assets_by_type(org_id: str) -> dict[str, int]:
    db = _client()
    out: dict[str, int] = {}
    for d in db.collection("assets").where("org_id", "==", org_id).stream():
        data = d.to_dict() or {}
        key = data.get("asset_type") or "image"
        out[key] = out.get(key, 0) + 1
    return out


# ---------- Write surface ----------

def insert_action(
    incident_id: str,
    by_user_id: str,
    action_type: str,
    notes: Optional[str],
) -> dict:
    db = _client()
    action_id = new_action_id()
    payload: dict[str, Any] = {
        "id": action_id,
        "incident_id": incident_id,
        "by_user_id": by_user_id,
        "type": action_type,
        "notes": notes,
        "created_at": _now_iso(),
    }
    db.collection("actions").document(action_id).set(payload)
    return payload


def update_incident_status(incident_id: str, status: str) -> Optional[dict]:
    db = _client()
    ref = db.collection("incidents").document(incident_id)
    snap = ref.get()
    if not snap.exists:
        return None
    ref.update({"operator_status": status, "updated_at": _now_iso()})
    return _doc_to_dict(ref.get())


def update_incident_severity(incident_id: str, severity: str) -> Optional[dict]:
    """Bundle E: override severity + triage_label post-insert."""
    db = _client()
    ref = db.collection("incidents").document(incident_id)
    snap = ref.get()
    if not snap.exists:
        return None
    ref.update(
        {
            "severity": severity,
            "triage_label": severity,
            "updated_at": _now_iso(),
        }
    )
    return _doc_to_dict(ref.get())


def upsert_user(
    user_id: str,
    email: str,
    display_name: str,
    org_id: str,
    role: Optional[str] = None,
) -> dict:
    """Bundle F: ``role`` only applies to new inserts; existing users keep
    their current role across sign-ins."""
    db = _client()
    ref = db.collection("users").document(user_id)
    snap = ref.get()
    if snap.exists:
        ref.update({"email": email, "display_name": display_name, "org_id": org_id})
    else:
        ref.set(
            {
                "id": user_id,
                "email": email,
                "display_name": display_name,
                "org_id": org_id,
                "role": role or "admin",
                "created_at": _now_iso(),
            }
        )
    return _doc_to_dict(ref.get())


def get_user(user_id: str) -> Optional[dict]:
    db = _client()
    snap = db.collection("users").document(user_id).get()
    if not snap.exists:
        return None
    return _doc_to_dict(snap)


def get_all_assets_with_phash(org_id: str) -> list[dict]:
    db = _client()
    out: list[dict] = []
    for d in db.collection("assets").where("org_id", "==", org_id).stream():
        data = d.to_dict() or {}
        if not data.get("phash"):
            continue
        out.append(
            {
                "id": d.id,
                "title": data.get("title"),
                "asset_type": data.get("asset_type"),
                "provenance_status": data.get("provenance_status"),
                "phash": data.get("phash"),
            }
        )
    return out


# ---------- Write surface for seeder + simulate-incident ----------

def insert_asset(payload: dict) -> None:
    db = _client()
    doc: dict[str, Any] = {
        "id": payload["id"],
        "org_id": payload["org_id"],
        "title": payload["title"],
        "asset_type": payload["asset_type"],
        "event_name": payload.get("event_name"),
        "sport": payload.get("sport"),
        "rights_owner": payload.get("rights_owner"),
        "description": payload.get("description"),
        "status": payload.get("status") or "watching",
        "provenance_status": payload.get("provenance_status") or "unknown",
        "primary_path": payload.get("primary_path"),
        "preview_path": payload.get("preview_path"),
        "phash": payload.get("phash"),
        "created_at": _now_iso(),
    }
    db.collection("assets").document(payload["id"]).set(doc)


def insert_feed_item(payload: dict) -> None:
    db = _client()
    doc: dict[str, Any] = {
        "id": payload["id"],
        "org_id": payload["org_id"],
        "source_type": payload.get("source_type") or "simulated",
        "source_platform": payload.get("source_platform"),
        "source_url": payload.get("source_url"),
        "source_author": payload.get("source_author"),
        "source_region": payload.get("source_region"),
        "caption": payload.get("caption"),
        "content_type": payload.get("content_type") or "image",
        "media_path": payload.get("media_path"),
        "preview_path": payload.get("preview_path"),
        "phash": payload.get("phash"),
        "ingest_time": _now_iso(),
    }
    db.collection("feedItems").document(payload["id"]).set(doc)


def insert_match_candidate(payload: dict) -> None:
    db = _client()
    doc: dict[str, Any] = {
        "id": payload["id"],
        "feed_item_id": payload["feed_item_id"],
        "asset_id": payload["asset_id"],
        "similarity_score": float(payload["similarity_score"]),
        "hamming_distance": int(payload["hamming_distance"]),
        "confidence_band": payload["confidence_band"],
        "provenance_gap": int(payload.get("provenance_gap") or 0),
        "created_at": _now_iso(),
    }
    db.collection("matchCandidates").document(payload["id"]).set(doc)


def insert_incident(payload: dict) -> None:
    """Insert an incident with denormalized fields for fast list reads."""

    db = _client()
    # Denormalize asset/feed metadata so list_incidents avoids two extra reads.
    asset_title = payload.get("asset_title")
    source_platform = payload.get("source_platform")
    source_region = payload.get("source_region")

    if not asset_title and payload.get("asset_id"):
        asset_snap = db.collection("assets").document(payload["asset_id"]).get()
        if asset_snap.exists:
            asset_title = (asset_snap.to_dict() or {}).get("title") or ""

    if (not source_platform or not source_region) and payload.get("feed_item_id"):
        feed_snap = db.collection("feedItems").document(payload["feed_item_id"]).get()
        if feed_snap.exists:
            feed_data = feed_snap.to_dict() or {}
            source_platform = source_platform or feed_data.get("source_platform")
            source_region = source_region or feed_data.get("source_region")

    severity = payload["severity"]
    doc: dict[str, Any] = {
        "id": payload["id"],
        "org_id": payload["org_id"],
        "asset_id": payload["asset_id"],
        "feed_item_id": payload["feed_item_id"],
        "title": payload["title"],
        "severity": severity,
        "severity_rank": _SEVERITY_RANK.get(severity, 9),
        "triage_label": payload.get("triage_label") or severity,
        "trust_score": float(payload.get("trust_score") or 0.0),
        "spread_score": float(payload.get("spread_score") or 0.0),
        "operator_status": payload.get("operator_status") or "new",
        "reason_short": payload.get("reason_short"),
        "reason_detailed": payload.get("reason_detailed"),
        "operator_copy": payload.get("operator_copy"),
        "map_region": payload.get("map_region"),
        "map_lat": payload.get("map_lat"),
        "map_lng": payload.get("map_lng"),
        "asset_title": asset_title or "",
        "source_platform": source_platform,
        "source_region": source_region,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    db.collection("incidents").document(payload["id"]).set(doc)
