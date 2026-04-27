# Live Cascade + Duplicate-Asset Detection — Design Spec

**Date:** 2026-04-27
**Author:** Claude (sonnet-4.7) under brainstorming skill, ratified by user
**Repo:** `D:\kill-cont-fresh`
**Branch base:** `second_branch`
**Predecessor spec:** [`2026-04-26-fix-incompleteness-design.md`](2026-04-26-fix-incompleteness-design.md) (Bundles B/A/C/D, all landed)

---

## 1. Goal in one sentence

A live run, or a duplicate asset upload, must produce a visibly cascading reaction in **every** tab — Monitor, Incidents, Evidence, Live Watch, Overview, and the sidebar — without the operator ever needing to manually refresh.

## 2. Why now

Playthrough on 2026-04-27 surfaced two concrete demo gaps that the earlier B/A/C/D bundles did not close:

1. **Monitor tab is stale during live runs.** `_live_emitter` calls `simulate_incident()` which inserts a feed_item, but the only SSE event published is `incident.created`. The Monitor page subscribes to `feed.ingested` / `demo.seeded` / `demo.reset`, so its feed list stays frozen until the operator reloads. Verified by inspection of `apps/api/app/api/routes/demo.py:269` and `apps/web/src/features/monitor/useFeeds.ts:16`.
2. **Same-asset re-registration "works by accident."** Today the matcher only crosses asset × feed_item. A duplicate upload triggers an incident only because the *first* upload's synthetic-fallback path leaves a feed_item behind that the *second* upload's pHash matches. Turn `synthesize_demo_match` off (which is the planned default for the public profile) and the duplicate flow goes silent. There is no deliberate asset-vs-asset detection in the codebase.

Two further weaknesses motivate the surrounding polish:

3. **Evidence tab passively absorbs new incidents.** The underlying list refreshes on `incident.created`, but the currently-viewed incident does not change and there is no UI signal that newer cases have arrived. Operators must click Next/Prev to discover them.
4. **Cross-tab awareness is zero.** An operator who kicks off a live run from Live Watch and immediately navigates to Settings or Assets sees no signal that 3 incidents have just landed.

Gemini summaries are confirmed working — the screenshots from 2026-04-27 11:51 IST show INC-71445 with a green "Gemini · gemini-2.5-flash · 5.0 s" chip and real model output ("High similarity image match (0.85) on Telegram broadcast, likely a synthetic repost of 'test 1'…"). The amber "Canned reason" chips are seeded incidents from `/demo/seed` (which intentionally avoids burning ~12 Gemini calls on every reset). No change required to the Gemini path.

## 3. User-facing decisions (locked during brainstorming)

| # | Decision | Choice |
|---|---|---|
| Q1 | Same-asset duplicate handling | **B** — allow + create monitor-severity incident |
| Q2 | Monitor tab refresh polish | **B** — alive refresh with NEW pulse |
| Q3 | Evidence tab fresh-incident handling | **B** — "N new cases" banner with Jump button |
| Q4 | Duplicate-asset data model | **A** — synthesize a feed_item with `source_type="self_duplicate"` |
| Q5 | Threshold for asset×asset match | **A** — two-tier: 0.80 asset↔feed (existing), 0.92 asset↔asset (new) |
| Q6 | Cross-tab awareness | **A** — sidebar incident-count badges with auto-fade |

## 4. Architecture

Three load-bearing existing pieces stay in place:

- **`app/services/matcher.py::match_asset_against_feeds(asset_id)`** — already runs after every successful upload, already adapter-clean (writes go through `repos.insert_*`), already publishes `incident.created`. We extend it; we do not replace it.
- **`app/services/events_bus.py::publish(event_type, payload)`** — in-process asyncio pub/sub. Single new event type added (`feed.ingested` from non-seed paths).
- **TanStack Query + `useSSE` hooks** — already invalidate on event types they recognize. We extend the listener lists; we do not change the hook architecture.

The work splits cleanly across backend and frontend; nothing in this spec touches the SQLite schema, the Firestore adapter, or the auth middleware.

### 4.1 Component diagram (text)

