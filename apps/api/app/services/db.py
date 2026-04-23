"""SQLite data layer for KillCont MVP.

One sqlite file at ``var/app.db``. The module exposes a small helper API
(``get_conn``, ``init_db``, ``reset_db``) plus a row factory that returns dicts
so the route handlers can ``jsonable`` the results directly.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import get_settings


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id           TEXT PRIMARY KEY,
  email        TEXT NOT NULL,
  display_name TEXT NOT NULL,
  org_id       TEXT NOT NULL,
  role         TEXT NOT NULL DEFAULT 'admin',
  created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS assets (
  id                  TEXT PRIMARY KEY,
  org_id              TEXT NOT NULL,
  title               TEXT NOT NULL,
  asset_type          TEXT NOT NULL,
  event_name          TEXT,
  sport               TEXT,
  rights_owner        TEXT,
  description         TEXT,
  status              TEXT NOT NULL DEFAULT 'processing',
  provenance_status   TEXT NOT NULL DEFAULT 'unknown',
  primary_path        TEXT,
  preview_path        TEXT,
  phash               TEXT,
  created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS feed_items (
  id              TEXT PRIMARY KEY,
  org_id          TEXT NOT NULL,
  source_type     TEXT NOT NULL,
  source_platform TEXT,
  source_url      TEXT,
  source_author   TEXT,
  source_region   TEXT,
  caption         TEXT,
  content_type    TEXT NOT NULL,
  media_path      TEXT,
  preview_path    TEXT,
  phash           TEXT,
  ingest_time     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS match_candidates (
  id                 TEXT PRIMARY KEY,
  feed_item_id       TEXT NOT NULL REFERENCES feed_items(id) ON DELETE CASCADE,
  asset_id           TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  similarity_score   REAL NOT NULL,
  hamming_distance   INTEGER NOT NULL,
  confidence_band    TEXT NOT NULL,
  provenance_gap     INTEGER NOT NULL DEFAULT 0,
  created_at         TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS incidents (
  id                TEXT PRIMARY KEY,
  org_id            TEXT NOT NULL,
  asset_id          TEXT NOT NULL REFERENCES assets(id),
  feed_item_id      TEXT NOT NULL REFERENCES feed_items(id),
  title             TEXT NOT NULL,
  severity          TEXT NOT NULL,
  triage_label      TEXT NOT NULL,
  trust_score       REAL NOT NULL,
  spread_score      REAL NOT NULL,
  operator_status   TEXT NOT NULL DEFAULT 'new',
  reason_short      TEXT,
  reason_detailed   TEXT,
  operator_copy     TEXT,
  map_lat           REAL,
  map_lng           REAL,
  map_region        TEXT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS actions (
  id            TEXT PRIMARY KEY,
  incident_id   TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  by_user_id    TEXT NOT NULL,
  type          TEXT NOT NULL,
  notes         TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_incidents_severity_created
  ON incidents(severity, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_status
  ON incidents(operator_status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feed_items_ingest
  ON feed_items(ingest_time DESC);
CREATE INDEX IF NOT EXISTS idx_match_candidates_feed
  ON match_candidates(feed_item_id);
CREATE INDEX IF NOT EXISTS idx_actions_incident
  ON actions(incident_id, created_at DESC);
"""


def _dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def _db_path() -> Path:
    return get_settings().db_path_obj


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Context-managed sqlite connection with dict rows and foreign keys on."""

    path = _db_path()
    _ensure_parent(path)
    conn = sqlite3.connect(path)
    conn.row_factory = _dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Apply schema, idempotent. Called from FastAPI startup hook."""

    path = _db_path()
    _ensure_parent(path)
    with get_conn() as conn:
        conn.executescript(SCHEMA_SQL)


def reset_db() -> None:
    """Drop every table, recreate schema. Used by /demo/reset."""

    with get_conn() as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS actions;
            DROP TABLE IF EXISTS incidents;
            DROP TABLE IF EXISTS match_candidates;
            DROP TABLE IF EXISTS feed_items;
            DROP TABLE IF EXISTS assets;
            DROP TABLE IF EXISTS users;
            """
        )
        conn.executescript(SCHEMA_SQL)
