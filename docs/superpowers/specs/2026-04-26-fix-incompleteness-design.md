# Design — Fix the "this project is so incomplete" gaps

**Date:** 2026-04-26
**Author:** Claude (with user)
**Repo:** `D:\kill-cont-fresh` · branch `second_branch`
**Status:** Approved by user 2026-04-26 02:30; ready for plan

---

## Problem statement

After playing through the demo, the user surfaced six concrete failures or
confusions that, taken together, mean the product **looks complete on the
surface but doesn't behave coherently** end-to-end.

Each item below is named with an issue ID (`I1`–`I6`) so the implementation
plan can reference them directly.

### I1 — "Upload and protect" silently does nothing

`apps/web/src/features/assets/AssetUploadModal.tsx:19`

```ts
const canSubmit = useMemo(() => !!title.trim() && !!file && !upload.isPending, …);
<button disabled={!canSubmit} type="submit">Upload and protect</button>
```

The Title `<input>` shows the placeholder `"Final whistle broadcast clip"`. If
the user reads the placeholder as already-filled and never types, `title.trim()`
is `""`, `canSubmit` is `false`, the button is silently disabled, and clicking
it does nothing. There is no inline validation message and no autofocus on the
field, so users — including this one — interpret it as "the upload feature is
broken." It is not; the feedback is missing.

### I2 — Live Watch "Latest segments" is unattributed theatre

`apps/api/app/api/routes/demo.py:217–252`

```python
LIVE_SEGMENT_STATUSES = ["Segment clean","Signal match","Segment clean",
                         "Restream suspected","Segment clean"]

async def _live_emitter(...):
    for i in range(total):
        ...
        payload = {"minute": f"{minute_base}:{(18+i*6)%60:02d}",
                   "source": random.choice([...]),
                   "status": status,
                   "latency_seconds": random.randint(28,58)}
        await publish("live.segment", payload)
```

Every field shown in the "Latest segments" rail (`minute`, `source`,
`latency_seconds`, `status`) is randomized from hardcoded lists. None of it
corresponds to a real fingerprinting pass. The UI presents it identically to
real data, which is dishonest. Users reasonably ask "what is this giving me?"

### I3 — "Fresh from the matcher" rail rarely changes

`demo.py:257–266`

```python
if status == "Restream suspected":
    try:
        await simulate_incident(SimulateRequest(asset_id=asset_id,
            platform=platform or random.choice(SIMULATED_PLATFORMS)))
    except Exception:
        pass
```

Out of 8 segments per Live click, `Restream suspected` fires only on
segment 4. So **exactly one** new incident is created per click. The rail
shows `latestIncidents = allIncidents.slice(0, 4)` — the top-4 of a list
seeded with 4–10 rows. New rows are not visually distinguished (no "NEW"
chip, no Gemini reasoning preview), so the rail looks unchanged.

### I4 — Uploading an asset doesn't trigger any matcher work

`apps/api/app/api/routes/assets.py:58–95`

```python
@router.post("/{asset_id}/upload")
async def upload_asset_media(...):
    storage.save_bytes(...)
    storage.make_preview(...)
    storage.make_frame_strip(...)
    phash = compute_phash(primary)
    UPDATE assets SET primary_path=?, preview_path=?, phash=?, status='watching' WHERE id=?
    await publish("asset.updated", {"asset_id": asset_id})
```

Upload computes a pHash but **never compares it against existing feed
items**. No `match_candidates` rows, no `incidents`, no Gemini calls. So
Monitor / Incidents / Evidence / Overview all stay frozen on the seeded
state — the new asset adds a row to the Assets list and nothing else
changes anywhere in the product. This is the largest single gap.

### I5 — Overview metric counts barely move after a Live run

`apps/web/src/features/overview/useDashboardOverview.ts:14–22` correctly
listens for `incident.created` SSE and invalidates the dashboard query.
The plumbing is fine. The user's frustration is downstream of I3: when
each Live click adds exactly one incident, `Active incidents 10 → 11`
is easy to miss.

### I6 — Gemini's role is invisible

