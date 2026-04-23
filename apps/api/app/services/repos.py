"""Thin query helpers shared across route handlers.

Not a full ORM — just the couple of joined reads that would otherwise be
duplicated in 3+ places (incident summary row + dashboard overview + asset
detail). Everything returns plain dicts from the ``dict_factory`` on the
connection.
"""

from __future__ import annotations

import secrets
import string
from typing import Optional

from app.services.db import get_conn


# ---------- ID helpers ----------

def _rand_suffix(n: int = 4) -> str:
    alphabet = string.digits
    return "".join(secrets.choice(alphabet) for _ in range(n))


def new_asset_id() -> str:
    return f"AST-{_rand_suffix(4)}"


def new_feed_id() -> str:
    return f"FEED-{_rand_suffix(5)}"


def new_incident_id() -> str:
    return f"INC-{_rand_suffix(5)}"


def new_candidate_id() -> str:
    return f"CAND-{_rand_suffix(6)}"


def new_action_id() -> str:
    return f"ACT-{_rand_suffix(6)}"


# ---------- Formatters ----------

def _pct(score: float) -> str:
    return f"{score * 100:.1f}%"


def _spread_label(score: float) -> str:
    if score >= 0.66:
        return "high"
    if score >= 0.33:
        return "moderate"
    return "low"


def incident_to_summary(row: dict) -> dict:
    """Shape a joined incident row into the FE-facing summary format.

    Expected keys on ``row``: everything on ``incidents`` plus ``asset_title``,
    ``source_platform``, ``source_region``, ``trust_score``.
    """

    return {
        "incident_id": row["id"],
        "title": row["title"],
        "severity": row["severity"],
        "platform": row.get("source_platform") or "unknown",
        "matched_asset": row.get("asset_title") or "",
        "confidence": _pct(row.get("trust_score") or 0.0),
        "spread": _spread_label(row.get("spread_score") or 0.0),
        "region": row.get("map_region") or row.get("source_region") or "",
        "summary": row.get("reason_short") or "",
        "operator_status": row.get("operator_status") or "new",
        "asset_id": row.get("asset_id"),
        "feed_item_id": row.get("feed_item_id"),
        "created_at": row.get("created_at"),
    }


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
        "created_at": incident["created_at"],
        "updated_at": incident["updated_at"],
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
