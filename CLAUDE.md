# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Snapshot

KillCont is a Google Solution Challenge hackathon entry: an operator-grade web console that detects reused sports media (images/clips) across the web. A FastAPI backend pairs with a React 19 + Vite frontend. The local-profile MVP runs end-to-end today with SQLite, local filesystem, demo bearer auth, and an in-process SSE bus. A public profile (Firestore + Cloud Storage + Firebase Auth) is being finished so the demo can be hosted on Google Cloud's Always-Free tier (Firebase Hosting + Cloud Run). An active construction plan lives at `C:\Users\Praneeth P\.claude\plans\zany-inventing-aho.md`.

## Repository Layout

```
apps/
  api/                FastAPI backend (Python 3.11+)
    app/
      api/routes/     HTTP routes (assets, feeds, incidents, dashboard, demo, events, session, health)
      core/config.py  Pydantic settings — profile/auth/backend switches
      services/       authn, db (SQLite), repos (queries), storage (media), events_bus (SSE), seeder, demo_data, similarity, triage
      schemas/        Pydantic response models
    requirements.txt
    var/              Local SQLite DB + /media/ uploads (gitignored)
  web/                React 19 + Vite 8 + TanStack Query
    src/
      app/            Router + shell (marketing vs protected product)
      features/       overview, assets, monitor, incidents, evidence, live-watch, settings, auth, demo, marketing
      lib/            api.ts (fetch wrapper), sse.ts, types.ts, mock-data.ts
docs/                 architecture, status, logbook, mindset, design-direction, website-blueprint, research-notes
infra/google-cloud/   Deploy stubs (Dockerfile, firebase.json, rules — to be filled)
packages/             contracts + design-system (stubs)
scripts/              One-off scripts (smoke harness, Firestore migrator — to be added)
graphify-out/         RAG index of the codebase (300 nodes, 472 edges, 61 communities)
```

## Common Commands

Backend (from `apps/api/`):
```
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m compileall app        # type-free compile check — stand-in for tests
```

Frontend (from `apps/web/`):
```
npm install
npm run dev                     # Vite dev server on :5173
npm run build                   # tsc -b && vite build
npm run preview                 # serve built dist/
```

Demo pipeline (against a running API on :8000 with a valid bearer token):
```
POST /api/v1/demo/seed
POST /api/v1/demo/simulate-incident
POST /api/v1/incidents/{id}/actions   (accept | reject | review)
POST /api/v1/demo/live/start          body: {segments, interval_seconds, asset_id?, platform?}
GET  /api/v1/dashboard/overview
GET  /api/v1/events/stream?token=<jwt>   (SSE)
GET  /api/v1/health/profile           (runtime profile + Gemini snapshot — DP10/DP12)
POST /api/v1/debug/test-gemini        body: {severity}; returns source/latency/reason — DP12
GET  /api/v1/incidents/{id}/notice    (Markdown takedown notice — DP6)
```

No test framework is configured — verification is `compileall` + `npm run build` + the manual demo sequence above. A `scripts/smoke.py` harness is planned (Step S6 of the active plan).

## Architecture (Big Picture)

**Dual runtime profiles, identical contracts.** `RUNTIME_PROFILE=local` uses SQLite (`apps/api/var/app.db`) and local filesystem; `RUNTIME_PROFILE=public` will use Firestore and Cloud Storage. Adapter seams live in `app/services/repos/` (`_sqlite.py` live, `_firestore.py` stub) and `app/services/storage/` (`_local.py` live, `_gcs.py` stub) — package `__init__.py` re-exports the active backend chosen by `app/services/profile.py::active_metadata_backend()` / `active_media_backend()`. Route handlers keep importing module-level functions — `from app.services import repos, storage` — never swap routes when changing backends. Image-processing helpers (`make_preview`, `derive_repost`, `generate_placeholder_image`, `make_frame_strip`) are storage-agnostic and live in `storage/_common.py`, re-exported regardless of adapter.

**Dual auth backends.** `AUTH_BACKEND=demo` issues bearer tokens shaped `killcont-demo-<userId>` and is validated locally. `AUTH_BACKEND=firebase` expects a Firebase ID token on `/session/login` (field `id_token`), verified with `firebase-admin`. The FastAPI middleware in `apps/api/app/main.py` enforces auth on every `/api/v1/*` path except `PUBLIC_PATHS` (login + health). EventSource can't set headers so SSE routes also accept `?token=` query-string.

