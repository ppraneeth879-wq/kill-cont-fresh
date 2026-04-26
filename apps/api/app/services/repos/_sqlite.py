"""SQLite metadata adapter — the local-profile implementation.

Verbatim port of the original ``app/services/repos.py`` query helpers.
Route handlers reach these through the package-level dispatcher in
``app/services/repos/__init__.py`` so the call surface stays
``repos.list_incidents(...)``.
"""

from __future__ import annotations

from typing import Optional

from app.services.db import get_conn

from ._common import new_action_id, incident_to_summary


# ---------- Query helpers ----------

INCIDENT_JOIN_SELECT = """
SELECT incidents.*,
       assets.title AS asset_title,
       feed_items.source_platform AS source_platform,
       feed_items.source_region AS source_region
  FROM incidents
  LEFT JOIN assets      ON assets.id       = incidents.asset_id
  LEFT JOIN feed_items  ON feed_items.id   = incidents.feed_item_id
"""


def list_incidents(
    org_id: str,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    clauses = ["incidents.org_id = ?"]
    params: list = [org_id]
    if status:
        clauses.append("incidents.operator_status = ?")
        params.append(status)
    if severity:
        clauses.append("incidents.severity = ?")
        params.append(severity)
    where = " WHERE " + " AND ".join(clauses)
    sql = (
        INCIDENT_JOIN_SELECT
        + where
        + " ORDER BY CASE incidents.severity "
          "  WHEN 'strike' THEN 0 WHEN 'monitor' THEN 1 ELSE 2 END, "
          "  datetime(incidents.created_at) DESC "
          "LIMIT ?"
    )
    params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [incident_to_summary(r) for r in rows]


def get_incident_detail(incident_id: str) -> Optional[dict]:
    with get_conn() as conn:
        incident = conn.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        ).fetchone()
        if not incident:
            return None
        asset = conn.execute(
            "SELECT id, title, asset_type, event_name, provenance_status, "
            "       primary_path, preview_path "
            "  FROM assets WHERE id = ?",
            (incident["asset_id"],),
        ).fetchone() or {}
        feed = conn.execute(
            "SELECT * FROM feed_items WHERE id = ?",
            (incident["feed_item_id"],),
        ).fetchone() or {}
        candidates = conn.execute(
            "SELECT * FROM match_candidates WHERE feed_item_id = ? "
            "ORDER BY similarity_score DESC",
            (incident["feed_item_id"],),
        ).fetchall()
        actions = conn.execute(
            "SELECT * FROM actions WHERE incident_id = ? ORDER BY datetime(created_at) DESC",
            (incident_id,),
        ).fetchall()

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
        "updated_at": incident["updated_at"],
        "triage_source": incident.get("triage_source"),
        "triage_model": incident.get("triage_model"),
        "triage_latency_ms": incident.get("triage_latency_ms"),
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
    sql = (
        "SELECT assets.*, "
        "   (SELECT COUNT(*) FROM incidents "
        "     WHERE incidents.asset_id = assets.id) AS incident_count "
        "FROM assets WHERE assets.org_id = ? "
        "ORDER BY datetime(assets.created_at) DESC"
    )
    with get_conn() as conn:
        rows = conn.execute(sql, (org_id,)).fetchall()
    return [
        {
            "asset_id": r["id"],
            "title": r["title"],
            "asset_type": r["asset_type"],
            "event_name": r.get("event_name") or "",
            "status": r["status"],
            "provenance_status": r["provenance_status"],
            "incident_count": r["incident_count"],
            "preview_path": r.get("preview_path"),
        }
        for r in rows
    ]


def get_asset_detail(asset_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT *, (SELECT COUNT(*) FROM incidents WHERE asset_id = ?) AS incident_count "
            "  FROM assets WHERE id = ?",
            (asset_id, asset_id),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "asset_type": row["asset_type"],
        "event_name": row.get("event_name"),
        "sport": row.get("sport"),
        "rights_owner": row.get("rights_owner"),
        "description": row.get("description"),
        "status": row["status"],
        "provenance_status": row["provenance_status"],
        "primary_path": row.get("primary_path"),
        "preview_path": row.get("preview_path"),
        "phash": row.get("phash"),
        "created_at": row["created_at"],
        "incident_count": row["incident_count"],
    }


def list_feed_items(org_id: str, limit: int = 50) -> list[dict]:
    sql = (
        "SELECT * FROM feed_items WHERE org_id = ? "
        "ORDER BY datetime(ingest_time) DESC LIMIT ?"
    )
    with get_conn() as conn:
        return conn.execute(sql, (org_id, limit)).fetchall()


def get_feed_item(feed_item_id: str) -> Optional[dict]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM feed_items WHERE id = ?", (feed_item_id,)
        ).fetchone()


def count_incidents_by_status(org_id: str) -> dict[str, int]:
    sql = (
        "SELECT operator_status, COUNT(*) AS n FROM incidents "
        "  WHERE org_id = ? GROUP BY operator_status"
    )
    with get_conn() as conn:
        rows = conn.execute(sql, (org_id,)).fetchall()
    return {r["operator_status"]: r["n"] for r in rows}


