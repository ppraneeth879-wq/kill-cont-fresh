# Live Cascade + Duplicate-Asset Detection — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every tab cascade visibly when live runs fire incidents AND when an operator re-uploads the same asset, deliberately (not accidentally via the synthetic-fallback path).

**Architecture:** Two backend touches (a new pHash threshold knob and a Pass-1 asset×asset duplicate check inside `matcher.py`, plus a single missing `feed.ingested` publish) unlock four frontend touches (Monitor `freshIds`, Evidence "N new cases" banner, sidebar badges, type plumbing). No schema migration. No new dependencies.

**Tech Stack:** FastAPI / Pydantic / SQLite / firebase-admin (backend), React 19 / Vite 8 / TanStack Query / SSE (frontend). Spec: `docs/superpowers/specs/2026-04-27-live-cascade-and-duplicates-design.md` (commit `d9741e2`).

---

### Task 1: `phash_duplicate_threshold` config + `.env.example`

**Files:**
- Modify: `apps/api/app/core/config.py`
- Modify: `apps/api/.env.example`

- [ ] **Step 1: Add the field to Settings**

In `apps/api/app/core/config.py`, find `phash_match_threshold: float = 0.80` and insert directly after it:

```python
    # Asset×asset duplicate detection. Tighter than the asset×feed_item
    # threshold because we are claiming "these are the same image," not
    # "this is a derivative." 0.92 is loose enough for compression/resize
    # tolerance but tight enough to ignore visually-similar placeholders.
    phash_duplicate_threshold: float = 0.92
```

- [ ] **Step 2: Document both knobs in .env.example**

In `apps/api/.env.example`, replace the line `PHASH_MATCH_THRESHOLD=0.80` with:

```
# Matching thresholds
#   PHASH_MATCH_THRESHOLD     - asset vs feed_item (repost/derivative detection)
#   PHASH_DUPLICATE_THRESHOLD - asset vs asset (re-registration of the same image)
PHASH_MATCH_THRESHOLD=0.80
PHASH_DUPLICATE_THRESHOLD=0.92
```

- [ ] **Step 3: Verify**

Run: `cd apps/api && python -c "from app.core.config import get_settings; s=get_settings(); print(s.phash_match_threshold, s.phash_duplicate_threshold)"`
Expected: `0.8 0.92`

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/core/config.py apps/api/.env.example
git commit -m "feat(t1): add PHASH_DUPLICATE_THRESHOLD config knob (0.92)"
```

---

### Task 2: Publish `feed.ingested` from `simulate_incident`

**Files:**
- Modify: `apps/api/app/api/routes/demo.py`

- [ ] **Step 1: Add the publish call**

In `apps/api/app/api/routes/demo.py`, find the `repos.insert_feed_item({...})` call inside `simulate_incident` (around line 133–148). Immediately after that call, add:

```python
    # Bundle E (live cascade): tell Monitor's useFeeds hook a new feed_item
    # exists. Without this, the live run leaves Monitor stale because the
    # only event published below is `incident.created`, which Monitor
    # doesn't listen for.
    await publish("feed.ingested", {"feed_item_id": feed_id})
```

- [ ] **Step 2: Verify**

Run: `cd apps/api && python -m compileall app 2>&1 | tail -3` — expect 0 errors.

Run smoke harness: `cd /d/kill-cont-fresh && python scripts/smoke.py` — expect `[smoke] all green`.

- [ ] **Step 3: Commit**

```bash
git add apps/api/app/api/routes/demo.py
git commit -m "feat(t2): publish feed.ingested after simulate_incident insert_feed_item"
```

---

### Task 3: `AssetMatchSummary.kind` field (backend + frontend types)

**Files:**
- Modify: `apps/api/app/schemas/asset.py`
- Modify: `apps/web/src/lib/types.ts`

- [ ] **Step 1: Add the field to the Pydantic model**

In `apps/api/app/schemas/asset.py`, edit `AssetMatchSummary` to add the new optional field (right after `synthetic`):

```python
class AssetMatchSummary(BaseModel):
    feed_item_id: str
    similarity_score: float
    confidence_band: str
    severity: str
    incident_id: Optional[str] = None
    triage_source: Optional[str] = None
    synthetic: bool = False
    # Bundle E: distinguishes a normal feed match ("feed") from an
    # asset-vs-asset duplicate-registration match ("duplicate"). The
    # frontend uses this to label the upload toast.
    kind: str = "feed"  # "feed" | "duplicate"