`generate_triage()` is called from `simulate_incident()` and indirectly
from `_live_emitter()`. Its three return fields populate every incident's
`reason_short` / `reason_detailed` / `operator_copy`. These show on
Incidents, Incident Detail, and Evidence pages — **with no indicator
that Gemini wrote them**. There's no chip, no model name on the row, no
tooltip. The Settings page test button is the only place "Gemini" is
named in the UI, leaving the user to ask "where does Gemini even fit
beyond that?"

---

## Goals

By the end of this work the user can:

1. Open the asset uploader, see exactly what's required, and either get
   a clear validation error or a registered asset.
2. Upload an asset and immediately see new feed items, match candidates,
   and incidents appear on Monitor / Incidents / Evidence / Overview —
   driven by a real pHash scan against existing feeds plus an opinionated
   one-shot synthetic feed-vs-asset match.
3. Click "Start live event" and watch 2–3 fresh incidents land in the
   "Fresh from matcher" rail with a visible NEW pulse and the Gemini
   reasoning excerpt under each card.
4. See, on every incident card and detail view, whether the reasoning
   came from Gemini (and which model/latency) or from the canned fallback.
5. Trust that everything labeled "live" is doing real work; everything
   labeled "synthetic" is honestly named.

## Non-goals

- Real platform connectors (YouTube, Reddit, etc.) — still simulated.
- Custom-trained matching models — pHash stays.
- Multi-tenant / multi-org — single hardcoded `org-demo-1`.
- Replacing the synthetic Live segment stream with real video ingestion.
  Instead, we relabel it honestly and let the synthetic stream still
  drive demo theatre.

## Out of scope (deferred)

- Migration to Cloud Run / Firestore / Firebase Hosting (S10–S12 of the
  parent plan, picks up after this).
- E2E test harness beyond the existing `scripts/smoke.py`.

---

## Architecture

We split the work into four bundles, each independently shippable, in
the order **B → A → C → D**. B is the largest (real backend matcher);
A is the smallest (form UX); C is medium (live-watch coherence); D
threads visibility throughout the UI.

### Bundle B — On-upload matcher

The missing pipeline. Implemented in three layers:

**1. New service: `app/services/matcher.py`**

```
def match_asset_against_feeds(asset_id: str) -> list[dict]:
    """Compare a single asset's pHash against every feed_items row in
    the same org. For any pair whose Hamming-derived similarity >=
    PHASH_MATCH_THRESHOLD, write a match_candidate. Promote and create
    an incident for any candidate that satisfies should_promote_to_incident.
    Run generate_triage() per promoted incident, store the result on
    the incidents row plus a new triage_source column.

    Returns a list of {feed_item_id, similarity, severity, incident_id?}
    so the route handler can respond with what was found."""
```

Reuses `app.services.similarity.{hamming_distance, similarity_score,
should_promote_to_incident, derive_severity}` and `app.services.triage.
generate_triage`. No raw SQL — uses the existing `repos.insert_*`
adapter helpers so it works against both SQLite and Firestore.

**2. Wire into upload route: `app/api/routes/assets.py`**

```
@router.post("/{asset_id}/upload")
async def upload_asset_media(...):
    # ... existing pHash + preview work ...
    matches = await matcher.match_asset_against_feeds(asset_id)
    for m in matches:
        if m.get("incident_id"):
            await publish("incident.created", {...})
    return AssetDetail(..., matches=matches)
```

