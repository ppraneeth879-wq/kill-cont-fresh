# KillCont Status

Last updated: 2026-04-26

## Overall State

- Active coding workspace: `.claude/worktrees/vibrant-dubinsky-9c449f`.
- Phase: MVP local demo flow is functioning end-to-end.
- Delivery mode: AI-assisted rapid build and verification.
- Current goal: harden and deploy the same flow publicly (free/low-cost first path).
- Agreed deployment direction: Firebase Hosting + Cloud Run + Firestore + Cloud Storage.

## North Star For The Hackathon

- Ship a polished web application that feels operational, not conceptual.
- Demonstrate detection of reused sports media in mixed simulated feeds.
- Show explainable incident triage and clear operator actions.
- Show a live command center with overview, incidents, evidence, and live-watch updates.

## What Works Right Now

- Demo sign-in issues deterministic demo bearer tokens.
- Backend auth now supports mode switching (`demo` and `firebase`) through environment config.
- Frontend auth path is mode-aware (`VITE_AUTH_MODE`) while preserving existing sign-in UX.
- Auth middleware protects private API routes and supports SSE token query fallback.
- Demo controls support seed, reset, simulate incident, and live segment start.
- Simulate incident creates feed item, match candidate, triage text, and incident records.
- Incident detail and action endpoints are wired and returning live records.
- Dashboard, assets, incidents, and feeds endpoints are wired to frontend pages.
- Frontend routes are connected to live API hooks for overview, incidents, assets, monitor, evidence, live watch, and settings.
- Backend compile and frontend production build both pass.
- End-to-end HTTP smoke sequence now passes for health -> login -> seed -> simulate -> action -> live-start -> overview/assets/feeds.

## Module Status

| Module | Status | Notes |
| --- | --- | --- |
| Product positioning | Completed | Trust + detection + action direction locked |
| Repo and worktree reconciliation | Completed | Active branch aligned with root MVP implementation snapshot |
| Design system direction | Completed | Existing visual language preserved while wiring live data |
| Frontend application shell | Completed | Routing, nav, protected flow, and core pages in place |
| Frontend live data wiring | Completed | Mock paths replaced for core MVP operator surfaces |
| Backend core API | Completed | FastAPI routes for auth/session, demo, incidents, dashboard, assets, feeds |
| Demo incident pipeline | Completed | Seed + simulate + incident detail + action + live events path verified |
| Auth profile architecture | Completed | API and web both support demo/firebase mode wiring via env config |
| Similarity engine (MVP) | Completed | Fast PIL-based 64-bit hash in production path |
| Evidence workflow | Completed | Dynamic ContextHeader (DP9), prev/next navigation, notice export, provenance chip |
| Threat map | Completed | SVG world map on Overview + LiveWatch with `map_lat`/`map_lng` + propagation arcs (DP7) |
| UX polish (DP+ phase) | Completed | DP8 placeholder imagery, DP9 evidence context, DP10 settings cards, DP11 livewatch refresh, DP12 Gemini visibility, DP13 ContextHeader, DP14 MediaFrame, DP15 layout sweep |
| Public cloud profile | Completed | Adapter seams (S2), Firestore (S3), Cloud Storage (S4), Firebase sign-in (S5), smoke harness (S6), Cloud Run (S10) + Firebase Hosting (S11) deploy artifacts all landed. Manual `gcloud run deploy` + `firebase deploy` is the final step (see `infra/google-cloud/deploy-api.sh` + `deploy-web.sh`). |
| On-upload matcher (Bundle B) | Completed | `app/services/matcher.py` runs on every upload, persists matches via `repos.insert_*`, promotes to incident with Gemini triage, synthesizes one demo match if real-feed scoring is empty. New `triage_source/triage_model/triage_latency_ms` columns on incidents. |
| Asset upload UX (Bundle A) | Completed | Autofocus + inline validation + 25 MB cap on the modal; post-upload toast with match summary, scroll-into-view + flash on the new asset row. |
| Live watch refresh (Bundle C) | Completed | Multi-incident emitter (Restream-suspected + Signal-match both promote, platform rotates per fire). Honest "demo stream" copy. Fresh-from-matcher rail shows NEW pulse + reason snippet, rows clickable. |
| Gemini visibility (Bundle D) | Completed | Shared `TriageSourceChip` (Gemini · model · latency or Canned reason) on Incidents/Detail/Evidence. `/health/profile.gemini` exposes lifetime ok_count/fallback_count/total_count, surfaced in Settings → System Status. |
| Documentation operating model | Active | Status and logbook updated alongside implementation |

## Current Runtime Stack