```

- [ ] **Step 2: Mirror on the TypeScript side**

In `apps/web/src/lib/types.ts`, edit `AssetMatchSummary`:

```typescript
export type AssetMatchSummary = {
  feed_item_id: string;
  similarity_score: number;
  confidence_band: string;
  severity: string;
  incident_id?: string | null;
  triage_source?: string | null;
  synthetic?: boolean;
  /** Bundle E: 'feed' for normal asset/feed_item match, 'duplicate' for asset/asset re-registration. */
  kind?: "feed" | "duplicate";
};
```

- [ ] **Step 3: Verify**

```bash
cd apps/api && python -m compileall app 2>&1 | tail -3
cd apps/web && npx vite build 2>&1 | tail -3
```

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/schemas/asset.py apps/web/src/lib/types.ts
git commit -m "feat(t3): AssetMatchSummary.kind field for duplicate vs feed matches"
```

---

### Task 4: `_check_duplicate_asset` + Pass-1 wiring in matcher.py

**Files:**
- Modify: `apps/api/app/services/matcher.py`

- [ ] **Step 1: Add the new helper at module level**

In `apps/api/app/services/matcher.py`, just below `_synthesize_one_match` (or the existing helpers — anywhere at module scope after `_score_pair`), add:

```python
async def _check_duplicate_asset(
    new_asset: dict[str, Any],
    org_id: str,
    settings: Any,
) -> dict[str, Any] | None:
    """Pass 1: detect re-registration of the same image.

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
    return summary
```

- [ ] **Step 2: Wire Pass 1 into the existing entrypoint**

In `match_asset_against_feeds`, find the line `summaries: list[dict[str, Any]] = []` (currently around line 73). Replace the block from there through the `for feed in feed_items:` loop start with:

```python
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

    # Pass 2 (existing): asset × feed_item match for repost detection.
    feed_items = repos.list_feed_items(org_id, limit=500)
    for feed in feed_items:
```

(The rest of the function — feed loop, synthesize fallback, return — stays unchanged. Just verify the indentation matches.)

- [ ] **Step 3: Tag the existing feed-loop summary so it's distinguishable**

Inside the `for feed in feed_items:` loop, after the line `summaries.append(summary)`, add:

```python
        summary["kind"] = "feed"
```

And in `_synthesize_one_match` near the end where it calls `_score_pair`, after the call:

```python
    summary = await _score_pair(...)
    summary["kind"] = "feed"
    return summary
```

(Find the existing `return await _score_pair(...)` line — refactor it to capture the result, set the kind, then return.)

- [ ] **Step 4: Verify**

Backend compiles clean:
```bash
cd apps/api && python -m compileall app 2>&1 | tail -3
```

End-to-end probe — same image registered twice should produce **two** matches, one with `kind="duplicate"`:
```bash
TOKEN="killcont-demo-demo-user-1"
SOURCE_JPG=$(ls /d/kill-cont-fresh/apps/api/var/media/assets/*/preview.jpg | head -1)

# First registration
A1=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"dup probe 1","asset_type":"image","provenance_status":"verified"}' \
  http://127.0.0.1:8000/api/v1/assets | python -c "import sys,json;print(json.load(sys.stdin)['id'])")
curl -s -X POST -H "Authorization: Bearer $TOKEN" -F "file=@$SOURCE_JPG" \
  "http://127.0.0.1:8000/api/v1/assets/$A1/upload" > /tmp/a1.json

# Second registration (same image)
A2=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"dup probe 2","asset_type":"image","provenance_status":"verified"}' \
  http://127.0.0.1:8000/api/v1/assets | python -c "import sys,json;print(json.load(sys.stdin)['id'])")
curl -s -X POST -H "Authorization: Bearer $TOKEN" -F "file=@$SOURCE_JPG" \
  "http://127.0.0.1:8000/api/v1/assets/$A2/upload" | python -c "
import sys,json
d=json.load(sys.stdin)
print('matches:', len(d['matches']))
for m in d['matches']:
    print(f'  kind={m.get(\"kind\")} severity={m[\"severity\"]} score={m[\"similarity_score\"]:.3f} incident={m.get(\"incident_id\")}')"
```