def count_assets_by_type(org_id: str) -> dict[str, int]:
    sql = (
        "SELECT asset_type, COUNT(*) AS n FROM assets "
        "  WHERE org_id = ? GROUP BY asset_type"
    )
    with get_conn() as conn:
        rows = conn.execute(sql, (org_id,)).fetchall()
    return {r["asset_type"]: r["n"] for r in rows}


def insert_action(incident_id: str, by_user_id: str, action_type: str, notes: Optional[str]) -> dict:
    action_id = new_action_id()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO actions (id, incident_id, by_user_id, type, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (action_id, incident_id, by_user_id, action_type, notes),
        )
        row = conn.execute("SELECT * FROM actions WHERE id = ?", (action_id,)).fetchone()
    return row


def update_incident_status(incident_id: str, status: str) -> Optional[dict]:
    with get_conn() as conn:
        conn.execute(
            "UPDATE incidents SET operator_status = ?, updated_at = datetime('now') "
            "WHERE id = ?",
            (status, incident_id),
        )
        row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return row


def upsert_user(user_id: str, email: str, display_name: str, org_id: str) -> dict:
    with get_conn() as conn:
        existing = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE users SET email = ?, display_name = ? WHERE id = ?",
                (email, display_name, user_id),
            )
        else:
            conn.execute(
                "INSERT INTO users (id, email, display_name, org_id) VALUES (?, ?, ?, ?)",
                (user_id, email, display_name, org_id),
            )
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return row


def get_user(user_id: str) -> Optional[dict]:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_all_assets_with_phash(org_id: str) -> list[dict]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, title, asset_type, provenance_status, phash "
            "  FROM assets WHERE org_id = ? AND phash IS NOT NULL",
            (org_id,),
        ).fetchall()


# ---------- Write surface for seeder + simulate-incident ----------

def insert_asset(payload: dict) -> None:
    """Insert a fully-formed asset row. Caller fills every column.

    Expected keys: id, org_id, title, asset_type, event_name, sport,
    rights_owner, description, status, provenance_status, primary_path,
    preview_path, phash.
    """

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO assets (id, org_id, title, asset_type, event_name, sport, "
            "   rights_owner, description, status, provenance_status, primary_path, "
            "   preview_path, phash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                payload["id"],
                payload["org_id"],
                payload["title"],
                payload["asset_type"],
                payload.get("event_name"),
                payload.get("sport"),
                payload.get("rights_owner"),
                payload.get("description"),
                payload.get("status") or "watching",
                payload.get("provenance_status") or "unknown",
                payload.get("primary_path"),
                payload.get("preview_path"),
                payload.get("phash"),
            ),
        )


def insert_feed_item(payload: dict) -> None:
    """Insert a feed-item row.

    Expected keys: id, org_id, source_type, source_platform, source_url,
    source_author, source_region, caption, content_type, media_path,
    preview_path, phash.
    """

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO feed_items (id, org_id, source_type, source_platform, source_url, "
            "   source_author, source_region, caption, content_type, media_path, "
            "   preview_path, phash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                payload["id"],
                payload["org_id"],
                payload.get("source_type") or "simulated",
                payload.get("source_platform"),
                payload.get("source_url"),
                payload.get("source_author"),
                payload.get("source_region"),
                payload.get("caption"),
                payload.get("content_type") or "image",
                payload.get("media_path"),
                payload.get("preview_path"),
                payload.get("phash"),
            ),
        )


def insert_match_candidate(payload: dict) -> None:
    """Insert a match-candidate row.

    Expected keys: id, feed_item_id, asset_id, similarity_score,
    hamming_distance, confidence_band, provenance_gap.
    """

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO match_candidates (id, feed_item_id, asset_id, similarity_score, "
            "   hamming_distance, confidence_band, provenance_gap) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                payload["id"],
                payload["feed_item_id"],
                payload["asset_id"],
                payload["similarity_score"],
                payload["hamming_distance"],
                payload["confidence_band"],
                int(payload.get("provenance_gap") or 0),
            ),
        )


def insert_incident(payload: dict) -> None:
    """Insert a fully-formed incident row.

    Expected keys: id, org_id, asset_id, feed_item_id, title, severity,
    triage_label, trust_score, spread_score, operator_status (default new),
    reason_short, reason_detailed, operator_copy, map_region, map_lat,
    map_lng. Denormalized fields (asset_title, source_platform,
    source_region) are stored in the SQLite schema only via the JOIN at
    read time — they are accepted in payload but ignored here.
    """

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO incidents (id, org_id, asset_id, feed_item_id, title, severity, "
            "   triage_label, trust_score, spread_score, operator_status, reason_short, "
            "   reason_detailed, operator_copy, map_region, map_lat, map_lng, "
            "   triage_source, triage_model, triage_latency_ms) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                payload["id"],
                payload["org_id"],
                payload["asset_id"],
                payload["feed_item_id"],
                payload["title"],
                payload["severity"],
                payload.get("triage_label") or payload["severity"],
                float(payload.get("trust_score") or 0.0),
                float(payload.get("spread_score") or 0.0),
                payload.get("operator_status") or "new",
                payload.get("reason_short"),
                payload.get("reason_detailed"),
                payload.get("operator_copy"),
                payload.get("map_region"),
                payload.get("map_lat"),
                payload.get("map_lng"),
                payload.get("triage_source"),
                payload.get("triage_model"),
                payload.get("triage_latency_ms"),
            ),
        )
