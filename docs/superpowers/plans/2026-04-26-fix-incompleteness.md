# Fix the "this project is so incomplete" gaps — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the six demo-blocking gaps (I1–I6) the user surfaced — make Upload-and-Protect work, run a real matcher on upload so Monitor/Incidents/Evidence/Overview all update, label the live segment stream honestly, refresh "Fresh from matcher" every Live click, and make Gemini visible everywhere.

**Architecture:** Four independently-shippable bundles in order **B → A → C → D**, no test framework (verification = `python -m compileall app` + `npx vite build` + manual demo sequence). All work stays in the local profile (`RUNTIME_PROFILE=local + AUTH_BACKEND=demo`); cloud profile remains the offline fallback. Adapter-clean — every backend write goes through `repos.insert_*` so SQLite + future Firestore behave identically.

**Tech Stack:** FastAPI 0.111 + pydantic-settings + sqlite3 + httpx (Gemini) on the backend; React 19 + Vite 8 + TanStack Query + framer-motion on the frontend. Spec: `docs/superpowers/specs/2026-04-26-fix-incompleteness-design.md`.

**No-test-framework rule:** Per `CLAUDE.md`, no `pytest`/`vitest` is configured. "Write the failing test" steps in this plan are replaced with "Write a failing manual probe" — a one-liner Python REPL or curl invocation we expect to error before the implementation step, then succeed after. The TDD spirit (red → green → commit) is preserved without bringing up new infra.

---

## File structure

### Bundle B — On-upload matcher

| File | Action | Responsibility |
|---|---|---|
| `apps/api/app/services/matcher.py` | **Create** | Single function `match_asset_against_feeds(asset_id) -> list[dict]`. Scans every feed_item with a pHash, writes match_candidate + (when promoted) incident rows + Gemini triage, returns summary list. |
| `apps/api/app/api/routes/assets.py` | Modify (lines 58–95) | Call the matcher after pHash is computed, attach `matches` to the returned `AssetDetail`, publish one `incident.created` per promoted incident. |
| `apps/api/app/schemas/asset.py` | Modify | Add `AssetMatchSummary` model + `AssetDetail.matches: list[AssetMatchSummary] = []`. |
| `apps/api/app/core/config.py` | Modify (after line 55) | Add `synthesize_demo_match: bool = True` (env: `SYNTHESIZE_DEMO_MATCH`). |
| `apps/api/app/services/db.py` | Modify (`init_db`) | 3 `ALTER TABLE incidents ADD COLUMN` (triage_source, triage_model, triage_latency_ms) wrapped in try/except for idempotency. |
| `apps/api/app/services/repos/_sqlite.py` | Modify (`insert_incident`, `get_incident_detail`, `INCIDENT_JOIN_SELECT`) | Persist + read the 3 new triage columns. |
| `apps/api/app/services/repos/_common.py` | Modify (`incident_to_summary`) | Surface `triage_source`, `triage_model`, `triage_latency_ms` on the summary dict. |
| `apps/api/app/api/routes/demo.py` | Modify (`simulate_incident`) | Capture `LAST_GEMINI_SOURCE/MODEL/LATENCY` after `generate_triage` and pass them into the incident insert. |
| `apps/web/src/lib/types.ts` | Modify | Add `AssetMatchSummary` + extend `AssetDetail` with `matches`; add the 3 triage_* fields to `IncidentSummary` and `IncidentDetail`. |

### Bundle A — Asset upload form UX

| File | Action | Responsibility |
|---|---|---|
| `apps/web/src/features/assets/AssetUploadModal.tsx` | Modify | Autofocus Title; touched-state + inline error helpers; "show all errors" on submit attempt; success toast wired to Bundle B `matches`. |
| `apps/web/src/features/assets/AssetsPage.tsx` | Modify | Track most-recent uploaded asset id, scroll its tile into view, attach a `--fresh` flash for ~4s. |
| `apps/web/src/styles/global.css` | Modify | Add `.field-error`, `.field--invalid`, `.upload-toast`, `.asset-tile--fresh` keyframe rules; tweak `::placeholder` color so it's obviously non-content. |

### Bundle C — Live Watch honest + lively

| File | Action | Responsibility |
|---|---|---|
| `apps/api/app/api/routes/demo.py` | Modify (`_live_emitter`) | Promote 3 segments (indexes 1, 3, 5) to real `simulate_incident`, rotating `_pick_asset(None)` each call. |
| `apps/web/src/features/live-watch/LiveWatchPage.tsx` | Modify | Rename "Latest segments" → "Live segment monitor (synthetic stream)" + tooltip; render `TriageSourceChip` + 14-word `reason_short` snippet + NEW pulse on each Fresh row using `freshIds`. |
| `apps/web/src/styles/global.css` | Modify | Add `.synthetic-stream-note`, `.live-row--fresh`, `.live-row__reason` rules. |

### Bundle D — Gemini visibility

| File | Action | Responsibility |
|---|---|---|
| `apps/web/src/components/ui/TriageSourceChip.tsx` | **Create** | Pure presentational: `{source, model?, latencyMs?}` → `🧠 Gemini` (green) or `📝 Canned` (grey) with hover tooltip. |
| `apps/web/src/features/incidents/IncidentsPage.tsx` | Modify | Render the chip in the incident row metadata. |
| `apps/web/src/features/incidents/IncidentDetailPage.tsx` | Modify | Render the chip beside the reason header. |
| `apps/web/src/features/evidence/EvidencePage.tsx` | Modify | Render the chip on the reason block. |
| `apps/web/src/features/live-watch/LiveWatchPage.tsx` | Modify | Render the chip per-row in the Fresh rail (already touched in Bundle C). |
| `apps/web/src/features/settings/SettingsPage.tsx` | Modify | Add a "Where Gemini is in the loop" card with three bullets + counter ("X this session: Y Gemini, Z canned"). |
| `apps/web/src/features/settings/useGeminiCounters.ts` | **Create** | TanStack Query hook reading `/incidents` + computing the counters; refreshes on `incident.created`. |
| `apps/web/src/styles/global.css` | Modify | `.triage-chip`, `.triage-chip--gemini`, `.triage-chip--fallback`, `.triage-chip__tooltip` rules. |

---

## Bundle B — On-upload matcher

### Task B1: DB migration — three triage columns + idempotent ALTER

**Files:**
- Modify: `apps/api/app/services/db.py:146-152` (`init_db`)

- [ ] **Step 1: Write a failing manual probe**

Run (with the API NOT running so we get exclusive DB access):

```bash
cd apps/api
python -c "import sqlite3; c=sqlite3.connect('var/app.db'); print(c.execute('PRAGMA table_info(incidents)').fetchall())"
```

Expected BEFORE the change: column list contains `id, org_id, asset_id, feed_item_id, title, severity, triage_label, trust_score, spread_score, operator_status, reason_short, reason_detailed, operator_copy, map_lat, map_lng, map_region, created_at, updated_at` — and **does NOT** contain `triage_source`, `triage_model`, or `triage_latency_ms`. We're about to add those.