- Frontend: React + Vite + TypeScript.
- Backend: FastAPI + Pydantic.
- Persistence: SQLite (`apps/api/var/app.db`) + local media filesystem (`apps/api/var/media`).
- Auth: demo bearer token model (`killcont-demo-<userId>`).
- Auth mode toggle: `AUTH_BACKEND=demo|firebase` (API), `VITE_AUTH_MODE=demo|firebase` (web).
- Realtime updates: SSE event bus.
- Triage text: canned outputs with optional Gemini API fallback.

## Public Deployment Target (Next)

- Web on Firebase Hosting.
- API on Cloud Run.
- Metadata on Firestore.
- Media on Cloud Storage.
- Keep local SQLite/filesystem profile for offline demo fallback and rapid local testing.

## Closed (2026-04-26) — Bundle B / A / C / D (Plan: fix-incompleteness)

User-reported demo gaps from playthrough I1–I6 ("upload doesn't register matches", "Fresh-from-matcher doesn't refresh", "what is Gemini even doing here?", etc.) closed end-to-end. Plan: `docs/superpowers/plans/2026-04-26-fix-incompleteness.md`.

- **Bundle B — On-upload matcher.** New `app/services/matcher.py` runs after every successful asset upload: scores against existing feed_items, writes `match_candidates`, promotes strong matches to `incidents` with full Gemini triage, captures `triage_source/triage_model/triage_latency_ms`, and synthesizes one derived feed-item if no real matches cleared the threshold (gated by `Settings.synthesize_demo_match=True`). Adapter-clean — every write goes through `repos.insert_*`. SQLite SCHEMA_SQL gained the three triage columns at the canonical level so `/demo/reset` no longer breaks. Verified: upload of an existing preview JPG took the incident count 4 → 5 with `AssetDetail.matches[0].triage_source = "gemini"`.
- **Bundle A — Asset upload form UX.** `AssetUploadModal` now autofocuses the title input on open, runs inline validation (title required, file ≤ 25 MB, `image/*` mime), and shows the chosen file's name+size as a hint. `AssetsPage` consumes the resolved `AssetDetail.matches` from the mutation: a slide-in toast above the table summarises "N matches surfaced · M incidents created" (or "no reposts found"), the new row scrolls into the centre of the viewport, flashes for 1.6 s, and auto-dismisses after 8 s.
- **Bundle C — Live Watch honest stream.** `_live_emitter` now promotes on both "Restream suspected" and "Signal match" segments and rotates `SIMULATED_PLATFORMS` per fire — an 8-segment run produces ~3 incidents across 3 different platforms/regions instead of the previous 1. LiveWatch eyebrow + subtitle made honest about the simulation. Fresh-from-matcher rail rows are clickable, render the reason snippet (2-line clamp), and flash + show a "NEW" pill when SSE delivers `incident.created`.
- **Bundle D — Gemini visibility.** New `apps/web/src/components/ui/TriageSourceChip.tsx` (pulse-dot, two sizes, tooltip with full provenance) wired into IncidentsPage rows + selected-detail header, IncidentDetailPage hero, and EvidencePage case-summary panel. `triage.py` keeps lifetime `GEMINI_OK_COUNT/GEMINI_FALLBACK_COUNT` counters; `/health/profile.gemini` now carries `ok_count/fallback_count/total_count`. Settings → System Status shows a "Gemini activity: N live · M fallback · T total" row whenever any call has run.

Verification (2026-04-26):
- `python -m compileall app` clean.
- `npx vite build` clean (514 modules, 22.50 kB CSS, 584 kB JS).
- `python scripts/smoke.py` 10/10 green in 7.56 s.
- End-to-end: seed → simulate-incident with Gemini key set → incident.triage_source=`gemini`, model=`gemini-2.5-flash`, latency_ms≈5677; `/health/profile` ok_count=1, total=1.

## Closed (2026-04-25) — DP+ UX Polish Sprint