**SSE realtime.** `app/services/events_bus.py` runs an in-process asyncio pub/sub with bounded (100-item) per-subscriber queues. Routes call `publish()` after state changes; the FE consumes via `lib/sse.ts` on protected pages. This is why serverless targets with a 10s function cap (Vercel, Lambda) are off-limits — Cloud Run's streaming is load-bearing.

**pHash-only matching.** `app/services/similarity.py` computes 64-bit perceptual hashes via the `imagehash` library. `PHASH_MATCH_THRESHOLD` (default 0.80) gates `match_candidates` rows. Vertex AI embeddings are explicitly out of scope (README working rule: no custom model training).

**SQLite schema (6 tables).** `organizations`, `users`, `assets`, `feed_items`, `match_candidates`, `incidents`, `actions` — see `app/services/db.py` `SCHEMA_SQL`. Firestore mirror (denormalized) is documented at `docs/architecture.md` lines 276–290.

**Frontend shell split.** `apps/web/src/app/router.tsx` splits the app into a public marketing shell (`/`, `/sign-in`) and a `ProtectedRoute`-gated product shell (`/app/overview`, `/app/assets`, `/app/monitor`, `/app/incidents`, `/app/evidence`, `/app/live-watch`, `/app/settings`). `lib/api.ts` injects the bearer token from `localStorage["killcont-token"]` on every request; `mediaUrl()` rewrites relative paths against `VITE_API_BASE_URL`.

**God nodes (treat as load-bearing).** From the graphify RAG index: `simulate_incident()` (25 edges, `routes/demo.py`), `get_conn()` (25, `services/db.py`), `ingest_feed()` (23, `routes/feeds.py`), `seed_championship_final()` (22, `services/seeder.py`), `get_settings()` (19, `core/config.py`), `upload_asset_media()` (11, `routes/assets.py`), `publish()` (10, `services/events_bus.py`).

## Working Rules (override defaults)

- **No CI/CD.** Explicit README rule. Deploys are manual (`gcloud run deploy`, `firebase deploy`).
- **No custom model training.** pHash is the matching ceiling for this hackathon.
- **Prefer GCP managed services** over self-hosted equivalents when complexity is equal.
- **Local profile is the offline demo fallback** — `RUNTIME_PROFILE=local + AUTH_BACKEND=demo` must never regress. Any cloud change gets a behavior-equivalence check against the local profile.
- **Update `docs/status.md` and `docs/logbook.md`** after every meaningful milestone.
- **No secrets in git.** `service-account.json`, `.env`, Firebase admin credentials — all gitignored. Firebase *web* config (`apiKey`, etc.) is public by design and safe to commit for a private repo.
- **Execution cadence on the active plan: stop after each major step.** Don't chain S0→S12 without approval.

## Key Environment Variables

**Backend (`apps/api/.env`)** — see `.env.example` for the full list:
- `RUNTIME_PROFILE` = `local` | `public`
- `AUTH_BACKEND` = `demo` | `firebase`
- `METADATA_BACKEND` = `sqlite` | `firestore`
- `MEDIA_BACKEND` = `local` | `gcs`
- `DB_PATH`, `MEDIA_DIR` (local profile)
- `ALLOWED_ORIGINS` (CSV), `PUBLIC_WEB_ORIGIN` (hosted FE URL)
- `PHASH_MATCH_THRESHOLD` (default 0.80)
- `DEMO_ORG_ID`, `DEMO_DEFAULT_USER_ID` (hard-coded demo tenant)
- `GEMINI_API_KEY` (optional — reason text generation)
- `GCP_PROJECT_ID`, `FIREBASE_PROJECT_ID`, `FIREBASE_STORAGE_BUCKET`, `FIREBASE_CREDENTIALS_PATH` (public profile)