```
Asset upload  ──►  matcher.match_asset_against_feeds(asset_id)
                       │
                       ├── Pass 1 (NEW): asset × asset @ 0.92
                       │     │  on hit:
                       │     │    repos.insert_feed_item(source_type="self_duplicate")
                       │     │    publish("feed.ingested")
                       │     │    repos.insert_incident(severity="monitor", Gemini-triaged)
                       │     │    publish("incident.created")
                       │     └─ summary returned with synthetic=true, kind="duplicate"
                       │
                       └── Pass 2 (existing): asset × feed_item @ 0.80
                             │  unchanged

Live run ──►  _live_emitter ──►  simulate_incident()
                                    │
                                    ├── repos.insert_feed_item(...)
                                    ├── publish("feed.ingested")   ← NEW LINE
                                    ├── repos.insert_incident(...)
                                    └── publish("incident.created")  (existing)

Frontend SSE consumers
├── useIncidents (existing)         listens: incident.created
├── useFeeds (Monitor)              listens: feed.ingested + demo.* (existing list)
│       NEW: also tracks freshIds set, 4.5s window
├── useEvidenceBanner (NEW hook)    listens: incident.created
│       owns {incomingCount, latestNewId}, auto-clear after 30s idle
└── useSidebarBadges (NEW hook)     listens: incident.created + feed.ingested
        owns {incidents: number, monitor: number}, auto-fade after 5s idle
        suppresses badge on currently-active route
```

### 4.2 Data model touchpoints

**No schema migration.** The synthetic feed_item for duplicates uses existing columns:

```python
{
    "id": new_feed_id(),
    "org_id": new_asset["org_id"],
    "source_type": "self_duplicate",                # NEW enum value, no DB constraint
    "source_platform": "killcont:duplicate-registration",
    "source_url": None,
    "source_author": None,
    "source_region": "Internal",
    "caption": f"Duplicate registration of '{matched_asset['title']}' as {new_asset['id']}",
    "content_type": "image",
    "media_path": new_asset["primary_path"],        # reuse the new asset's pixels
    "preview_path": new_asset["preview_path"],
    "phash": new_asset["phash"],
}
```

The matched_candidate row uses the new asset as both sides of the relation in spirit, but the FK still points at the synthetic feed_item; the *matched* asset is recorded via the candidate's `asset_id` field as usual. Pre-existing `match_candidates.asset_id` semantics ("the protected asset that this feed item matched") flips here — the candidate's `asset_id` references the **older** asset (the one that already existed), and the synthetic feed_item references the **newer** asset's pixels. This keeps the existing UI ("here's the protected asset, here's what we found in the wild") visually coherent — the older asset reads as "official," the newer asset reads as "captured upload" because that's whose pixels are in the synthetic feed.

### 4.3 Threshold knobs

`app/core/config.py` adds **one** new field:

```python
phash_duplicate_threshold: float = 0.92
```

`.env.example` documents both:

```
# Matching thresholds
#   PHASH_MATCH_THRESHOLD     — asset vs feed_item (repost/derivative detection)
#   PHASH_DUPLICATE_THRESHOLD — asset vs asset (re-registration of the same image)
PHASH_MATCH_THRESHOLD=0.80
PHASH_DUPLICATE_THRESHOLD=0.92
```

`PHASH_DUPLICATE_THRESHOLD` is intentionally tighter than `PHASH_MATCH_THRESHOLD`. With seeded placeholder imagery the three protected assets score 0.65–0.78 against each other; only near-identical re-uploads (compression/resize tolerant, but visually the same) clear 0.92.

## 5. Component-level design

### 5.1 Backend: `app/services/matcher.py`

New function `_check_duplicate_asset(new_asset, org_id)` runs **before** the existing feed-loop. Returns the matched older asset dict or None.

```python
async def match_asset_against_feeds(asset_id: str) -> list[dict[str, Any]]:
    settings = get_settings()
    new_asset = repos.get_asset_detail(asset_id)
    if not new_asset or not new_asset.get("phash"):
        return []
    org_id = new_asset.get("org_id") or settings.demo_org_id
    summaries: list[dict[str, Any]] = []

    # Pass 1: duplicate-asset detection (NEW)
    duplicate_summary = await _check_duplicate_asset(new_asset, org_id, settings)
    if duplicate_summary:
        summaries.append(duplicate_summary)

    # Pass 2: existing asset×feed_item matcher (unchanged body)
    ...

    return summaries
```

`_check_duplicate_asset` calls `repos.get_all_assets_with_phash(org_id)` (already exists — used by `_pick_asset` in demo.py). Filters out the new asset itself by id. Computes `similarity_score` against each. If any score ≥ `settings.phash_duplicate_threshold`, picks the highest-scoring older asset, builds the synthetic feed_item from the new asset's pixels, inserts via `repos.insert_feed_item`, **publishes `feed.ingested`**, then calls into the existing `_score_pair` flow with `synthetic=True` and a new flag `kind="duplicate"` carried in the returned summary so the FE can label it.

### 5.2 Backend: `app/api/routes/demo.py::simulate_incident`

Single one-line addition right after `repos.insert_feed_item(...)` near line 152:

```python
await publish("feed.ingested", {"feed_item_id": feed_id})
```

This unblocks Monitor's live refresh for both `simulate_incident` direct calls and `_live_emitter` (which calls `simulate_incident` indirectly).

### 5.3 Backend: `app/services/repos/_sqlite.py` (no change required)