- [ ] **Step 2: Implement migration**

Replace the body of `init_db()` in `apps/api/app/services/db.py` with:

```python
def init_db() -> None:
    """Apply schema, idempotent. Called from FastAPI startup hook."""

    path = _db_path()
    _ensure_parent(path)
    with get_conn() as conn:
        conn.executescript(SCHEMA_SQL)
        # --- Idempotent column additions for older DBs (Bundle B / Plan 2026-04-26) ---
        for ddl in (
            "ALTER TABLE incidents ADD COLUMN triage_source TEXT",
            "ALTER TABLE incidents ADD COLUMN triage_model TEXT",
            "ALTER TABLE incidents ADD COLUMN triage_latency_ms REAL",
        ):
            try:
                conn.execute(ddl)
            except sqlite3.OperationalError:
                # Column already exists on a freshly seeded DB — fine.
                pass
```

- [ ] **Step 3: Run the probe again to verify the columns appear**

Boot the API once so `init_db()` runs (`python -m uvicorn app.main:app --port 8000` then Ctrl+C after "Application startup complete."), then re-run:

```bash
python -c "import sqlite3; c=sqlite3.connect('var/app.db'); print([r[1] for r in c.execute('PRAGMA table_info(incidents)').fetchall()])"
```

Expected: list now includes `triage_source`, `triage_model`, `triage_latency_ms`.

Re-run `init_db` a second time (boot + Ctrl+C again) — should NOT raise `duplicate column` errors. The try/except swallows them.

- [ ] **Step 4: compileall**

```bash
cd apps/api && python -m compileall app
```

Expected: exit 0, no `*.py` errors printed.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/services/db.py
git commit -m "feat(b1): add triage_source/model/latency_ms columns to incidents (idempotent)"
```

---

### Task B2: Settings flag — `synthesize_demo_match`

**Files:**
- Modify: `apps/api/app/core/config.py:43-55`

- [ ] **Step 1: Failing probe**

```bash
cd apps/api
python -c "from app.core.config import get_settings; print(get_settings().synthesize_demo_match)"
```

Expected: `AttributeError: 'Settings' object has no attribute 'synthesize_demo_match'`.

- [ ] **Step 2: Add the field**

In `apps/api/app/core/config.py`, immediately after the `phash_match_threshold: float = 0.80` block (around line 43), add:

```python
    # Bundle B: when an upload finds zero real matches, synthesize ONE
    # derived feed-item from the asset's primary so the demo flow always
    # produces a visible incident. Off by default in public deployments.
    synthesize_demo_match: bool = True
```

- [ ] **Step 3: Re-run probe**

```bash
python -c "from app.core.config import get_settings; print(get_settings().synthesize_demo_match)"
```

Expected: `True`.

- [ ] **Step 4: Probe env override**

```bash
SYNTHESIZE_DEMO_MATCH=false python -c "from app.core.config import get_settings; print(get_settings().synthesize_demo_match)"
```

Expected: `False`.

- [ ] **Step 5: compileall + commit**

```bash
python -m compileall app
git add apps/api/app/core/config.py
git commit -m "feat(b2): add Settings.synthesize_demo_match flag"
```

---

### Task B3: Persist + read the three triage columns through `repos`

**Files:**
- Modify: `apps/api/app/services/repos/_sqlite.py:262-385` (`insert_incident`, `get_incident_detail`, `INCIDENT_JOIN_SELECT`)
- Modify: `apps/api/app/services/repos/_common.py` (`incident_to_summary`)

- [ ] **Step 1: Failing probe**

After Task B1 the columns exist but nothing writes them. Probe:

```bash
cd apps/api
python -c "
from app.services import repos
from app.services.db import get_conn
with get_conn() as c:
    row = c.execute('SELECT id, triage_source, triage_model, triage_latency_ms FROM incidents LIMIT 1').fetchone()
    print(row)
"
```

Expected: row exists from previous seed, but `triage_source/model/latency_ms` are all `None`. After Task B6 wires `simulate_incident` to pass them, a fresh seed should populate them.

- [ ] **Step 2: Extend `insert_incident` to accept + persist three new keys**

In `apps/api/app/services/repos/_sqlite.py`, replace the `INSERT INTO incidents (...)` SQL inside `insert_incident` (lines 360–384) with:

```python
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
```

- [ ] **Step 3: Surface the columns in `get_incident_detail`**

Find the return-dict assembly inside `get_incident_detail` (around lines 87–115 of `_sqlite.py`). Append three keys to the returned dict immediately after `"updated_at": incident["updated_at"],`:

```python
        "triage_source": incident.get("triage_source"),
        "triage_model": incident.get("triage_model"),
        "triage_latency_ms": incident.get("triage_latency_ms"),
```

- [ ] **Step 4: Surface the columns in `incident_to_summary`**

Open `apps/api/app/services/repos/_common.py`. Find the `incident_to_summary` function (it builds an `IncidentSummary`-shaped dict from a JOIN row). Add three keys to the returned dict — immediately before the closing `}`:

```python
        "triage_source": row.get("triage_source"),
        "triage_model": row.get("triage_model"),
        "triage_latency_ms": row.get("triage_latency_ms"),
```

(If the existing function uses dict literal returns — adapt; the goal is the three keys travel from JOIN row → list endpoint.)

- [ ] **Step 5: Verify the columns reach the list endpoint**

```bash
cd apps/api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 2
TOKEN=killcont-demo-demo-user-1
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/incidents | python -c "import json,sys; d=json.load(sys.stdin); print([{k: v.get(k) for k in ('incident_id','triage_source','triage_model','triage_latency_ms')} for v in d['items'][:2]])"
kill %1
```

Expected: the keys appear in the response (values may be `null` until B6 populates them).

- [ ] **Step 6: compileall + commit**

```bash
python -m compileall app
git add apps/api/app/services/repos/_sqlite.py apps/api/app/services/repos/_common.py
git commit -m "feat(b3): persist + surface triage_source/model/latency_ms"
```

---

### Task B4: Schema — `AssetMatchSummary` + `AssetDetail.matches`

**Files:**
- Modify: `apps/api/app/schemas/asset.py:36-51`

- [ ] **Step 1: Failing probe**

```bash
cd apps/api
python -c "from app.schemas.asset import AssetMatchSummary"
```

Expected: `ImportError: cannot import name 'AssetMatchSummary'`.

- [ ] **Step 2: Add the schema + extend AssetDetail**

In `apps/api/app/schemas/asset.py`, append after the existing `AssetDetail` class:

```python
class AssetMatchSummary(BaseModel):
    feed_item_id: str
    similarity_score: float
    confidence_band: str
    severity: str
    incident_id: Optional[str] = None
    triage_source: Optional[str] = None  # 'gemini' | 'fallback' | None
    synthetic: bool = False              # True when feed item was generated by demo fallback