- **DP8** Replaced empty blue-gradient `.media-frame` placeholders with rich PIL-composed stadium scenes (sky gradient, stadium arc, pitch polygon, stage lights, crowd flecks, title chip, brand badge). Seeded asset previews + simulated repost frames now render real-looking imagery.
- **DP9** Evidence page now shows `Evidence · INC-XXXXX — <asset title>` with subtitle exposing asset id, feed id, severity, similarity %. Added prev/next incident navigation and `← Back to Incidents` breadcrumb. Accepts `?incident=` (legacy `?incidentId=` still supported).
- **DP10** Settings page deleted the static "Monitor mode" / "AI mode" text blocks. Replaced with **System Status** card (runtime profile, metadata backend, media backend, auth backend, SSE state, pHash threshold, Gemini status) + **Operator Profile** card (name, email, role, org, user id, sign-out). New `GET /api/v1/health/profile` endpoint feeds the System Status card via `useHealthProfile` (TanStack Query, 15s stale, 30s refetch).
- **DP11** LiveWatch now accepts a user-selected asset (`<select>` populated from `useAssets()` with auto-pick fallback). `_live_emitter` randomizes `minute_base`, source, platform, and triggers a real `simulate_incident` mid-stream so "Fresh from matcher" rail visibly changes per click. `LiveStartRequest` schema gained optional `asset_id` and `platform` fields.
- **DP12** `app/services/triage.py` exposes `LAST_GEMINI_STATUS`, `LAST_GEMINI_LATENCY_MS`, `LAST_GEMINI_SOURCE` and `current_gemini_snapshot()`. Status taxonomy: `unconfigured | ok | fallback | rate_limited | network_error | parse_error`. 6-second timeout on Gemini HTTP call. New `POST /api/v1/debug/test-gemini` endpoint runs `generate_triage` with a dummy asset/feed and returns source + latency. Settings page shows status dot (ok/warn/muted) + Test button.
- **DP13** Shared `ContextHeader` component (`apps/web/src/components/layout/ContextHeader.tsx`) — eyebrow + title + subtitle + actions slot. Adopted on Evidence and LiveWatch.
- **DP14** Shared `MediaFrame` component (`apps/web/src/components/ui/MediaFrame.tsx`) — single render path for media, with `__empty` state showing camera-slash icon + "No preview available" instead of blue-gradient fallback. Adopted on Incidents (both panes), IncidentDetail, Monitor.
- **DP15** Layout sweep — `.context-header` responsive grid; `.section-heading--inline` flex-wrap with min-width guards; `.stack-list__item` `overflow-wrap: anywhere` and `.status-pill { white-space: nowrap }`; new `.settings-grid` / `.settings-card` / `.status-list` rules; `.live-watch__selector` styling.

Verification (2026-04-25):
- `cd apps/api && python -m compileall app` — clean.
- `cd apps/web && npx vite build` — clean (501 modules, `dist/assets/index-DG19AuHm.css` 20.10 kB).
- Local profile demo flow re-walked: seed → simulate-incident → live/start (3×) → "Fresh from matcher" rail showed three different assets/reasons.
- `GET /health/profile` returns the documented shape; `POST /debug/test-gemini` returns `source: "fallback"` with no key set.

## Closed (2026-04-25 — same day, post-DP+) — S2 Adapter Seams

- Converted `app/services/repos.py` and `app/services/storage.py` into adapter packages. `repos/_sqlite.py` + `storage/_local.py` are verbatim ports of the previous behaviour; `repos/_firestore.py` + `storage/_gcs.py` raise `NotImplementedError("...pending S3"|"...pending S4")`.
- Added `app/services/profile.py` (`active_metadata_backend()` / `active_media_backend()`) as the single source of truth for backend selection. Unknown values in `.env` fall back to local instead of crashing.
- Backend-agnostic helpers live in `_common.py` (id generators + `incident_to_summary` for repos; PIL image processing for storage) and are re-exported regardless of adapter.
- Routes still import via `from app.services import repos, storage` — zero call-site changes.
- Verification (in-process): `reset_db → init_db → seed → list_incidents → get_incident_detail → list_assets → make_preview` returns 4 incidents / 3 assets / preview byte count > 0. Public-profile probe (`METADATA_BACKEND=firestore MEDIA_BACKEND=gcs`) raises `NotImplementedError` on every persistence call.

## Closed (2026-04-25 — same day, post-S2) — S3-S11 Cloud Profile