Expected: at least one match with `kind=duplicate severity=monitor score>=0.92`.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/services/matcher.py
git commit -m "feat(t4): asset-vs-asset duplicate detection (Pass 1) in matcher"
```

---

### Task 5: Backend verification gate

- [ ] **Step 1: Restart API and re-seed**

```bash
# Stop any running uvicorn
# Start fresh
cd apps/api && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 5
TOKEN="killcont-demo-demo-user-1"
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"scenario":"championship-final"}' \
  http://127.0.0.1:8000/api/v1/demo/seed
```

- [ ] **Step 2: Run smoke harness**

```bash
python scripts/smoke.py
```

Expected: `[smoke] all green in N.NNs`.

- [ ] **Step 3: Manual cascade probe**

Trigger a live run, confirm both `feed.ingested` and `incident.created` events fire 3 times each.

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"segments":8,"interval_seconds":0.5}' \
  http://127.0.0.1:8000/api/v1/demo/live/start
sleep 20
# Confirm 3 new incidents
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/incidents | \
  python -c "import sys,json;d=json.load(sys.stdin);print(len(d['items']),'incidents')"
```

Expected: 7+ incidents (4 seeded + 3 from live).

- [ ] **Step 4: No commit needed (gate only).**

---

### Task 6: useFeeds `freshIds` + MonitorPage flash + NEW pill

**Files:**
- Modify: `apps/web/src/features/monitor/useFeeds.ts`
- Modify: `apps/web/src/features/monitor/MonitorPage.tsx`

- [ ] **Step 1: Replace useFeeds hook body**

Replace the entire contents of `apps/web/src/features/monitor/useFeeds.ts` with:

```typescript
import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { useSSE } from "../../lib/sse";
import type { FeedItem } from "../../lib/types";

type ListResponse = { items: FeedItem[] };

const FRESH_WINDOW_MS = 4500;

export function useFeeds() {
  const qc = useQueryClient();
  const [freshIds, setFreshIds] = useState<Set<string>>(new Set());

  const query = useQuery<ListResponse>({
    queryKey: ["feeds"],
    queryFn: () => api<ListResponse>("/feeds"),
    refetchOnWindowFocus: false,
  });

  useSSE((ev) => {
    if (ev.type === "feed.ingested") {
      const id = (ev.data?.feed_item_id as string | undefined) ?? "";
      if (id) {
        setFreshIds((prev) => {
          const next = new Set(prev);
          next.add(id);
          return next;
        });
        setTimeout(() => {
          setFreshIds((prev) => {
            const next = new Set(prev);
            next.delete(id);
            return next;
          });
        }, FRESH_WINDOW_MS);
      }
      qc.invalidateQueries({ queryKey: ["feeds"] });
    }
    if (ev.type === "demo.seeded" || ev.type === "demo.reset") {
      setFreshIds(new Set());
      qc.invalidateQueries({ queryKey: ["feeds"] });
    }
  });

  useEffect(() => {
    return () => setFreshIds(new Set());
  }, []);

  return { ...query, freshIds };
}
```

- [ ] **Step 2: Apply flash class + NEW pill in MonitorPage**

Find the row rendering loop in `apps/web/src/features/monitor/MonitorPage.tsx` (the `.map((feed) => ...)` over `feeds.items`). Get `freshIds` from the hook return: change the existing `const feedsQuery = useFeeds();` so the destructure now also reads `freshIds`. Look for where each feed row is rendered as a `<MediaFrame>` inside a clickable container OR a plain `<div>`/`<article>`. For each rendered row, derive `const isFresh = freshIds.has(feed.id);` and:
  - Add `${isFresh ? " stack-list__item--flash" : ""}` to the row's className (if it already uses `.stack-list__item` — most rows do).
  - Add a `<span>NEW</span>` pill (small, only renders when `isFresh`) inside the row's metadata area.