**Frontend (`apps/web/.env` / `.env.production`)**:
- `VITE_API_BASE_URL` (default `http://localhost:8000/api/v1`)
- `VITE_AUTH_MODE` = `demo` | `firebase`
- `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, `VITE_FIREBASE_STORAGE_BUCKET`, `VITE_FIREBASE_MESSAGING_SENDER_ID`, `VITE_FIREBASE_APP_ID`
- `VITE_GOOGLE_MAPS_API_KEY` (threat map; page degrades to static placeholder when empty)

## Known Gaps (being closed by the active plan)

1. **S12 — first manual deploy.** All deploy artifacts are landed (Dockerfile, deploy-api.sh, firebase.json, deploy-web.sh) but `gcloud run deploy` + `firebase deploy` haven't been run yet against the live `killcont-demo` project. Once deployed, back-fill `PUBLIC_WEB_ORIGIN` + `ALLOWED_ORIGINS` on Cloud Run with the hosted FE URL and add the hosting domain to Firebase Auth → authorized domains.
2. `tsc -b` trips on a pre-existing `TS5103` toolchain warning during `npm run build`. `npx vite build` produces a fully working bundle (514 modules) and is what `deploy-web.sh` falls back to. Worth fixing the tsconfig flag separately.

## Recently closed gaps (Bundles B/A/C/D, DP1–DP15, S2–S11)

### Bundle B — On-upload matcher (2026-04-26)

- **The biggest visible win:** uploading a new asset now actually surfaces matches. `app/services/matcher.py::match_asset_against_feeds(asset_id)` runs at the end of `routes/assets.py::upload_asset_media`, scores the asset's pHash against every existing feed_item with a pHash, writes `match_candidate` rows, promotes strong matches to `incidents` (Gemini-triaged), and returns a list of `AssetMatchSummary` for the FE toast.
- If real-feed scoring comes up empty, the matcher synthesizes one derived feed-item from the asset's primary so the upload always produces at least one visible incident. Gated by `Settings.synthesize_demo_match=True` (off-able for public deploys).
- SQLite SCHEMA_SQL canonical table now carries `triage_source/triage_model/triage_latency_ms`, so `/demo/reset` no longer breaks `simulate_incident` writes.

### Bundle A — Asset upload form UX (2026-04-26)

- `AssetUploadModal`: autofocus title on open, inline validation (title required, file ≤ 25 MB, `image/*` mime), `aria-invalid` red ring + per-field error/hint copy. File input narrowed to `image/*`.
- `AssetsPage` consumes `AssetDetail.matches` from the mutation: `.upload-toast` above the table summarising "N matches surfaced · M incidents created", new row scrolls into view + flashes for 1.6 s, auto-clears after 8 s.

### Bundle C — Live Watch honest synthetic stream (2026-04-26)

- `_live_emitter` PROMOTING_STATUSES = {"Restream suspected", "Signal match"}. Both qualify a segment for incident promotion; `promotion_idx` rotates `SIMULATED_PLATFORMS` per fire so consecutive rail rows look distinct (piracy-mirror → youtube → reddit → ...).
- LiveWatch eyebrow + subtitle made honest about the simulation. Fresh-from-matcher rail rows clickable, render `incident.summary` 2-line clamped, "NEW" pill + flash on SSE `incident.created` for ~4.5 s.

### Bundle D — Gemini visibility (2026-04-26)

- New `apps/web/src/components/ui/TriageSourceChip.tsx`: pulse-dot chip ("Gemini · gemini-2.5-flash · 5.7 s" or "Canned reason"). Two sizes, full tooltip. Wired into IncidentsPage rows + selected-detail header, IncidentDetailPage hero, EvidencePage case-summary panel.
- `triage.py` lifetime `GEMINI_OK_COUNT`/`GEMINI_FALLBACK_COUNT` counters; `current_gemini_snapshot()` returns `{ok_count, fallback_count, total_count}`. `/health/profile.gemini` relays them; Settings → System Status shows a "Gemini activity: N live · M fallback · T total" row when any call has run.

### Earlier closed gaps (S2–S11, DP1–DP15)

### S3 — Firestore metadata adapter (2026-04-25)

- `app/services/repos/_firestore.py` implements every public function from the SQLite adapter against the Firebase Admin Firestore client. Lazy `_ensure_admin_app()` reuses any already-initialized firebase_admin app.
- Incident docs **denormalize** `asset_title`, `source_platform`, `source_region` at write time (so `list_incidents` is a single composite-indexed read with no joins). Numeric `severity_rank` field is added for indexed sorting.
- 4 new write helpers (`insert_asset`, `insert_feed_item`, `insert_match_candidate`, `insert_incident`) added to **both** adapters; `seeder.py` + `routes/demo.py::simulate_incident` refactored to use them — no remaining raw `get_conn()` writes outside `_sqlite.py`.
- `infra/google-cloud/firestore.indexes.json` ships composite indexes (incidents by `org_id`+`severity_rank`+`created_at` DESC and by `org_id`+`operator_status`+`created_at` DESC and by `org_id`+`asset_id`; matchCandidates by `feed_item_id`+`similarity_score` DESC; actions by `incident_id`+`created_at` DESC; feedItems by `org_id`+`ingest_time` DESC). `firestore.rules` is default-deny — admin SDK bypasses these.
- `scripts/migrate_to_firestore.py` seeds Firestore from an existing local SQLite db for demo continuity.

### S4 — Cloud Storage media adapter (2026-04-25)

- `app/services/storage/_gcs.py` uses a **work-mirror** approach: every Path operation also writes to local `MEDIA_DIR` (`/tmp/var/media` on Cloud Run); after each PIL write the wrapped helper in `storage/__init__.py` calls `upload_existing(path)` to push the bytes to GCS. Avoids re-plumbing PIL helpers (`make_preview`, `make_frame_strip`, `derive_repost`, `generate_placeholder_image`) to `BytesIO`.
- `app/main.py` mounts `/media` as `StaticFiles` in local profile but as `RedirectResponse(302 → public_url_for(...))` in cloud profile. Frontend `mediaUrl()` is unchanged.
- `infra/google-cloud/storage.rules` is default-deny for the client SDK; bucket-level IAM grants `allUsers:objectViewer` (applied by `deploy-api.sh`) so previews are public.

### S5 — Firebase Google sign-in (2026-04-25)

- New `apps/web/src/lib/firebase.ts` with lazy app/auth init gated on `VITE_AUTH_MODE === "firebase"` + `isFirebaseConfigured()`. `signInWithGoogle()` opens a popup, returns `{idToken, email, displayName}`, stashes the token in `localStorage[FIREBASE_ID_TOKEN_KEY]`. `onIdTokenChanged` re-stashes the rotated token automatically.
- `SignInPage.tsx` branches on `mode === "firebase"`: shows a single "Continue with Google" button → popup → ID token → existing `useAuth().signIn(email, displayName)` flow which posts to `/session/login` with the token already in localStorage. Demo mode unchanged.
- `useAuth.signOut()` calls `signOutGoogle()` and clears `FIREBASE_ID_TOKEN_KEY` in firebase mode.

### S6 — Smoke harness (2026-04-25)

- `scripts/smoke.py` (pure stdlib `urllib`) runs the canonical 10-step sequence: health → login → seed → simulate-incident → action(approved) → live/start → overview → assets → feeds → health/profile.
- Argparse: `--base-url`, `--profile {local,public}`. Public profile reads `SMOKE_FIREBASE_ID_TOKEN` from env. Exit 0 on success.
- Local run: 10/10 green in 1.93s. Replaces the hand-typed HTTP sequence in `docs/status.md`.

### S10 — Cloud Run deploy artifacts (2026-04-25)

- `apps/api/Dockerfile` (Python 3.12-slim, libjpeg62-turbo + zlib1g, copies app/, sets `MEDIA_DIR=/tmp/var/media`, `DB_PATH=/tmp/var/app.db`, CMD honors `${PORT}`).
- `apps/api/.dockerignore` excludes `var/`, `*.db`, `.env*`, `service-account.json`, caches, build output.
- `infra/google-cloud/deploy-api.sh` runs `gcloud run deploy killcont-api --source apps/api --region us-central1 --allow-unauthenticated` with the full env-var set, then applies Firestore composite indexes, then grants `allUsers:objectViewer` on the bucket.

### S11 — Firebase Hosting deploy artifacts (2026-04-25)

- `apps/web/firebase.json` (public=dist, single SPA rewrite `**` → `/index.html`, long-cache for `/assets/**`, no-cache for `index.html`).
- `apps/web/.firebaserc` (default project `killcont-demo`).
- `apps/web/.env.production.example` template for `VITE_API_BASE_URL`, `VITE_AUTH_MODE=firebase`, `VITE_FIREBASE_*`, `VITE_GOOGLE_MAPS_API_KEY`.
- `infra/google-cloud/deploy-web.sh` writes `.env.production` from required env vars, runs `npm run build` (falls back to `npx vite build` if tsc trips on TS5103), then `firebase deploy --only hosting`. Prints reminder commands to back-fill `PUBLIC_WEB_ORIGIN` on Cloud Run.

### Earlier closed gaps (DP1–DP15, S2)

### S2 — Repository interfaces (2026-04-25)

- **Adapter seams in place.** `app/services/repos.py` and `app/services/storage.py` are now packages. `repos/_sqlite.py` and `storage/_local.py` are verbatim ports of the previous behaviour; `repos/_firestore.py` and `storage/_gcs.py` are placeholders that raise `NotImplementedError("...pending S3"|"...pending S4")` so a typo in `.env` cannot bring the API up in a half-broken state.
- **Single source of truth** for which adapter is live: `app/services/profile.py::active_metadata_backend()` / `active_media_backend()` — falls back to local if `.env` carries an unknown value.
- **Backend-agnostic helpers** (`incident_to_summary`, `new_*_id`, `make_preview`, `derive_repost`, `generate_placeholder_image`, `make_frame_strip`) live in `_common.py` and are re-exported regardless of adapter.
- **Verification:** `python -m compileall app` clean, `npx vite build` clean (501 modules), local-profile in-process flow (`reset_db → init_db → seed → list_incidents → get_incident_detail → list_assets → make_preview`) green; public-profile probe (`METADATA_BACKEND=firestore MEDIA_BACKEND=gcs`) raises `NotImplementedError` on every persistence call as designed.

### DP+ UX polish sprint (2026-04-25)

- **DP8 Placeholder imagery** — `app/services/storage.py::generate_placeholder_image` rewritten to compose a real stadium scene (sky gradient, stadium arc, pitch polygon, stage-light ellipses, crowd flecks, title chip, brand badge). 960×540 JPEG quality 86. No more empty blue gradients on assets/incidents/monitor/evidence.
- **DP9 Evidence context** — `EvidencePage.tsx` now renders `Evidence · INC-XXXXX — <asset title>` with subtitle exposing asset id, feed id, severity, similarity %. Added prev/next incident navigation and `← Back to Incidents` breadcrumb. Accepts `?incident=` (legacy `?incidentId=` kept).
- **DP10 Settings cards** — Replaced static Monitor/AI text blocks with **System Status** card (runtime profile, metadata backend, media backend, auth backend, SSE state, pHash threshold, Gemini live/fallback dot + Test button) and **Operator Profile** card (name, email, role, org, user id, sign-out). New `GET /api/v1/health/profile` route + `useHealthProfile` TanStack hook (15s stale, 30s refetch).
- **DP11 LiveWatch refresh** — `LiveStartRequest` accepts optional `asset_id` + `platform`. `_live_emitter` randomizes `minute_base`/source/platform and triggers a real `simulate_incident` mid-stream so "Fresh from matcher" rail visibly changes per click. Frontend got an asset `<select>` (Auto-pick + each asset) inside the `ContextHeader` actions slot.
- **DP12 Gemini visibility** — `triage.py` exposes `LAST_GEMINI_STATUS` / `LAST_GEMINI_LATENCY_MS` / `LAST_GEMINI_SOURCE` and `current_gemini_snapshot()`. Status taxonomy: `unconfigured | ok | fallback | rate_limited | network_error | parse_error`. 6s timeout on Gemini call. New `POST /api/v1/debug/test-gemini` route returns `{source, status, latency_ms, configured, model, reason_short, reason_detailed, operator_copy}`. Settings page surfaces the snapshot as a status dot + Test button.
- **DP13 ContextHeader** — Shared `apps/web/src/components/layout/ContextHeader.tsx` with eyebrow + title + subtitle + actions slot, three-row grid that stacks below 640px. Adopted on Evidence + LiveWatch.
- **DP14 MediaFrame** — Shared `apps/web/src/components/ui/MediaFrame.tsx` with `__empty` state (camera-slash icon + "No preview available") replacing the gradient fallback. Adopted on Incidents, IncidentDetail, Monitor.
- **DP15 Layout sweep** — `.section-heading--inline` flex-wrap with min-width guards; `.stack-list__item > strong` `overflow-wrap: anywhere`; `.status-pill { white-space: nowrap }`; new `.settings-grid` / `.settings-card` / `.status-list` / `.status-row` / `.status-dot--{ok,warn,muted}` rules; new `.live-watch__selector` rules. No horizontal scrollbar at 1920 → 375 px.

### Earlier closed gaps (DP1–DP7)

- **DP1 TopNav** — fake "Live Sync"/"Google Login" removed; Settings link + user-avatar dropdown added.
- **DP2 Incidents** — right panel bound to real selection (live thumbnails, similarity %, trust, reason, operator copy); SSE fresh-pulse on new incidents.
- **DP3 Assets** — thumbnail rail; `preview_path` added to `AssetSummary` + `list_assets` repo output.
- **DP4 Monitor** — feed rows show thumbnails + linked-incident badges via `feedToIncident` map; selection pane with full metadata.
- **DP5 LiveWatch** — fallback rows dropped; SSE-connected indicator; auto-triaged incident rail.
- **DP6 Evidence** — new `GET /api/v1/incidents/{id}/notice` returns a Markdown takedown notice; "Prepare notice" triggers download; "Copy operator summary" → clipboard; 4-state provenance chip.
- **DP7 Threat map** — SVG world map on Overview + LiveWatch (`apps/web/src/features/shared/ThreatMap.tsx`). Incidents plotted via `map_lat`/`map_lng` auto-populated by `app/services/geo.py::coords_for_region` (simulate + seed). Propagation arcs between `->`-separated cities in `map_region`. Marker click navigates to incident detail. Works offline — no Google Maps key needed.
