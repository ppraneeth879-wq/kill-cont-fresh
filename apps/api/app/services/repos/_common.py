"""Backend-agnostic helpers shared by every repos adapter.

ID generation and incident-to-summary formatting do not touch persistence,
so both the SQLite and Firestore implementations re-export from here.
"""

from __future__ import annotations

import secrets
import string


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
        "map_lat": row.get("map_lat"),
        "map_lng": row.get("map_lng"),
    }