`AssetDetail` schema gains an optional `matches: list[AssetMatchSummary]`
so the FE can render a confirmation toast ("Found 2 matching feed items;
1 incident created").

**3. Demo-friendly "always something happens" path**

If `match_asset_against_feeds` returns zero candidates (very common —
the new asset's pHash won't match seeded mirror images by accident),
synthesize ONE fresh feed item by calling the existing
`derive_repost(primary, …)` path (the same code `simulate_incident`
uses) and run the matcher again. This guarantees the demo flow always
produces at least one visible incident on upload, while real-data
behavior is unchanged when matches do exist.

Gated behind a new `Settings.synthesize_demo_match: bool = True` flag in
`app/core/config.py`. Default `True`, override via env var
`SYNTHESIZE_DEMO_MATCH=false` for `RUNTIME_PROFILE=public` deployments.

### Bundle A — Asset upload form UX

Pure frontend; backend untouched.

`AssetUploadModal.tsx`:
- Autofocus the Title input on modal open.
- Track `touched` per field; on blur with empty Title, render an inline
  red helper "Title is required."
- On submit, if `canSubmit` is false, set all fields to touched so the
  required-field hint becomes visible (rather than the silent disable).
- Distinct placeholder color via `::placeholder` rule so it's clearly
  non-content.
- After successful upload, show a toast ("AST-XXX uploaded. 2 matches
  found, 1 incident created.") wired to the new Bundle B response.
- Auto-close modal AND scroll the new asset row into view + flash it
  with the same `freshIds` animation already used on incidents.

### Bundle C — Live Watch honest + lively

`demo.py::_live_emitter`:
- Promote 2–3 segments (not 1) to the simulate trigger. Easiest:
  segments at index 1, 3, 5 each call `simulate_incident` with
  rotating asset_ids (use `_pick_asset(None)` cycling, not the
  user-selected one for every shot — that way 3 different asset
  cards appear).
- Optional: keep one user-selected one for the first promoted segment
  if `asset_id` was provided.

`LiveWatchPage.tsx` (segment stream pane):
- Rename header to "Live segment monitor (synthetic stream)" with a
  tooltip-style subtitle: "Synthetic ~2 s segment ticks illustrating
  what the matcher would see on a real broadcast feed. Real matching
  fires on the highlighted segments — those create incidents in the
  rail to the right."
- Highlight (different border tint) segments whose status is
  `Restream suspected`/`Signal match` so you can visually tie a
  segment to the incident it produced.

`LiveWatchPage.tsx` ("Fresh from matcher" rail):
- Use `freshIds` (already tracked by `useIncidents`) to render a "NEW"
  chip + 4-second pulse animation per row.
- Show the first ~14 words of `incident.reason_short` under the title,
  so Gemini's writing is visible at a glance.

### Bundle D — Gemini visibility

**Backend:**
- Add `triage_source: str` column to `incidents` (`'gemini' | 'fallback'`).
  Migration: SQLite `ALTER TABLE incidents ADD COLUMN triage_source TEXT
  NOT NULL DEFAULT 'fallback'`. Firestore: just write it on new docs;
  reads default to `'fallback'` when missing.
- `generate_triage()` already exposes `LAST_GEMINI_SOURCE` per call.
  In the two callers (`simulate_incident`, `matcher`), capture the
  module-level value immediately after the call and write it on the
  incident.
- Add three columns to `incidents`: `triage_source TEXT`,
  `triage_model TEXT`, `triage_latency_ms REAL`. All three default to
  null/`'fallback'` for back-compat. Three columns is simpler than a
  packed JSON blob and survives any future indexing.
- `IncidentSummary` and `IncidentDetail` schemas surface all three
  fields as optional.

**Frontend:**
- New small component `<TriageSourceChip source detail? />`. Renders
  `🧠 Gemini` (green) or `📝 Canned` (grey). On hover, tooltip with
  model + latency + timestamp.
- Render the chip on:
  - Incident card on Incidents page
  - Incident detail header
  - Evidence page reason block
  - Live Watch "Fresh from matcher" rail per-row
- Settings page: add a "Where Gemini is in the loop" card with three
  bullets ("Triage reasoning on every new incident", "Visible on every
  incident card via the chip", "Falls back to canned strings when the
  key is missing or rate-limited") and counters
  ("X incidents this session: Y Gemini, Z canned").

---

## Data flow (Bundle B end-to-end)

```
User clicks "Upload and protect"
  -> POST /assets             (creates assets row, status='processing')
  -> POST /assets/{id}/upload (uploads file)
     -> save bytes, make_preview, make_frame_strip
     -> compute_phash
     -> UPDATE assets SET phash=?, status='watching'
     -> matcher.match_asset_against_feeds(asset_id)
        -> for each feed_item with phash:
             distance = hamming(asset.phash, feed.phash)
             score = similarity(...)
             if score >= threshold:
                insert match_candidate
                if should_promote(score, provenance_gap, threshold):
                   triage = await generate_triage(...)
                   triage_source = LAST_GEMINI_SOURCE  # 'gemini'|'fallback'
                   insert incident (with triage_source, triage_model, triage_latency_ms)
                   await publish("incident.created", {...})
        -> if no matches AND demo_mode:
             synthesize one feed_item via derive_repost(asset.primary)
             rerun the loop on that one feed_item
        -> return matches[]
     -> publish "asset.updated"
     -> return AssetDetail with matches[]

FE:
  -> AssetUploadModal closes, toast shows match summary
  -> Assets list invalidates -> new row visible
  -> SSE incident.created fires -> Incidents/Evidence/Monitor/Overview
                                   /LiveWatch all refetch via existing hooks
```

## Error handling

- Backend matcher: on any exception inside `match_asset_against_feeds`,
  log + return empty list. Upload still succeeds (we don't want an
  unrelated matcher bug to block asset registration).
- Gemini timeouts/errors: existing fallback path stays. `triage_source`
  is set to `'fallback'` on any non-`ok` Gemini status, so the chip
  reflects reality even when Gemini fails mid-batch.
- FE: if `AssetDetail.matches` is missing (older backend or no matches),
  the toast just says "AST-XXX registered." No error UI.

## Testing strategy

No formal test framework is configured (per CLAUDE.md). Verification:

1. `python -m compileall apps/api/app` — clean.
2. `cd apps/web && npx vite build` — clean (continues to skip `tsc -b`
   per the existing TS5103 workaround).
3. Manual sequence:
   - Reset demo from Settings.
   - Upload a real image (any sports JPG). Confirm toast "X matches
     found", confirm Monitor / Incidents pages now show new rows.
   - Click Start live event. Confirm 2–3 NEW pulses in the rail with
     Gemini reason snippets, two different asset cards.
   - Open one incident detail. Confirm Gemini chip shows green with
     tooltip showing `gemini-2.5-flash · 4.1s · 02:31`.
   - With `GEMINI_API_KEY` unset, repeat — chip should be grey
     "Canned" everywhere.
4. `python scripts/smoke.py` against the running API — must remain
   exit 0 (the smoke harness already covers seed → simulate → action,
   we're not breaking those).

---

## Migration / backward compatibility

- **DB migration:** Three `ALTER TABLE incidents ADD COLUMN` statements
  in `app/services/db.py::init_db()`, each wrapped in a try/except
  catching `sqlite3.OperationalError` so re-runs are idempotent.
  Existing rows get NULLs which the FE renders as the "Canned" chip
  (same visual as `triage_source='fallback'`). No data loss.
- **Firestore:** new docs include `triage_source`; old docs missing it
  default to `'fallback'` in the read mapper. No back-fill needed.
- **API contract:** `IncidentSummary` / `IncidentDetail` get optional
  fields. FE handles missing values gracefully (chip shows "Unknown").
- **Local profile remains the offline fallback.** The matcher works
  identically against SQLite — no cloud dependency added.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Gemini-per-match floods the API on a feed-rich org | Cap matcher to first 20 promoted incidents per upload; remaining matches get canned text + a banner "5 more matches not triaged due to throttle" |
| The synthetic "always one match" path masks real bugs | Gated behind `demo_mode` setting; `RUNTIME_PROFILE=public` flips it off |
| The `triage_source` column write fails on Firestore due to a missing index | None needed — it's a simple field write, not a query field |
| FE chip clutters incident cards | Single small badge; component is purely additive |

---

## Approval

User approved the four-bundle plan in this order: **B → A → C → D**, in
session of 2026-04-26 02:30. They explicitly authorized "after you
finish bundling that, start implementation also" — so the writing-plans
skill follows immediately, no second approval gate needed.