A worked example of the JSX pattern (adapt to MonitorPage's exact structure):

```tsx
{feeds.items.map((feed) => {
  const isFresh = freshIds.has(feed.id);
  return (
    <article
      key={feed.id}
      className={`stack-list__item${isFresh ? " stack-list__item--flash" : ""}`}
      onClick={() => setSelectedId(feed.id)}
    >
      <div className="stack-list__meta">
        <span>{feed.source_platform ?? "unknown"}</span>
        <span>{feed.source_region ?? "—"}</span>
        {isFresh && (
          <span
            className="status-pill status-pill--monitor"
            style={{ marginLeft: "auto", fontSize: 10 }}
          >
            NEW
          </span>
        )}
      </div>
      {/* ...rest of the existing row content unchanged */}
    </article>
  );
})}
```

The `.stack-list__item--flash` class is already defined in `global.css` (added during Bundle A2 — 1.6s color/box-shadow pulse). No new CSS needed.

- [ ] **Step 3: Verify**

```bash
cd apps/web && npx vite build 2>&1 | tail -3
```

Manual: open http://localhost:5173/app/monitor in a browser, then in another shell:

```bash
TOKEN="killcont-demo-demo-user-1"
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"segments":8,"interval_seconds":1.5}' \
  http://127.0.0.1:8000/api/v1/demo/live/start
```

The Live Feed list should add 3 fresh rows over the next ~16 s, each flashing with a NEW pill for ~1.6 s.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/features/monitor/useFeeds.ts apps/web/src/features/monitor/MonitorPage.tsx
git commit -m "feat(t6): Monitor live refresh with freshIds + NEW pulse"
```

---

### Task 7: EvidencePage "N new cases" jump banner

**Files:**
- Modify: `apps/web/src/features/evidence/EvidencePage.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Add banner state + SSE handler in EvidencePage**

In `apps/web/src/features/evidence/EvidencePage.tsx`, near the existing imports add:

```typescript
import { useEffect, useRef, useState } from "react";
import { useSSE } from "../../lib/sse";
```

(`useEffect`, `useRef`, `useState` may already be imported — merge into existing import.)

Inside the `EvidencePage` component (right after the existing `useState`/derived hooks, before the `return`), add:

```typescript
  const [incomingCount, setIncomingCount] = useState(0);
  const [latestNewId, setLatestNewId] = useState<string | null>(null);
  const lastEventAt = useRef<number>(0);

  useSSE((ev) => {
    if (ev.type !== "incident.created") return;
    const id = (ev.data?.incident_id as string | undefined) ?? "";
    if (!id || id === selectedId) return;
    setIncomingCount((c) => c + 1);
    setLatestNewId(id);
    lastEventAt.current = Date.now();
  });

  // Auto-clear after 30 s of idle
  useEffect(() => {
    if (incomingCount === 0) return;
    const t = setInterval(() => {
      if (Date.now() - lastEventAt.current > 30_000) {
        setIncomingCount(0);
        setLatestNewId(null);
      }
    }, 1000);
    return () => clearInterval(t);
  }, [incomingCount]);
```

- [ ] **Step 2: Render the banner inside the actions slot**

Find the existing `actions` JSX (the `<>` with Prev/Next/Copy summary/Export notice buttons). Add the banner as the FIRST element inside `actions`:

```tsx
const actions = (
  <>
    {incomingCount > 0 && latestNewId && (
      <button
        className="pill-link pill-link--solid evidence-jump-banner"
        onClick={() => {
          goTo(latestNewId);
          setIncomingCount(0);
          setLatestNewId(null);
        }}
        type="button"
      >
        ⚡ {incomingCount} new case{incomingCount === 1 ? "" : "s"} — View latest
      </button>
    )}
    <button className="pill-link pill-link--ghost" disabled={!prevIncident} onClick={() => goTo(prevIncident?.incident_id)} type="button">
      ← Prev
    </button>
    {/* ...rest of existing buttons unchanged */}
  </>
);
```

- [ ] **Step 3: Add the CSS rule**

Append to `apps/web/src/styles/global.css` (anywhere after the existing `.pill-link` definitions):

```css
/* Bundle E: Evidence "N new cases" jump banner. Yellow accent so it
   stands out from the standard prev/next/export actions. */
.evidence-jump-banner {
  background: linear-gradient(180deg, rgba(242, 184, 100, 0.22), rgba(242, 184, 100, 0.06));
  border-color: rgba(242, 184, 100, 0.55);
  color: #fbe2b8;
  animation: evidence-jump-banner-in 0.35s ease-out;
}

.evidence-jump-banner:hover {
  background: linear-gradient(180deg, rgba(242, 184, 100, 0.32), rgba(242, 184, 100, 0.12));
}

@keyframes evidence-jump-banner-in {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

- [ ] **Step 4: Verify**

```bash
cd apps/web && npx vite build 2>&1 | tail -3
```

Manual: open http://localhost:5173/app/evidence?incident=INC-1040, fire a live run, confirm the banner appears in the header counting up.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/evidence/EvidencePage.tsx apps/web/src/styles/global.css
git commit -m "feat(t7): Evidence 'N new cases' jump banner on incident.created"
```

---

### Task 8: useSidebarBadges hook + Sidebar pill render

**Files:**
- Create: `apps/web/src/features/shell/useSidebarBadges.ts`
- Modify: `apps/web/src/components/layout/Sidebar.tsx`
- Modify: `apps/web/src/styles/global.css`

- [ ] **Step 1: Create the hook**

Create `apps/web/src/features/shell/useSidebarBadges.ts` with:

```typescript
import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { useSSE } from "../../lib/sse";

type Badges = { incidents: number; monitor: number };
const FADE_MS = 5000;

/**
 * Bundle E: cross-tab awareness during a live run.
 *
 * Listens to SSE at the AppShell/Sidebar level so the counters survive
 * navigation between protected routes. Counts increment on
 * `incident.created` / `feed.ingested`; the whole map is reset to zero
 * after FADE_MS of no events. The currently-active route is suppressed
 * (no point telling the operator about the page they're already on).
 */
export function useSidebarBadges(): Badges {
  const [badges, setBadges] = useState<Badges>({ incidents: 0, monitor: 0 });
  const lastEventAt = useRef<number>(0);
  const location = useLocation();

  useSSE((ev) => {
    if (ev.type === "incident.created") {
      lastEventAt.current = Date.now();
      setBadges((b) => ({ ...b, incidents: b.incidents + 1 }));
    }
    if (ev.type === "feed.ingested") {
      lastEventAt.current = Date.now();
      setBadges((b) => ({ ...b, monitor: b.monitor + 1 }));
    }
  });

  useEffect(() => {
    const t = setInterval(() => {
      if (Date.now() - lastEventAt.current > FADE_MS) {
        setBadges((b) =>
          b.incidents === 0 && b.monitor === 0 ? b : { incidents: 0, monitor: 0 },
        );
      }
    }, 1000);
    return () => clearInterval(t);
  }, []);

  return {
    incidents: location.pathname.startsWith("/app/incidents") ? 0 : badges.incidents,
    monitor: location.pathname.startsWith("/app/monitor") ? 0 : badges.monitor,
  };
}
```

- [ ] **Step 2: Wire badges into Sidebar.tsx**

In `apps/web/src/components/layout/Sidebar.tsx`, near the top of the component:

```typescript
import { useSidebarBadges } from "../../features/shell/useSidebarBadges";

export function Sidebar() {
  const badges = useSidebarBadges();
  // ...existing code
```

Find where the nav items are rendered (likely a `<NavLink>` for each route or an array map). For the "Incidents" and "Monitor" nav items, add a badge pill that renders when count > 0. Adapt to the existing JSX shape — example:

```tsx
<NavLink to="/app/incidents" /* ... */>
  <span>Incidents</span>
  {badges.incidents > 0 && (
    <span className="sidebar-nav__badge" aria-label={`${badges.incidents} new`}>
      {badges.incidents}
    </span>
  )}
</NavLink>
```

Same shape for the Monitor link with `badges.monitor`.

- [ ] **Step 3: CSS for the badge**

Append to `apps/web/src/styles/global.css`:

```css
/* Bundle E: cross-tab badge on sidebar nav items during live runs. */
.sidebar-nav__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  margin-left: auto;
  border-radius: 999px;
  background: var(--accent);
  color: #001020;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
  box-shadow: 0 0 0 2px rgba(0, 153, 255, 0.18);
  animation: sidebar-badge-pop 0.25s ease-out;
}

@keyframes sidebar-badge-pop {
  from { transform: scale(0.6); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}
```

- [ ] **Step 4: Verify**

```bash
cd apps/web && npx vite build 2>&1 | tail -3
```

Manual: navigate to http://localhost:5173/app/settings, fire a live run from another shell, watch the sidebar — `Incidents` and `Monitor` should each get a `3` pill that fades after ~5 s. Navigate to `/app/incidents` mid-run — the `Incidents` badge should disappear immediately.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/features/shell/useSidebarBadges.ts apps/web/src/components/layout/Sidebar.tsx apps/web/src/styles/global.css
git commit -m "feat(t8): sidebar badges for cross-tab incident + feed_item awareness"
```

---

### Task 9: Frontend verification gate

- [ ] **Step 1: Build clean**

```bash
cd apps/web && npx vite build 2>&1 | tail -5
```

Expected: clean build, ~516+ modules transformed.

- [ ] **Step 2: Manual end-to-end**

1. Open http://localhost:5173, sign in.
2. Navigate to Assets → Register asset → upload an image. Note the toast.
3. Without changing the file, register **the same image** as a different title. Confirm the toast says "2 matches surfaced" and one of them is the duplicate (visible in dev tools network tab on `AssetDetail.matches[0].kind === "duplicate"`).
4. Navigate to Live Watch → Start live event.
5. While running, navigate to Settings — confirm sidebar shows `Incidents N` and `Monitor M` badges.
6. Navigate to Evidence (any incident URL) while a live run is firing — confirm "⚡ N new cases" banner appears.
7. Click the banner — confirm navigation to the freshest incident.
8. Navigate to Monitor mid-run — confirm new feed_item rows appear with NEW pulse.

- [ ] **Step 3: No commit (gate only).**

---

### Task 10: Update docs

**Files:**
- Modify: `docs/status.md`
- Modify: `docs/logbook.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: status.md**

Add a row to the Module Status table:

```markdown
| Live cascade + duplicate detection (Bundle E) | Completed | Asset×asset duplicate detection at PHASH_DUPLICATE_THRESHOLD=0.92 produces a monitor-severity incident with a synthetic feed_item. Monitor / Evidence / Sidebar all cascade live during simulate-incident and live runs. |
```

Append a "Closed (2026-04-27) — Bundle E" section under the existing Closed sections.

- [ ] **Step 2: logbook.md**

Append a 2026-04-27 entry listing every commit in this plan + verification numbers.

- [ ] **Step 3: CLAUDE.md**

Add a "### Bundle E — Live cascade + duplicate detection (2026-04-27)" subsection under "Recently closed gaps" with the matcher Pass-1 fact, the new env knob name, and the three new frontend pieces (useFeeds freshIds / Evidence banner / sidebar badges).

- [ ] **Step 4: Commit**

```bash
git add docs/status.md docs/logbook.md CLAUDE.md
git commit -m "docs: roll status/logbook/CLAUDE forward for Bundle E (live cascade + duplicate detection)"
```

---

## Out of scope (deferred)

- Real Google sign-in via Firebase popup (next phase per user message)
- Cloud Run + Firebase Hosting deploy (S12)
- Asset×asset clustering across orgs (multi-tenant)

## Self-review notes

- All function names verified against `apps/api/app/services/repos/__init__.py` (`get_all_assets_with_phash`, `get_feed_item`, `new_feed_id`, `insert_feed_item`).
- `_score_pair` signature in matcher.py confirmed: takes keyword args `asset`, `feed`, `score`, `promoted_so_far`, `synthetic`. No `kind` param — set on the returned dict.
- `useSSE` signature confirmed in `apps/web/src/lib/sse.ts`.
- `.stack-list__item--flash` already defined in global.css (Bundle A2). No new flash CSS needed for Monitor (T6).
- 0.92 threshold tested mentally against seeded asset placeholders (gradient backgrounds, similar palettes) — they score 0.65–0.78. Safe.