- **S3 — Firestore metadata adapter.** `app/services/repos/_firestore.py` now implements every public function (list/get/insert/update for users, assets, feed_items, match_candidates, incidents, actions). Incident docs denormalize `asset_title`, `source_platform`, `source_region` at write time. `severity_rank` numeric field added for indexed sorting. Added 4 new write helpers (`insert_asset`, `insert_feed_item`, `insert_match_candidate`, `insert_incident`) to both adapters and refactored `seeder.py` + `routes/demo.py::simulate_incident` to use them (no more raw `get_conn()` writes that bypassed the seam). `infra/google-cloud/firestore.indexes.json` ships composite indexes for the queries that need them; `firestore.rules` is default-deny (admin SDK bypasses).
- **S4 — Cloud Storage media adapter.** `app/services/storage/_gcs.py` uses a work-mirror approach: every Path operation mirrors to local `MEDIA_DIR` (`/tmp/var/media` on Cloud Run), then uploads to GCS via `_upload_path()`. PIL helpers (`make_preview`, `make_frame_strip`, `derive_repost`, `generate_placeholder_image`) are wrapped in `storage/__init__.py` to auto-upload after each write when `is_cloud_backend()`. `app/main.py` mounts `/media` as `StaticFiles` in local profile but as a `RedirectResponse(302 → public_url_for(...))` in cloud profile. `storage.rules` default-deny for client SDK; reads via bucket IAM `allUsers:objectViewer` (granted by `deploy-api.sh`).
- **S5 — Firebase Google sign-in.** New `apps/web/src/lib/firebase.ts` with lazy app/auth init. `signInWithGoogle()` opens popup, receives ID token, stashes in `localStorage[FIREBASE_ID_TOKEN_KEY]`, returns `{idToken, email, displayName}`. `onIdTokenChanged` re-stashes the rotated token. `SignInPage.tsx` branches on `mode === "firebase"` to show "Continue with Google" button; demo mode keeps the existing email/name form. `useAuth.signOut()` calls `signOutGoogle()` and clears the token in firebase mode.
- **S6 — Smoke harness.** `scripts/smoke.py` (pure stdlib) runs the 10-step canonical sequence: health → login → seed → simulate-incident → action → live/start → overview → assets → feeds → health/profile. Argparse: `--base-url`, `--profile {local,public}`. Public profile reads `SMOKE_FIREBASE_ID_TOKEN` from env. Local run completed in 1.93s green.
- **S10 — Cloud Run deploy.** `apps/api/Dockerfile` (Python 3.12-slim, libjpeg62-turbo, MEDIA_DIR=/tmp/var/media, DB_PATH=/tmp/var/app.db, honors `$PORT`). `apps/api/.dockerignore` excludes `var/`, `*.db`, `.env*`, `service-account.json`. `infra/google-cloud/deploy-api.sh` orchestrates `gcloud run deploy --source apps/api --region us-central1 --allow-unauthenticated` with full env-var set, then applies Firestore indexes, then grants `allUsers:objectViewer` on the media bucket.
- **S11 — Firebase Hosting deploy.** `apps/web/firebase.json` (public=dist, single SPA rewrite `**` → `/index.html`, long-cache for `/assets/**`, no-cache for `index.html`). `apps/web/.firebaserc` (default project `killcont-demo`). `apps/web/.env.production.example` template. `infra/google-cloud/deploy-web.sh` writes `.env.production` from env, runs `npm run build` (falls back to `npx vite build` if tsc trips on TS5103), then `firebase deploy --only hosting`.

Verification (2026-04-25, post-S11):
- `cd apps/api && python -m compileall app` — clean.
- `cd apps/web && npx vite build` — clean (513 modules).
- `python scripts/smoke.py` against running local API — 10/10 green in 1.93s.
- Public-profile probe (`METADATA_BACKEND=firestore MEDIA_BACKEND=gcs`) — adapters resolve, would reach Firestore/GCS at runtime (not exercised here without real cloud creds).

## Immediate Next Tasks

1. **S12** — Run `bash infra/google-cloud/deploy-api.sh` against the provisioned `killcont-demo` GCP project, then `bash infra/google-cloud/deploy-web.sh`. Back-fill `PUBLIC_WEB_ORIGIN` + `ALLOWED_ORIGINS` on Cloud Run with the hosted FE URL. Add the Firebase Hosting domain to Firebase Auth → authorized domains.
2. **S12** — Run `python scripts/smoke.py --profile public --base-url https://killcont-api-xxx.run.app/api/v1` with `SMOKE_FIREBASE_ID_TOKEN` set to validate the deployed stack end-to-end.
3. **Demo polish** — record a 2-minute screen capture for judges; pre-warm Cloud Run with `--min-instances=1` if cold starts exceed 2s during the demo window.

## Verification Completed

- `apps/web`: `npm run build` / `npx vite build`
- `apps/api`: `python -m compileall app`
- API smoke validation (HTTP): health/login/seed/simulate/action/live-start/dashboard/assets/feeds all returned 200
- API sanity validation (in-process): login/me/seed/simulate returned 200 after auth backend refactor
- DP+ verification (2026-04-25): `/health/profile` returns full shape, `/debug/test-gemini` returns valid fallback when key absent, LiveWatch produces three distinct incidents per click, Evidence header shows incident id + asset title for any selected incident, no blue-gradient placeholders remain on any product page
- S3-S11 verification (2026-04-25): adapter packages re-export under both profiles, `scripts/smoke.py --profile local` exits 0 in <2s, vite production bundle 513 modules clean, Dockerfile + deploy scripts ready for first manual deploy

## Risks To Track

- Scope drift from MVP flow into broad connector work.
- Cloud adapter work introducing regressions in local demo mode.
- Over-expanding auth complexity before public demo reliability is locked.
- Threat map/evidence polish slipping behind deployment tasks.

## Update Protocol

- Update this file after any major implementation milestone.
- Keep status honest and specific.
- Change module states only when something is truly built or blocked.
- Add blockers the same day they are discovered.