```

Modify `AssetDetail` — add one field at the end of the class body:

```python
    matches: list[AssetMatchSummary] = []
```

- [ ] **Step 3: Re-run probe**

```bash
python -c "from app.schemas.asset import AssetMatchSummary, AssetDetail; print(AssetDetail.model_fields['matches'].annotation)"
```

Expected: `list[AssetMatchSummary]`.

- [ ] **Step 4: compileall + commit**

```bash
python -m compileall app
git add apps/api/app/schemas/asset.py
git commit -m "feat(b4): AssetMatchSummary + AssetDetail.matches"
```

---

### Task B5: Create `app/services/matcher.py`

**Files:**
- Create: `apps/api/app/services/matcher.py`

- [ ] **Step 1: Failing probe**

```bash
python -c "from app.services import matcher"
```

Expected: `ModuleNotFoundError: No module named 'app.services.matcher'`.

- [ ] **Step 2: Write the module**

Create `apps/api/app/services/matcher.py` with this exact content:

```python
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
from app.services.triage import (
    LAST_GEMINI_LATENCY_MS,
    LAST_GEMINI_SOURCE,
    generate_triage,
)


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

    org_id = asset.get("org_id") or settings.demo_org_id
    asset_phash = asset["phash"]
    summaries: list[dict[str, Any]] = []
    promoted = 0

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
    return the FE-facing summary. Honors GEMINI_PROMOTE_BUDGET."""

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
            triage_source = LAST_GEMINI_SOURCE  # captured immediately
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
    return await _score_pair(
        asset=asset,
        feed=feed_full,
        score=max(score, settings.phash_match_threshold + 0.05),
        promoted_so_far=0,
        synthetic=True,
    )
```

- [ ] **Step 3: Re-run probe**

```bash
python -c "from app.services import matcher; print(matcher.match_asset_against_feeds.__doc__[:60])"
```

Expected: prints the first 60 chars of the module docstring (no error).

- [ ] **Step 4: compileall + commit**

```bash
python -m compileall app
git add apps/api/app/services/matcher.py
git commit -m "feat(b5): matcher service — pair-wise scan, candidates, promotion, triage, demo synth"
```

---

### Task B6: Update `simulate_incident` to capture triage source/model/latency

**Files:**
- Modify: `apps/api/app/api/routes/demo.py:174-202` (`simulate_incident`)

- [ ] **Step 1: Failing probe**

```bash
# Restart API after B3, then:
TOKEN=killcont-demo-demo-user-1
curl -s -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/demo/simulate-incident | python -c "import json,sys; d=json.load(sys.stdin); print(d['incident'].get('triage_source'), d['incident'].get('triage_model'))"
```

Expected: `None None` (the row is created but the simulate path doesn't populate these yet).

- [ ] **Step 2: Modify simulate_incident**

In `apps/api/app/api/routes/demo.py`, replace the `triage_text = await generate_triage(...)` line and the following `repos.insert_incident({...})` block with:

```python
    triage_text = await generate_triage(asset_full, repos.get_feed_item(feed_id) or {}, score, severity)
    # Capture immediately — these are module-level globals on triage.py.
    from app.services.triage import LAST_GEMINI_SOURCE, LAST_GEMINI_LATENCY_MS
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
```

- [ ] **Step 3: Re-probe**

```bash
# Restart, then:
curl -s -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/demo/simulate-incident | python -c "import json,sys; d=json.load(sys.stdin); print(d['incident'].get('triage_source'), d['incident'].get('triage_model'))"
```

Expected (with `GEMINI_API_KEY` set in `.env`): `gemini gemini-2.5-flash`. With key unset: `fallback None`.

- [ ] **Step 4: compileall + commit**

```bash
python -m compileall app
git add apps/api/app/api/routes/demo.py
git commit -m "feat(b6): simulate_incident captures Gemini source/model/latency"
```

---

### Task B7: Wire matcher into the upload route + AssetDetail.matches

**Files:**
- Modify: `apps/api/app/api/routes/assets.py:58-95`

- [ ] **Step 1: Failing probe**

Upload a JPG via the UI (or curl) and observe the response payload — `matches` will be missing entirely. We're about to make it appear.

- [ ] **Step 2: Modify upload_asset_media**

In `apps/api/app/api/routes/assets.py`, replace the entire body of `upload_asset_media` with:

```python
@router.post("/{asset_id}/upload", response_model=AssetDetail)
async def upload_asset_media(
    asset_id: str,
    file: UploadFile = File(...),
) -> AssetDetail:
    asset = repos.get_asset_detail(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")

    folder = storage.asset_dir(asset_id)
    ext = Path(file.filename or "upload.jpg").suffix.lower() or ".jpg"
    primary = folder / f"original{ext}"
    storage.save_bytes(primary, await file.read())

    preview = folder / "preview.jpg"
    storage.make_preview(primary, preview)
    storage.make_frame_strip(primary, folder / "frames")

    try:
        phash = compute_phash(primary)
    except Exception:
        phash = None

    with get_conn() as conn:
        conn.execute(
            "UPDATE assets SET primary_path = ?, preview_path = ?, phash = ?, "
            "       status = 'watching' WHERE id = ?",
            (
                storage.relpath(primary),
                storage.relpath(preview),
                phash,
                asset_id,
            ),
        )

    # Bundle B: run the matcher against existing feed items. Never let a
    # matcher bug block the asset registration itself.
    from app.services import matcher
    try:
        matches = await matcher.match_asset_against_feeds(asset_id)
    except Exception:
        matches = []

    updated = repos.get_asset_detail(asset_id)
    await publish("asset.updated", {"asset_id": asset_id})

    detail = AssetDetail(**updated)
    detail.matches = [
        AssetMatchSummary(**m) for m in matches
    ]
    return detail
```

Update the imports at the top of the file — replace `from app.schemas.asset import (...)` with:

```python
from app.schemas.asset import (
    AssetCreateRequest,
    AssetCreateResponse,
    AssetDetail,
    AssetListResponse,
    AssetMatchSummary,
    AssetSummary,
)
```

- [ ] **Step 3: Probe end-to-end**

```bash
TOKEN=killcont-demo-demo-user-1
# Reseed for a clean state
curl -s -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/demo/seed >/dev/null
# Create an asset row
ASSET_ID=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
   -d '{"title":"matcher probe","asset_type":"image","provenance_status":"present"}' \
   http://127.0.0.1:8000/api/v1/assets | python -c "import json,sys; print(json.load(sys.stdin)['id'])")
echo "asset=$ASSET_ID"
# Upload a real JPG (any file with a real image header)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -F "file=@apps/api/var/media/AST-172/preview.jpg" \
  "http://127.0.0.1:8000/api/v1/assets/$ASSET_ID/upload" | python -m json.tool | head -30
```

Expected: response includes a `matches` array. On a freshly-seeded DB the asset's pHash is unlikely to score above threshold against the seeded feed items, so the synthetic-fallback path runs — `matches[0].synthetic == True` and `matches[0].incident_id` is set. Hit `GET /incidents` afterwards and the new incident is in the list.

- [ ] **Step 4: compileall + commit**

```bash
python -m compileall app
git add apps/api/app/api/routes/assets.py
git commit -m "feat(b7): upload route runs matcher + returns AssetDetail.matches"
```

---

### Task B8: Frontend types — `AssetMatchSummary` + triage_* on incidents

**Files:**
- Modify: `apps/web/src/lib/types.ts`

- [ ] **Step 1: Failing probe**

```bash
cd apps/web
grep -n "AssetMatchSummary" src/lib/types.ts
```

Expected: empty (no match).

- [ ] **Step 2: Add the types**

In `apps/web/src/lib/types.ts`, find the `AssetDetail` interface and add a `matches` field. Add the new interface immediately above it:

```ts
export interface AssetMatchSummary {
  feed_item_id: string;
  similarity_score: number;
  confidence_band: string;
  severity: string;
  incident_id?: string | null;
  triage_source?: "gemini" | "fallback" | null;
  synthetic?: boolean;
}
```

Then extend `AssetDetail`:

```ts
  matches?: AssetMatchSummary[];
```

Find `IncidentSummary` and `IncidentDetail` interfaces and add three optional fields to each:

```ts
  triage_source?: "gemini" | "fallback" | null;
  triage_model?: string | null;
  triage_latency_ms?: number | null;
```

- [ ] **Step 3: Verify build**

```bash
npx vite build
```

Expected: build succeeds. (`tsc -b` may still emit TS5103, but that's pre-existing — `npx vite build` is the source of truth per `CLAUDE.md`.)

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/types.ts
git commit -m "feat(b8): FE types — AssetMatchSummary + incident triage fields"
```

---

### Bundle B verification gate

- [ ] **Step 1: Run smoke harness**

```bash
python scripts/smoke.py
```

Expected: 10/10 green.

- [ ] **Step 2: Manual end-to-end**

1. Reset demo via Settings (or `POST /demo/reset`).
2. Open `/app/assets`, click + Upload, fill Title "Matcher Test", attach any JPG, submit.
3. Modal closes (Bundle A polish lands later — for now closing without a toast is OK).
4. Open `/app/incidents` — a NEW row exists referencing your asset.
5. Open `/app/monitor` — the new feed item appears.
6. Open `/app/overview` — counts incremented.
7. Click into the new incident — Gemini reason text is populated (or canned text if no key).

If any of those fail, fix before moving to Bundle A.

---

## Bundle A — Asset upload form UX

### Task A1: Autofocus Title + touched-state validation

**Files:**
- Modify: `apps/web/src/features/assets/AssetUploadModal.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Failing probe (manual)**

Open the upload modal. Title input is not focused (cursor is elsewhere); leaving it blank and clicking submit silently disables — no error message.

- [ ] **Step 2: Rewrite the modal**

Replace `apps/web/src/features/assets/AssetUploadModal.tsx` with:

```tsx
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import type { AssetDetail } from "../../lib/types";
import { useAssetUpload } from "./useAssets";

type AssetUploadModalProps = {
  open: boolean;
  onClose: () => void;
  onUploaded?: (detail: AssetDetail) => void;
};

export function AssetUploadModal({ open, onClose, onUploaded }: AssetUploadModalProps) {
  const upload = useAssetUpload();
  const [title, setTitle] = useState("");
  const [assetType, setAssetType] = useState("image");
  const [eventName, setEventName] = useState("Championship Night");
  const [provenanceStatus, setProvenanceStatus] = useState("present");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [touched, setTouched] = useState({ title: false, file: false });
  const [error, setError] = useState<string>("");
  const titleRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (open) {
      // Tiny delay lets the panel animate in before stealing focus.
      const t = setTimeout(() => titleRef.current?.focus(), 60);
      return () => clearTimeout(t);
    }
    setTitle("");
    setAssetType("image");
    setEventName("Championship Night");
    setProvenanceStatus("present");
    setDescription("");
    setFile(null);
    setTouched({ title: false, file: false });
    setError("");
    return undefined;
  }, [open]);

  const titleError = touched.title && !title.trim() ? "Title is required." : "";
  const fileError = touched.file && !file ? "Choose a media file to upload." : "";
  const canSubmit = useMemo(
    () => !!title.trim() && !!file && !upload.isPending,
    [file, title, upload.isPending],
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched({ title: true, file: true });
    if (!title.trim() || !file) {
      setError("Fix the highlighted fields and try again.");
      return;
    }
    setError("");
    try {
      const detail = await upload.mutateAsync({
        title: title.trim(),
        asset_type: assetType,
        event_name: eventName.trim(),
        provenance_status: provenanceStatus,
        description: description.trim() || undefined,
        file,
      });
      onUploaded?.(detail);
      onClose();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Upload failed.");
    }
  }

  if (!open) return null;

  return (
    <article className="panel panel--detail">
      <div className="panel__header">
        <div>
          <span className="eyebrow eyebrow--muted">Register asset</span>
          <h2 className="panel__title">Add official media to protection watch</h2>
        </div>
      </div>

      <form className="auth-panel__form" noValidate onSubmit={onSubmit}>
        <label className={`auth-panel__field ${titleError ? "field--invalid" : ""}`}>
          <span>
            Title <span className="field-required" aria-hidden="true">*</span>
          </span>
          <input
            aria-invalid={!!titleError}
            onBlur={() => setTouched((t) => ({ ...t, title: true }))}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="e.g. Final whistle broadcast clip"
            ref={titleRef}
            type="text"
            value={title}
          />
          {titleError && <span className="field-error" role="alert">{titleError}</span>}
        </label>

        <div className="table-grid table-grid--form">
          <label className="auth-panel__field">
            <span>Type</span>
            <select onChange={(event) => setAssetType(event.target.value)} value={assetType}>
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="live_watch">Live Watch</option>
            </select>
          </label>

          <label className="auth-panel__field">
            <span>Provenance</span>
            <select onChange={(event) => setProvenanceStatus(event.target.value)} value={provenanceStatus}>
              <option value="verified">Verified</option>
              <option value="present">Present</option>
              <option value="pending">Pending</option>
              <option value="missing">Missing</option>
            </select>
          </label>
        </div>

        <label className="auth-panel__field">
          <span>Event</span>
          <input
            onChange={(event) => setEventName(event.target.value)}
            placeholder="Championship Night"
            type="text"
            value={eventName}
          />
        </label>

        <label className="auth-panel__field">
          <span>Description</span>
          <textarea
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Optional context for operators"
            rows={3}
            value={description}
          />
        </label>

        <label className={`auth-panel__field ${fileError ? "field--invalid" : ""}`}>
          <span>
            Media file <span className="field-required" aria-hidden="true">*</span>
          </span>
          <input
            accept="image/*,video/*"
            aria-invalid={!!fileError}
            onBlur={() => setTouched((t) => ({ ...t, file: true }))}
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            type="file"
          />
          {fileError && <span className="field-error" role="alert">{fileError}</span>}
        </label>

        <div className="auth-panel__actions">
          <button className="pill-link pill-link--solid" disabled={!canSubmit} type="submit">
            {upload.isPending ? "Uploading..." : "Upload and protect"}
          </button>
          <button className="pill-link pill-link--ghost" onClick={onClose} type="button">
            Cancel
          </button>
        </div>

        {error && (
          <p className="auth-panel__error" role="alert">
            {error}
          </p>
        )}
      </form>
    </article>
  );
}
```

- [ ] **Step 3: Add CSS rules**

In `apps/web/src/styles/global.css`, append:

```css
.field-required { color: #f0526e; margin-left: 2px; }
.field-error {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #f0526e;
}
.field--invalid input,
.field--invalid select,
.field--invalid textarea {
  border-color: rgba(240, 82, 110, 0.6);
  box-shadow: 0 0 0 2px rgba(240, 82, 110, 0.18);
}
.auth-panel__field input::placeholder,
.auth-panel__field textarea::placeholder {
  color: rgba(207, 215, 240, 0.45);
  font-style: italic;
}
```

- [ ] **Step 4: Verify build**

```bash
cd apps/web && npx vite build
```

Expected: green.

- [ ] **Step 5: Manual probe**

Open `/app/assets`, click + Upload — Title is autofocused. Click submit immediately — red helper "Title is required." + red border on Title and the file field. Fill Title, leave file empty, submit — only file shows red. Filling both lets the button activate.

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/features/assets/AssetUploadModal.tsx apps/web/src/styles/global.css
git commit -m "feat(a1): asset upload modal — autofocus, touched-state validation, distinct placeholder"
```

---

### Task A2: Success toast + scroll-into-view + flash on AssetsPage

**Files:**
- Modify: `apps/web/src/features/assets/AssetsPage.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Failing probe**

Upload an asset successfully — modal closes silently. The new asset is somewhere on the page but the user has no idea what changed.

- [ ] **Step 2: Modify AssetsPage**

Open `apps/web/src/features/assets/AssetsPage.tsx`. We need to:
1. Pass an `onUploaded` handler to `<AssetUploadModal>` that captures the returned `AssetDetail`.
2. Track `recentAssetId: string | null` + `recentMatches: AssetMatchSummary[]` in state.
3. After upload, schedule the asset tile to scroll into view + receive a `--fresh` class for 4500ms.
4. Render a `.upload-toast` floating in the bottom-right summarizing matches.

Apply this diff (search for the existing modal usage and the assets list — exact context will vary, the additions below are the canonical shape):

```tsx
// Near the top of the component:
const [recentAssetId, setRecentAssetId] = useState<string | null>(null);
const [toast, setToast] = useState<{ assetId: string; matches: number; incidents: number; firstSource?: "gemini" | "fallback" | null } | null>(null);

useEffect(() => {
  if (!recentAssetId) return;
  const node = document.querySelector<HTMLElement>(`[data-asset-id="${recentAssetId}"]`);
  node?.scrollIntoView({ behavior: "smooth", block: "center" });
  const t = setTimeout(() => setRecentAssetId(null), 4500);
  return () => clearTimeout(t);
}, [recentAssetId]);

useEffect(() => {
  if (!toast) return;
  const t = setTimeout(() => setToast(null), 6000);
  return () => clearTimeout(t);
}, [toast]);

// Where <AssetUploadModal /> is rendered:
<AssetUploadModal
  open={uploadOpen}
  onClose={() => setUploadOpen(false)}
  onUploaded={(detail) => {
    setRecentAssetId(detail.id);
    const matches = detail.matches ?? [];
    const incidents = matches.filter((m) => !!m.incident_id).length;
    const firstSource = matches.find((m) => m.triage_source)?.triage_source ?? null;
    setToast({ assetId: detail.id, matches: matches.length, incidents, firstSource });
  }}
/>

// On each asset tile root element:
<article
  data-asset-id={asset.asset_id}
  className={`asset-tile${recentAssetId === asset.asset_id ? " asset-tile--fresh" : ""}`}
  ...
>
  ...
</article>

// Anywhere inside the page-frame, append the toast:
{toast && (
  <div className="upload-toast" role="status">
    <strong>{toast.assetId} uploaded.</strong>
    <span>
      {toast.matches} match{toast.matches === 1 ? "" : "es"} found
      {toast.incidents > 0 ? `, ${toast.incidents} incident${toast.incidents === 1 ? "" : "s"} created` : ""}.
    </span>
    {toast.firstSource === "gemini" && <span className="upload-toast__chip">🧠 Gemini reason</span>}
    {toast.firstSource === "fallback" && <span className="upload-toast__chip upload-toast__chip--muted">📝 Canned reason</span>}
  </div>
)}
```

If the existing tile element does not yet use `className="asset-tile"`, swap it (or add `data-asset-id` + the conditional `--fresh` modifier to whatever class is in place — the CSS rule below targets either).

- [ ] **Step 3: Add CSS rules**

Append to `apps/web/src/styles/global.css`:

```css
.upload-toast {
  position: fixed;
  right: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 18px;
  background: rgba(18, 27, 45, 0.96);
  border: 1px solid rgba(120, 175, 255, 0.22);
  border-radius: 12px;
  color: #f4f7ff;
  box-shadow: 0 18px 40px rgba(8, 12, 22, 0.45);
  font-size: 13px;
  z-index: 50;
  max-width: 320px;
}
.upload-toast strong { font-size: 14px; }
.upload-toast__chip {
  align-self: flex-start;
  margin-top: 4px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(75, 200, 130, 0.18);
  color: #74e1a2;
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.upload-toast__chip--muted {
  background: rgba(180, 180, 200, 0.16);
  color: #c0c8de;
}
@keyframes assetTileFlash {
  0%   { box-shadow: 0 0 0 0 rgba(120, 220, 170, 0.0); }
  20%  { box-shadow: 0 0 0 6px rgba(120, 220, 170, 0.45); }
  100% { box-shadow: 0 0 0 0 rgba(120, 220, 170, 0.0); }
}
.asset-tile--fresh,
.assets-grid > [class*="asset-tile"].asset-tile--fresh {
  animation: assetTileFlash 1.6s ease-out 2;
}
```

- [ ] **Step 4: Verify build**

```bash
cd apps/web && npx vite build
```

Expected: green.

- [ ] **Step 5: Manual probe**

Upload an asset. Modal closes → toast appears bottom-right ("AST-XXX uploaded. 1 match found, 1 incident created. 🧠 Gemini reason"). The new tile in the grid scrolls into view and pulses green for ~3s. Toast disappears after 6s.

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/features/assets/AssetsPage.tsx apps/web/src/styles/global.css
git commit -m "feat(a2): assets page — upload toast + scroll-into-view + flash"
```

---

### Bundle A verification gate

- [ ] **Manual end-to-end:** Upload a real JPG. Confirm: autofocus, validation visible, toast appears, asset flashes, Incidents/Monitor/Overview all show new rows.
- [ ] **Build:** `npx vite build` clean.

---

## Bundle C — Live Watch honest + lively

### Task C1: Multi-incident emitter (3 segments promote, rotating assets)

**Files:**
- Modify: `apps/api/app/api/routes/demo.py:217-268` (`LIVE_SEGMENT_STATUSES` + `_live_emitter`)

- [ ] **Step 1: Failing probe**

```bash
TOKEN=killcont-demo-demo-user-1
# Count incidents before
B=$(curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/incidents | python -c "import json,sys; print(len(json.load(sys.stdin)['items']))")
# Trigger one live run
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"segments":8,"interval_seconds":0.5}' http://127.0.0.1:8000/api/v1/demo/live/start
sleep 6
# Count after
A=$(curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/incidents | python -c "import json,sys; print(len(json.load(sys.stdin)['items']))")
echo "before=$B after=$A"
```

Expected before fix: `after = before + 1` (single incident).

- [ ] **Step 2: Rewrite emitter**

In `apps/api/app/api/routes/demo.py`, replace `LIVE_SEGMENT_STATUSES` and `_live_emitter` with:

```python
# Segments at indexes 1, 3, 5 trigger real simulate_incident calls.
LIVE_SEGMENT_STATUSES = [
    "Segment clean",
    "Signal match",       # promote #1
    "Segment clean",
    "Restream suspected", # promote #2
    "Segment clean",
    "Signal match",       # promote #3
    "Segment clean",
    "Segment clean",
]
PROMOTE_STATUSES = {"Signal match", "Restream suspected"}


async def _live_emitter(
    segments: int,
    interval: float,
    asset_id: Optional[str] = None,
    platform: Optional[str] = None,
) -> None:
    total = max(1, segments)
    minute_base = random.randint(68, 88)
    # Rotate assets across the promoted segments so the rail visibly shifts.
    available = repos.get_all_assets_with_phash(_org_id())
    rotation: list[Optional[str]] = []
    if asset_id:
        rotation.append(asset_id)
    if available:
        random.shuffle(available)
        rotation.extend([row["id"] for row in available])
    # Fall back to None (lets simulate_incident pick randomly).
    rotation = rotation or [None]

    rotation_idx = 0
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
            "promoted": status in PROMOTE_STATUSES,
        }
        await publish("live.segment", payload)

        if status in PROMOTE_STATUSES:
            try:
                pick = rotation[rotation_idx % len(rotation)]
                rotation_idx += 1
                await simulate_incident(
                    SimulateRequest(
                        asset_id=pick,
                        platform=platform or random.choice(SIMULATED_PLATFORMS),
                    )
                )
            except Exception:
                pass

    await publish("live.complete", {"segments": total})
```

- [ ] **Step 3: Re-run probe**

Same as Step 1. Expected after fix: `after = before + 3`.

- [ ] **Step 4: compileall + commit**

```bash
python -m compileall app
git add apps/api/app/api/routes/demo.py
git commit -m "feat(c1): live emitter promotes 3 segments with rotating assets"
```

---

### Task C2: LiveWatchPage — honest header copy + tooltip

**Files:**
- Modify: `apps/web/src/features/live-watch/LiveWatchPage.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Failing probe (manual)**

Open `/app/live-watch`. The pane labeled "Latest segments" implies real data. There's no indicator that segments are synthetic.

- [ ] **Step 2: Update copy + add tooltip**

Find the segment-stream pane heading in `apps/web/src/features/live-watch/LiveWatchPage.tsx`. Replace whatever the current title block is with:

```tsx
<div className="panel__header">
  <div>
    <span className="eyebrow eyebrow--muted">Live segment monitor</span>
    <h2 className="panel__title">Synthetic stream <span className="synthetic-badge">SIMULATED</span></h2>
    <p className="synthetic-stream-note">
      ~2 s segment ticks illustrate what the matcher would see on a real broadcast feed.
      Highlighted segments (<em>Signal match</em>, <em>Restream suspected</em>) trigger real
      pHash + Gemini work and create the incidents in the rail to the right.
    </p>
  </div>
</div>
```

In the per-segment rendering loop, add a `live-row--promoted` class when `segment.status === "Signal match"` or `"Restream suspected"`:

```tsx
<li
  className={`live-row${
    segment.status === "Signal match" || segment.status === "Restream suspected"
      ? " live-row--promoted"
      : ""
  }`}
  ...
>
  ...
</li>
```

- [ ] **Step 3: CSS**

Append to `apps/web/src/styles/global.css`:

```css
.synthetic-badge {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 8px;
  font-size: 10px;
  letter-spacing: 0.08em;
  border-radius: 999px;
  background: rgba(180, 180, 220, 0.18);
  color: #c4cdf4;
  vertical-align: middle;
}
.synthetic-stream-note {
  margin: 6px 0 0 0;
  font-size: 12px;
  line-height: 1.5;
  color: rgba(192, 200, 222, 0.78);
  max-width: 540px;
}
.live-row--promoted {
  border-left: 3px solid rgba(120, 200, 160, 0.65);
  background: rgba(120, 200, 160, 0.05);
  padding-left: 10px;
}
```

- [ ] **Step 4: Build + manual probe**

```bash
npx vite build
```

Then `/app/live-watch` — header now says "Synthetic stream [SIMULATED]" with the explanatory note. Promoted segments have a green left border.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/live-watch/LiveWatchPage.tsx apps/web/src/styles/global.css
git commit -m "feat(c2): live watch — honest synthetic-stream copy + promoted-segment highlight"
```

---

### Task C3: "Fresh from matcher" rail — NEW pulse + reason snippet

**Files:**
- Modify: `apps/web/src/features/live-watch/LiveWatchPage.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Failing probe (manual)**

In `/app/live-watch`, click "Go live". Three new incidents land but the rail looks indistinguishable from before — no NEW chip, no reason text under the title.

- [ ] **Step 2: Render NEW chip + reason snippet per row**

Find the rail render block in `LiveWatchPage.tsx`. The hook already returns `freshIds` (a `Set<string>` from `useIncidents({ live: true })`). Update each row to consume both:

```tsx
import { TriageSourceChip } from "../../components/ui/TriageSourceChip"; // Bundle D — wire in C3 already so we don't have to revisit

function snippet(text?: string | null, words = 14): string {
  if (!text) return "";
  const parts = text.split(/\s+/).filter(Boolean);
  if (parts.length <= words) return parts.join(" ");
  return parts.slice(0, words).join(" ") + "…";
}

// inside the rail map:
{liveIncidents.map((incident) => {
  const isFresh = freshIds.has(incident.incident_id);
  return (
    <li
      className={`live-row${isFresh ? " live-row--fresh" : ""}`}
      key={incident.incident_id}
    >
      <div className="live-row__head">
        <strong>{incident.title}</strong>
        {isFresh && <span className="new-chip" aria-label="newly created">NEW</span>}
        <TriageSourceChip
          source={incident.triage_source ?? null}
          model={incident.triage_model ?? null}
          latencyMs={incident.triage_latency_ms ?? null}
        />
      </div>
      <p className="live-row__reason">{snippet(incident.summary)}</p>
    </li>
  );
})}
```

(Adapt to whatever JSX the existing rail uses — keep its structure, layer in `live-row__head`, NEW chip, chip, `live-row__reason`.)

- [ ] **Step 3: CSS**

Append to `apps/web/src/styles/global.css`:

```css
.live-row__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.live-row__reason {
  margin: 4px 0 0 0;
  font-size: 12px;
  line-height: 1.5;
  color: rgba(192, 200, 222, 0.78);
}
.new-chip {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(120, 220, 170, 0.22);
  color: #74e1a2;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
}
@keyframes liveRowPulse {
  0%   { box-shadow: 0 0 0 0 rgba(120, 220, 170, 0.0); }
  18%  { box-shadow: 0 0 0 5px rgba(120, 220, 170, 0.40); }
  100% { box-shadow: 0 0 0 0 rgba(120, 220, 170, 0.0); }
}
.live-row--fresh {
  animation: liveRowPulse 1.4s ease-out 2;
}
```

- [ ] **Step 4: Build**

```bash
cd apps/web && npx vite build
```

Expected: green. **Note:** this task references `TriageSourceChip` which is created in Bundle D Task D1. Either land Bundle D Task D1 first, or temporarily replace the chip with a placeholder span — recommend doing D1 immediately before C3 so the import resolves.

- [ ] **Step 5: Manual probe**

Click Go live. Three rows pulse green, each shows NEW + the chip + the first 14 words of the Gemini-or-canned reason text.

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/features/live-watch/LiveWatchPage.tsx apps/web/src/styles/global.css
git commit -m "feat(c3): fresh-from-matcher rail — NEW pulse, reason snippet, triage chip"
```

---

### Bundle C verification gate

- [ ] **Manual:** click Go live three separate times, watch three different assets land each time, with NEW pulse + reason text.
- [ ] **Smoke:** `python scripts/smoke.py` still 10/10.

---

## Bundle D — Gemini visibility

### Task D1: Create `<TriageSourceChip>`

**Files:**
- Create: `apps/web/src/components/ui/TriageSourceChip.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Failing probe**

```bash
grep -r "TriageSourceChip" apps/web/src
```

Expected: 0 matches.

- [ ] **Step 2: Write the component**

Create `apps/web/src/components/ui/TriageSourceChip.tsx`:

```tsx
import { useState } from "react";

type Props = {
  source?: "gemini" | "fallback" | null;
  model?: string | null;
  latencyMs?: number | null;
  size?: "sm" | "md";
};

function formatLatency(ms: number | null | undefined): string {
  if (ms == null) return "";
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

export function TriageSourceChip({ source, model, latencyMs, size = "sm" }: Props) {
  const [hover, setHover] = useState(false);
  const flavor = source === "gemini" ? "gemini" : "fallback";
  const label = flavor === "gemini" ? "🧠 Gemini" : "📝 Canned";
  const tooltip =
    flavor === "gemini"
      ? `Reasoning generated by ${model ?? "Gemini"}${latencyMs ? ` · ${formatLatency(latencyMs)}` : ""}`
      : "Canned fallback text — Gemini key missing, rate-limited, or errored.";

  return (
    <span
      className={`triage-chip triage-chip--${flavor} triage-chip--${size}`}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onFocus={() => setHover(true)}
      onBlur={() => setHover(false)}
      tabIndex={0}
      aria-label={tooltip}
    >
      {label}
      {hover && <span className="triage-chip__tooltip" role="tooltip">{tooltip}</span>}
    </span>
  );
}
```

- [ ] **Step 3: CSS**

Append to `apps/web/src/styles/global.css`:

```css
.triage-chip {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  cursor: default;
  outline: none;
}
.triage-chip--sm { font-size: 10px; padding: 1px 6px; }
.triage-chip--gemini {
  background: rgba(120, 220, 170, 0.18);
  color: #7be3a4;
  border: 1px solid rgba(120, 220, 170, 0.3);
}
.triage-chip--fallback {
  background: rgba(180, 180, 200, 0.14);
  color: #c0c8de;
  border: 1px solid rgba(180, 180, 200, 0.22);
}
.triage-chip__tooltip {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 10px;
  border-radius: 6px;
  background: rgba(12, 18, 32, 0.96);
  color: #f4f7ff;
  font-size: 11px;
  font-weight: 400;
  white-space: nowrap;
  box-shadow: 0 6px 18px rgba(8, 12, 22, 0.45);
  z-index: 60;
  pointer-events: none;
}
```

- [ ] **Step 4: Build**

```bash
cd apps/web && npx vite build
```

Expected: green.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/components/ui/TriageSourceChip.tsx apps/web/src/styles/global.css
git commit -m "feat(d1): TriageSourceChip — green Gemini / grey Canned with hover tooltip"
```

---

### Task D2: Render chip on Incidents list

**Files:**
- Modify: `apps/web/src/features/incidents/IncidentsPage.tsx`

- [ ] **Step 1: Find the row metadata block**

In `IncidentsPage.tsx`, locate where each incident row renders its meta (severity pill, platform, etc.). We're going to add the chip near the severity pill.

- [ ] **Step 2: Add the import + render**

At the top of the file:

```tsx
import { TriageSourceChip } from "../../components/ui/TriageSourceChip";
```

In the row meta JSX, add:

```tsx
<TriageSourceChip
  source={incident.triage_source ?? null}
  model={incident.triage_model ?? null}
  latencyMs={incident.triage_latency_ms ?? null}
/>
```

- [ ] **Step 3: Build + manual probe**

```bash
npx vite build
```

Open `/app/incidents`. Each row shows the chip. Hover → tooltip with model + latency for Gemini, or fallback explanation.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/features/incidents/IncidentsPage.tsx
git commit -m "feat(d2): incidents list — render TriageSourceChip per row"
```

---

### Task D3: Render chip on Incident Detail + Evidence

**Files:**
- Modify: `apps/web/src/features/incidents/IncidentDetailPage.tsx`
- Modify: `apps/web/src/features/evidence/EvidencePage.tsx`

- [ ] **Step 1: Detail page**

In `IncidentDetailPage.tsx`, near the reason block header (look for "Reason" / "Why this matters" / `reason_short`), add:

```tsx
import { TriageSourceChip } from "../../components/ui/TriageSourceChip";
...
<div className="reason-header">
  <h3>Reasoning</h3>
  <TriageSourceChip
    source={incident.triage_source ?? null}
    model={incident.triage_model ?? null}
    latencyMs={incident.triage_latency_ms ?? null}
    size="md"
  />
</div>
```

- [ ] **Step 2: Evidence page**

In `EvidencePage.tsx`, find the reason block (already renders `reason_detailed` per the DP9 work). Add the same chip beside its title. Pull the incident object from the existing `useIncidentDetail` hook — it already exposes `triage_source`/`triage_model`/`triage_latency_ms` via the schema extension from B3.

- [ ] **Step 3: Build + manual probe**

```bash
npx vite build
```

Open an incident detail and the evidence page — both show the chip beside the reason block.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/features/incidents/IncidentDetailPage.tsx apps/web/src/features/evidence/EvidencePage.tsx
git commit -m "feat(d3): incident detail + evidence — render TriageSourceChip beside reason"
```

---

### Task D4: Settings — "Where Gemini is in the loop" card + counters

**Files:**
- Create: `apps/web/src/features/settings/useGeminiCounters.ts`
- Modify: `apps/web/src/features/settings/SettingsPage.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Failing probe**

Open `/app/settings`. There's no card explaining where Gemini fits or how many incidents used it.

- [ ] **Step 2: Create the counter hook**

Create `apps/web/src/features/settings/useGeminiCounters.ts`:

```ts
import { useMemo } from "react";
import { useIncidents } from "../incidents/useIncidents";

export type GeminiCounters = {
  total: number;
  gemini: number;
  fallback: number;
  unknown: number;
  pctGemini: number;
};

export function useGeminiCounters(): GeminiCounters {
  const { data } = useIncidents({ live: true });
  return useMemo<GeminiCounters>(() => {
    const items = data?.items ?? [];
    let gemini = 0;
    let fallback = 0;
    let unknown = 0;
    for (const i of items) {
      if (i.triage_source === "gemini") gemini += 1;
      else if (i.triage_source === "fallback") fallback += 1;
      else unknown += 1;
    }
    const total = items.length;
    return {
      total,
      gemini,
      fallback,
      unknown,
      pctGemini: total === 0 ? 0 : Math.round((gemini / total) * 100),
    };
  }, [data]);
}
```

- [ ] **Step 3: Add the card to SettingsPage**

In `apps/web/src/features/settings/SettingsPage.tsx`, after the existing "System Status" card and the "Operator Profile" card, add a new card. Import:

```tsx
import { useGeminiCounters } from "./useGeminiCounters";
import { TriageSourceChip } from "../../components/ui/TriageSourceChip";
```

Render block (inside the same `.settings-grid` parent):

```tsx
const counters = useGeminiCounters();
...
<article className="settings-card">
  <h3>Where Gemini is in the loop</h3>
  <ul className="gemini-loop-list">
    <li>
      <TriageSourceChip source="gemini" /> writes the <strong>reason_short</strong>,{" "}
      <strong>reason_detailed</strong>, and <strong>operator_copy</strong> for every new incident
      &mdash; both real (asset upload) and synthesized (live event, simulate-incident).
    </li>
    <li>
      The chip on incidents, evidence, and live-watch tells you which incidents used Gemini and
      which used the canned fallback.
    </li>
    <li>
      When the key is missing, rate-limited, or errors out, KillCont degrades to deterministic
      canned strings so the demo never blocks. The chip turns grey.
    </li>
  </ul>
  <div className="gemini-counters">
    <div>
      <span className="gemini-counters__label">This session</span>
      <strong>{counters.total}</strong>
      <span>incidents</span>
    </div>
    <div>
      <span className="gemini-counters__label">Gemini</span>
      <strong className="gemini-counters__gemini">{counters.gemini}</strong>
      <span>({counters.pctGemini}%)</span>
    </div>
    <div>
      <span className="gemini-counters__label">Canned</span>
      <strong className="gemini-counters__fallback">{counters.fallback}</strong>
      <span>{counters.unknown > 0 ? `(+${counters.unknown} unknown)` : ""}</span>
    </div>
  </div>
</article>
```

- [ ] **Step 4: CSS**

Append to `apps/web/src/styles/global.css`:

```css
.gemini-loop-list {
  list-style: none;
  padding: 0;
  margin: 0 0 16px 0;
  display: grid;
  gap: 10px;
}
.gemini-loop-list li {
  font-size: 13px;
  line-height: 1.55;
  color: rgba(207, 215, 240, 0.85);
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
}
.gemini-counters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 12px;
  border: 1px solid rgba(120, 175, 255, 0.18);
  border-radius: 10px;
  background: rgba(20, 28, 46, 0.45);
}
.gemini-counters > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: flex-start;
}
.gemini-counters strong {
  font-size: 22px;
  line-height: 1;
}
.gemini-counters__label {
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(192, 200, 222, 0.6);
}
.gemini-counters__gemini { color: #7be3a4; }
.gemini-counters__fallback { color: #c0c8de; }
```

- [ ] **Step 5: Build + manual probe**

```bash
cd apps/web && npx vite build
```

Open `/app/settings`. Card appears with three bullets and three counters reflecting the current incident list. Trigger a few simulate-incidents and the counters update via SSE-driven refetch (already wired into `useIncidents`).

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/features/settings/useGeminiCounters.ts apps/web/src/features/settings/SettingsPage.tsx apps/web/src/styles/global.css
git commit -m "feat(d4): settings — 'Where Gemini is in the loop' card + counters"
```

---

### Bundle D verification gate

- [ ] **Manual:** Every product page shows triage chips. Settings card explains the role + counts.
- [ ] **No-key probe:** Unset `GEMINI_API_KEY` in `.env`, restart, simulate-incident — every chip is grey "Canned".
- [ ] **With-key probe:** Re-enable, simulate-incident — new rows are green "Gemini" with a tooltip showing model + latency.
- [ ] **Smoke:** `python scripts/smoke.py` still 10/10.

---

## Final invariants (run after every bundle close)

- [ ] `cd apps/api && python -m compileall app` — exit 0.
- [ ] `cd apps/web && npx vite build` — green.
- [ ] `python scripts/smoke.py` — 10/10.
- [ ] Local profile (`RUNTIME_PROFILE=local`, `AUTH_BACKEND=demo`, no `GEMINI_API_KEY`) still runs the full demo offline.
- [ ] No new secrets committed.

---

## Status updates

After Bundle B closes, append to `docs/status.md` "Closed" section: "B1–B8 — on-upload matcher, AssetDetail.matches, three triage_* incident columns, simulate_incident triage capture (2026-04-26)".
After Bundle A: "A1–A2 — asset upload modal UX (autofocus, validation, toast, flash) (2026-04-26)".
After Bundle C: "C1–C3 — live emitter promotes 3 segments, honest synthetic-stream copy, NEW pulse + reason snippet (2026-04-26)".
After Bundle D: "D1–D4 — TriageSourceChip on Incidents/Detail/Evidence/LiveWatch + Settings 'Where Gemini' card (2026-04-26)".

Update `docs/logbook.md` with one entry per bundle.

Update `CLAUDE.md` "Recently closed gaps" with the new bundle headlines.
