"""One-off SQLite -> Firestore migrator.

Reads the local-profile SQLite database (``apps/api/var/app.db``) and writes
the same rows into Firestore using the public-profile adapter. Intended to
seed the cloud project once with the demo dataset; *not* a continuous sync.

Usage (from repo root)::

    set RUNTIME_PROFILE=public
    set METADATA_BACKEND=firestore
    set FIREBASE_PROJECT_ID=killcont-demo
    set FIREBASE_CREDENTIALS_PATH=path/to/service-account.json
    python scripts/migrate_to_firestore.py

The script imports the same adapter the API uses, so any schema mismatch
shows up immediately and is fixed in one place.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make ``apps/api`` importable so we can reuse the adapter package.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))


def _ensure_public_profile():
    os.environ.setdefault("RUNTIME_PROFILE", "public")
    os.environ.setdefault("METADATA_BACKEND", "firestore")


def main() -> int:
    _ensure_public_profile()

    # Import after env is set so the dispatchers pick up the right backend.
    from app.services.repos import _firestore as fs_repo  # type: ignore
    from app.services.repos import _sqlite as sqlite_repo  # type: ignore

    # Read everything from SQLite directly (uses local profile config)
    # by temporarily flipping the dispatcher's source. We reach into
    # ``_sqlite`` regardless of METADATA_BACKEND env because we just need
    # the read helpers.
    from app.services.db import get_conn

    org_ids: set[str] = set()

    with get_conn() as conn:
        users = list(conn.execute("SELECT * FROM users").fetchall())
        assets = list(conn.execute("SELECT * FROM assets").fetchall())
        feed_items = list(conn.execute("SELECT * FROM feed_items").fetchall())
        candidates = list(conn.execute("SELECT * FROM match_candidates").fetchall())
        incidents = list(conn.execute("SELECT * FROM incidents").fetchall())
        actions = list(conn.execute("SELECT * FROM actions").fetchall())

    print(
        f"sqlite snapshot: users={len(users)} assets={len(assets)} "
        f"feed_items={len(feed_items)} candidates={len(candidates)} "
        f"incidents={len(incidents)} actions={len(actions)}"
    )

    for u in users:
        fs_repo.upsert_user(u["id"], u["email"], u["display_name"], u["org_id"])
        org_ids.add(u["org_id"])

    for a in assets:
        fs_repo.insert_asset(dict(a))
        org_ids.add(a["org_id"])

    for f in feed_items:
        fs_repo.insert_feed_item(dict(f))
        org_ids.add(f["org_id"])

    for c in candidates:
        fs_repo.insert_match_candidate(dict(c))

    for i in incidents:
        # Pull the join values so the denormalized incident doc is correct.
        payload = dict(i)
        with get_conn() as conn:
            asset_row = conn.execute(
                "SELECT title FROM assets WHERE id = ?", (payload["asset_id"],)
            ).fetchone()
            feed_row = conn.execute(
                "SELECT source_platform, source_region FROM feed_items WHERE id = ?",
                (payload["feed_item_id"],),
            ).fetchone()
        if asset_row:
            payload["asset_title"] = asset_row["title"]
        if feed_row:
            payload["source_platform"] = feed_row["source_platform"]
            payload["source_region"] = feed_row["source_region"]
        fs_repo.insert_incident(payload)

    for ac in actions:
        # ``insert_action`` generates a new id, so use a direct write to keep
        # the original id from SQLite for reproducibility.
        from datetime import datetime, timezone

        client = fs_repo._client()
        client.collection("actions").document(ac["id"]).set(
            {
                "id": ac["id"],
                "incident_id": ac["incident_id"],
                "by_user_id": ac["by_user_id"],
                "type": ac["type"],
                "notes": ac["notes"],
                "created_at": ac["created_at"]
                or datetime.now(timezone.utc).isoformat(),
            }
        )

    print(f"migration done. org_ids touched: {sorted(org_ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