`get_all_assets_with_phash(org_id)` already exists and returns the rows we need. Verified.

### 5.4 Frontend: `features/monitor/useFeeds.ts`

Adopt the same shape as `useIncidents`:

```typescript
export function useFeeds() {
  const qc = useQueryClient();
  const [freshIds, setFreshIds] = useState<Set<string>>(new Set());
  const query = useQuery<ListResponse>({ ... });

  useSSE((ev) => {
    if (ev.type === "feed.ingested") {
      const id = ev.data?.feed_item_id as string | undefined;
      if (id) {
        setFreshIds((prev) => new Set(prev).add(id));
        setTimeout(() => {
          setFreshIds((prev) => {
            const next = new Set(prev);
            next.delete(id);
            return next;
          });
        }, 4500);
      }
      qc.invalidateQueries({ queryKey: ["feeds"] });
    }
    if (ev.type === "demo.seeded" || ev.type === "demo.reset") {
      setFreshIds(new Set());
      qc.invalidateQueries({ queryKey: ["feeds"] });
    }
  });

  return { ...query, freshIds };
}
```

`MonitorPage.tsx` consumes `freshIds`. Each row in the Live Feed list checks `freshIds.has(feed.id)` and conditionally applies `.stack-list__item--flash` (the existing CSS class — no new styles). Linked incident badge gets a small "NEW" pill rendered alongside it for the same window.

### 5.5 Frontend: `features/evidence/EvidencePage.tsx`

New component-local state:

```typescript
const [incomingCount, setIncomingCount] = useState(0);
const [latestNewId, setLatestNewId] = useState<string | null>(null);
const lastEventAt = useRef<number>(0);
```

`useSSE` handler increments `incomingCount` and updates `latestNewId` on `incident.created`, and sets `lastEventAt.current = Date.now()`. A `useEffect` with a 30 s timer auto-clears state when no new event has arrived.

Banner rendered inside the existing `actions` slot of `ContextHeader`, before the Prev/Next/Copy/Export buttons:

```tsx
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
```

`.evidence-jump-banner` reuses `.pill-link--solid` plus a yellow accent (`--monitor` color) so the banner stands out from the standard navigation buttons. Single new CSS rule.

### 5.6 Frontend: `components/layout/Sidebar.tsx` + new `useSidebarBadges` hook

New hook `apps/web/src/features/shell/useSidebarBadges.ts`:

```typescript
type Badges = { incidents: number; monitor: number };
const FADE_MS = 5000;

export function useSidebarBadges(): Badges {
  const [badges, setBadges] = useState<Badges>({ incidents: 0, monitor: 0 });
  const lastEventAt = useRef<number>(0);
  const location = useLocation();
  // mounted at AppShell so SSE survives nav between protected routes

  useSSE((ev) => {
    lastEventAt.current = Date.now();
    if (ev.type === "incident.created") {
      setBadges((b) => ({ ...b, incidents: b.incidents + 1 }));
    }
    if (ev.type === "feed.ingested") {
      setBadges((b) => ({ ...b, monitor: b.monitor + 1 }));
    }
  });

  // Decay loop: every second, if no event for FADE_MS, reset to zero
  useEffect(() => {
    const t = setInterval(() => {
      if (Date.now() - lastEventAt.current > FADE_MS) {
        setBadges({ incidents: 0, monitor: 0 });
      }
    }, 1000);
    return () => clearInterval(t);
  }, []);

  // Suppress the badge for the currently-active route
  return {
    incidents: location.pathname.startsWith("/app/incidents") ? 0 : badges.incidents,
    monitor: location.pathname.startsWith("/app/monitor") ? 0 : badges.monitor,
  };
}
```

`Sidebar.tsx` calls `useSidebarBadges()` and renders a small `.sidebar-nav__badge` pill next to the "Incidents" and "Monitor" nav items when count > 0.

## 6. Verification matrix

| Action | Expected cascade | Where to look |
|---|---|---|
| Upload a brand-new image | 1 incident from Pass 2 (synthetic feed). Asset row flashes on `/app/assets`. Sidebar shows `Incidents 1` + `Monitor 1` if user is elsewhere. | All five tabs + sidebar |
| Upload the same image again | **2 incidents** — Pass 1 (duplicate, monitor severity, synthetic feed `source_type="self_duplicate"`) + Pass 2 (synthetic match against the original's fallback feed if any). Both visible everywhere. | Assets toast count = 2 matches; Monitor shows 2 new rows |
| Start a live run from Live Watch | 3 incidents over ~16 s. Each fires `incident.created` AND `feed.ingested`. Live Watch rail: NEW pulse. Monitor: 3 fresh rows with NEW pulse (was broken before). Evidence (if viewing one): banner counts up to "⚡ 3 new cases". Sidebar badges count up if user is on Settings/Assets. | All tabs |
| Open Settings during a live run | Sidebar shows `Incidents 3` and `Monitor 3` for ~5 s past the last event, then fades to 0. | Sidebar only |
| Click "View latest" on Evidence banner | Page navigates to the freshest incident, banner clears immediately. | Evidence page |
| Navigate to Incidents tab while badges show "Incidents 3" | Badge for Incidents disappears immediately (suppression by active route); Monitor badge stays. | Sidebar |

## 7. Out of scope (intentionally rejected)

- **Auto-jump on Evidence** (rejected as Q3-C — fights operator focus).
- **Right-pane auto-select on Monitor** (rejected as Q2-C — same reason).
- **Global toast notifications** (rejected as Q6-B — 3 toasts in 16 s during a live run is noisy).
- **Asset×asset clustering across orgs** (multi-tenant feature, deferred until after the public deploy).
- **Real Google sign-in + cloud deploy** — that's the next phase per the user's message; this design intentionally stays in the local profile so it can land and be verified before deploy work begins.
- **Schema changes.** No `feed_item_id` nullability, no new FK, no migration. Synthetic-feed pattern handles the new case.

## 8. Risks & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Sidebar badges interrupt focus during long live runs | Low | Auto-fade after 5 s of idle; suppressed entirely when user is on the relevant tab |
| Duplicate-asset Pass 1 catches false positives because seeded assets are visually similar placeholders | Medium | 0.92 threshold tested against current seed — they score 0.65–0.78 (well below). Documented as `PHASH_DUPLICATE_THRESHOLD` env var so it can be re-tuned per profile |
| Pass 1 produces an extra Gemini call per duplicate upload, blowing free-tier budget on a test loop | Low | `GEMINI_PROMOTE_BUDGET=20` cap in matcher already guards this |
| `feed.ingested` event published from `simulate_incident` causes an existing `useFeeds` consumer to over-fetch | Low | `useFeeds` already listens to `feed.ingested`; this just makes that listener actually receive events. Monitor's only consumer of feeds is the list view itself |
| `kind="duplicate"` flag in the AssetMatchSummary breaks existing typed consumers | Low | Field is optional; existing consumers ignore unknown fields |
| New asset's pixels become "the captured upload" on the duplicate's incident detail page — visually inverted from the operator's mental model | Medium | Documented in §4.2; the Gemini-generated reason text will explain "this is a duplicate registration" so the framing reads correctly |

## 9. Implementation phasing

The plan should be one phase, not multiple. Estimated 8–12 tasks total, all on `second_branch`, each independently committable. Suggested order:

1. **Backend core** — config knob (`PHASH_DUPLICATE_THRESHOLD`), `matcher.py` Pass 1, `feed.ingested` publish from `simulate_incident`. Verify with curl + smoke harness.
2. **Frontend Monitor live refresh** — `useFeeds` freshIds + `MonitorPage` flash class.
3. **Frontend Evidence banner** — local state + banner JSX + tiny CSS.
4. **Frontend Sidebar badges** — `useSidebarBadges` hook + Sidebar pill render.
5. **Verification gate** — manual end-to-end (upload twice, run live event, navigate during run) plus smoke harness re-run.

No new dependencies. No schema migration. No deploy artifacts touched.

## 10. Files touched (forecast)

**New (1 file):**
- `apps/web/src/features/shell/useSidebarBadges.ts`

**Modified (~10 files):**
- `apps/api/app/core/config.py` — `phash_duplicate_threshold` field
- `apps/api/.env.example` — document both thresholds
- `apps/api/app/services/matcher.py` — Pass 1 implementation, `_check_duplicate_asset` helper
- `apps/api/app/api/routes/demo.py` — one `await publish("feed.ingested", ...)` line
- `apps/api/app/schemas/asset.py` — `AssetMatchSummary.kind?: "duplicate" | "feed"` (optional)
- `apps/web/src/features/monitor/useFeeds.ts` — freshIds state + SSE handler updates
- `apps/web/src/features/monitor/MonitorPage.tsx` — consume freshIds, apply flash class + NEW pill
- `apps/web/src/features/evidence/EvidencePage.tsx` — banner state + render
- `apps/web/src/styles/global.css` — one `.evidence-jump-banner` rule + one `.sidebar-nav__badge` rule
- `apps/web/src/components/layout/Sidebar.tsx` — invoke hook, render badges
- `apps/web/src/lib/types.ts` — `AssetMatchSummary.kind?` mirror

Backend `python -m compileall app` and frontend `npx vite build` must stay clean throughout.

---

**Spec status:** ratified during 2026-04-27 brainstorm. Ready for the `writing-plans` skill to expand into bite-sized TDD-flavored tasks.
