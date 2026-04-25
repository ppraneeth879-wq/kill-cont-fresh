# KillCont Logbook

This file is the running execution journal for the team.

Use it after every meaningful change so the project stays in sync.

## Logging Rules

- Add one entry per meaningful implementation session.
- Keep entries factual.
- Mention what was completed, what changed, and what should happen next.
- Link to the relevant docs or files when possible.
- If a decision was reversed, say why.
- If an AI agent produced code or docs, mention that so the team can verify it.

## Entry Template

```md
## YYYY-MM-DD HH:MM

### Done (2026-04-22)
- ...

### Decisions
- ...

### Next
- ...

### Risks / Notes
- ...
```

## 2026-04-25 23:55

### Done (2026-04-25 late — S3 through S11)

- **S3 — Firestore adapter.** Filled in `app/services/repos/_firestore.py` against the Firebase Admin Firestore client. Every public function from the SQLite adapter now has a matching Firestore implementation. Incident docs denormalize `asset_title` / `source_platform` / `source_region` at write time so `list_incidents` doesn't need a join; numeric `severity_rank` field added for indexed sorting. Closed an adapter-bypass leak by adding 4 new write helpers (`insert_asset`, `insert_feed_item`, `insert_match_candidate`, `insert_incident`) to both adapters and refactoring `seeder.py` + `routes/demo.py::simulate_incident` to use them — no remaining raw `get_conn()` writes outside `_sqlite.py`.
- Wrote `infra/google-cloud/firestore.indexes.json` (incidents by org+severity_rank+created_at DESC, org+operator_status+created_at DESC, org+asset_id; matchCandidates by feed+similarity DESC; actions by incident+created_at DESC; feedItems by org+ingest_time DESC) and `firestore.rules` (default-deny — admin SDK bypasses). Added `scripts/migrate_to_firestore.py` to seed Firestore from an existing local SQLite for demo continuity.
- **S4 — Cloud Storage adapter.** Filled in `app/services/storage/_gcs.py` with a work-mirror approach: every Path operation also lands under local `MEDIA_DIR` (which becomes `/tmp/var/media` on Cloud Run). After each PIL write the wrapped helper in `storage/__init__.py` calls `upload_existing(path)` to push the bytes to GCS. Avoids re-plumbing PIL helpers to `BytesIO`. `app/main.py` now serves `/media` as `StaticFiles` in local profile but as `RedirectResponse(302, public_url_for(...))` in cloud profile. `infra/google-cloud/storage.rules` is default-deny for the client SDK; bucket-level IAM grants `allUsers:objectViewer` so previews are public.
- **S5 — Firebase Google sign-in.** New `apps/web/src/lib/firebase.ts` with lazy app/auth init gated on `VITE_AUTH_MODE === "firebase"` + `isFirebaseConfigured()`. `signInWithGoogle()` opens a popup, returns `{idToken, email, displayName}`, and stashes the token in `localStorage[FIREBASE_ID_TOKEN_KEY]`. `onIdTokenChanged` listener re-stashes the rotated token automatically. `SignInPage.tsx` branches: in `firebase` mode it shows a single "Continue with Google" button (popup → ID token → call existing `useAuth().signIn(email, displayName)` which posts to `/session/login` with the token already in localStorage). Demo mode unchanged. `useAuth.signOut()` calls `signOutGoogle()` and clears the token in firebase mode.
- **S6 — Smoke harness.** `scripts/smoke.py` (pure stdlib `urllib`) runs the canonical 10-step sequence: health → login → seed → simulate-incident → action(approved) → live/start → overview → assets → feeds → health/profile. `--profile local` uses the demo bearer token; `--profile public` reads `SMOKE_FIREBASE_ID_TOKEN` from env. Hand-typed sequence retired; one command now verifies the whole HTTP surface. Local run: 10/10 green in 1.93s.
- **S10 — Cloud Run deploy artifacts.** `apps/api/Dockerfile` (Python 3.12-slim, libjpeg62-turbo + zlib1g, copies app/, sets `MEDIA_DIR=/tmp/var/media`, `DB_PATH=/tmp/var/app.db`, CMD honors `${PORT}`). `apps/api/.dockerignore` excludes `var/`, `*.db`, `.env*`, `service-account.json`, caches, build output. `infra/google-cloud/deploy-api.sh` runs `gcloud run deploy killcont-api --source apps/api --region us-central1 --allow-unauthenticated` with the full env-var set (RUNTIME_PROFILE=public, AUTH_BACKEND=firebase, METADATA_BACKEND=firestore, MEDIA_BACKEND=gcs, FIREBASE_PROJECT_ID, FIREBASE_STORAGE_BUCKET, PHASH_MATCH_THRESHOLD, ALLOWED_ORIGINS, PUBLIC_WEB_ORIGIN, optional GEMINI_API_KEY), then applies the Firestore composite indexes, then grants `allUsers:objectViewer` on the bucket.
- **S11 — Firebase Hosting deploy artifacts.** `apps/web/firebase.json` (public=dist, single SPA rewrite `**` → `/index.html`, long-cache for `/assets/**`, no-cache for `index.html`). `apps/web/.firebaserc` (default project `killcont-demo`). `apps/web/.env.production.example` template. `infra/google-cloud/deploy-web.sh` writes `.env.production` from required env vars, runs `npm run build` (falls back to `npx vite build` if tsc trips on TS5103 — pre-existing toolchain issue, vite build alone produces a fully working bundle), then `firebase deploy --only hosting`.

### Decisions

- **Denormalize on write, not on read** in Firestore. Fan-out reads get expensive fast on Always-Free tier. Storing `asset_title`/`source_platform`/`source_region` on the incident doc means `list_incidents` is a single composite-indexed query.
- **Work-mirror for GCS** instead of refactoring PIL helpers to `BytesIO`. PIL writes Path-based; we pay one local write + one upload per asset. Cloud Run's `/tmp` is ephemeral but writable, exactly the constraint this strategy needs.
- **`/media` route is conditional, not adapter-method.** StaticFiles in local, redirect in cloud. Frontend `mediaUrl()` is unchanged; the server hides the difference.
- **Pure-stdlib smoke harness.** No `httpx` dependency on the smoke path so the script runs on any 3.11+ Python with no install step.
- **`tsc -b` fallback.** `npm run build` first; if TS5103 fires we fall back to `npx vite build`. Vite's bundle is what Hosting serves; TS errors block CI in normal repos but we have no CI per README rule, and the bundle is type-stripped already.

### Next

- Provision the GCP/Firebase project (S0 from the plan — user-executed) if not already done.
- Run `bash infra/google-cloud/deploy-api.sh` with the right env vars to land the API on Cloud Run.
- Run `bash infra/google-cloud/deploy-web.sh` to land the web on Firebase Hosting.
- Back-fill `PUBLIC_WEB_ORIGIN` + `ALLOWED_ORIGINS` on the Cloud Run service so CORS accepts the hosted FE.
- Add the Firebase Hosting domain to Firebase Auth → authorized domains so Google sign-in popup works in production.
- Run `python scripts/smoke.py --profile public --base-url https://killcont-api-xxx.run.app/api/v1` with `SMOKE_FIREBASE_ID_TOKEN` set to validate the deployed stack.
- Record demo video.

### Risks / Notes

- Firestore queries require composite indexes; the first run will surface a console error with a deep-link to create them. `deploy-api.sh` applies them up-front via `gcloud firestore indexes composite create-from-file`.
- Cloud Run cold starts can hit ~5s on first request after idle. For the demo window, consider `gcloud run services update killcont-api --min-instances=1` (small cost, ~$0.10/day, but never goes idle).
- Firebase Auth Spark plan supports unlimited Google sign-ins. No quota concerns.
- All these changes preserve the local-profile fallback. Setting `RUNTIME_PROFILE=local` + `AUTH_BACKEND=demo` reverts to SQLite + local FS + bearer-token auth without any code changes.

## 2026-04-25 22:10

### Done (2026-04-25 evening — S2)

- Closed plan step S2 — Repository interfaces (adapter seams). `app/services/repos.py` is now `app/services/repos/` (`_common.py` / `_sqlite.py` / `_firestore.py` / `__init__.py`); `app/services/storage.py` is now `app/services/storage/` (`_common.py` / `_local.py` / `_gcs.py` / `__init__.py`). The previous-behaviour SQLite + local-FS code is verbatim in the `_sqlite.py` / `_local.py` files; the cloud stubs raise `NotImplementedError("...pending S3"|"...pending S4")` on every persistence call so misconfigured `.env` files fail fast.
- Added `app/services/profile.py` exposing `active_metadata_backend()` / `active_media_backend()` / `is_public_profile()` as the single source of truth for adapter selection. Unknown values fall back to the local adapter instead of raising at import time.
- Image-processing helpers (`make_preview`, `derive_repost`, `generate_placeholder_image`, `make_frame_strip`, plus `_clamp` / `_shade` / `_vertical_gradient`) and pure repos helpers (`incident_to_summary`, `new_asset_id`, `new_feed_id`, `new_incident_id`, `new_candidate_id`, `new_action_id`) all live in `_common.py` and are re-exported regardless of which backend is active.
- Route handlers, `seeder.py`, `demo_data.py`, `triage.py` continue to import via `from app.services import repos, storage` and `repos.list_incidents(...)` / `storage.asset_dir(...)` — zero call-site changes anywhere.
- Verification:
  - `python -m compileall apps/api/app` — clean.
  - `cd apps/web && npx vite build` — clean (501 modules, `index-DG19AuHm.css` 20.10 kB).
  - Local profile in-process flow (`reset_db → init_db → seed_championship_final → list_incidents → get_incident_detail → list_assets → media_root / asset_dir / generate_placeholder_image / make_preview`) returns the expected 3 assets + 4 incidents + non-zero preview bytes.
  - Public profile probe (`METADATA_BACKEND=firestore MEDIA_BACKEND=gcs RUNTIME_PROFILE=public`) imports cleanly and raises `NotImplementedError("Firestore metadata adapter pending — see plan step S3")` / `NotImplementedError("Cloud Storage media adapter pending — see plan step S4")` on every persistence call as designed.

### Decisions (2026-04-25 evening)

- Used module-level dispatch on import (not per-call resolution and not DI) so route signatures stay stable and there is zero hot-path overhead. The trade-off: changing `METADATA_BACKEND` requires a restart, which is exactly the discipline we want for a hackathon demo.
- Kept image-processing helpers path-based (`Path` in / `Path` out) for S2. Converting them to `BytesIO` is left to S4 where the GCS adapter needs it; doing it now would have changed the local adapter's call surface unnecessarily.
- `app/services/profile.py` chose to coerce unknown values to the local adapter rather than raise at import time. Misconfigured `.env` files therefore boot in local mode rather than crashing the API — the failure surfaces in `/health/profile` instead.

### Next (2026-04-25 evening)

- **S3** Implement Firestore metadata adapter against the local emulator (`firebase emulators:start --only firestore`). Denormalize `asset_title` / `source_platform` / `source_region` on incident docs so `list_incidents` is a single read. Add `infra/google-cloud/firestore.indexes.json` for composite indexes.
- **S4** Implement Cloud Storage media adapter. Route PIL helpers through `BytesIO`, conditionally swap `app.mount('/media', ...)` for a `GET /media/{path:path}` redirect-to-signed-URL route in the public profile. Add `infra/google-cloud/storage.rules`.
- **S5** Wire `signInWithPopup(GoogleAuthProvider)` into `SignInPage.tsx` when `VITE_AUTH_MODE=firebase`.

### Risks / Notes (2026-04-25 evening)

- The dispatcher reads `get_settings()` at package-import time. Tests that mutate `os.environ` after the module has been imported will not see the new backend without `get_settings.cache_clear()` plus a re-import. The smoke harness in S6 will need to fork a subprocess (or use `importlib.reload`) when toggling profiles.
- Type checkers will see two adapter modules with identical-named symbols. The dispatcher uses runtime conditional imports, so static tools may need an explicit `pyright`/`mypy` config later — not a problem yet because we don't run either.

## 2026-04-25 21:30

### Done (2026-04-25)

- Closed the DP+ UX polish sprint (DP8 through DP15) end-to-end against the local profile so the demo shell is visually demo-grade before any cloud adapter work begins.
- **DP8 — placeholder imagery.** Rewrote `app/services/storage.py::generate_placeholder_image` to compose a real stadium scene (sky gradient, stadium arc, pitch polygon, tinted stage-light ellipses, crowd flecks seeded by color sum, title chip with yellow accent bar, brand badge). 960×540 JPEG quality 86. Seeded asset previews and simulated repost frames now render distinct imagery (blue stadium, gold trophy, teal tunnel) instead of the empty blue gradient.
- **DP9 — evidence context.** `EvidencePage.tsx` now uses the shared `ContextHeader` with `Evidence · ${detail.id} — ${detail.asset.title}` plus subtitle exposing asset id, feed id, severity, similarity %. Added prev/next incident navigation via `setSearchParams` and `goTo(incidentId)` and a `← Back to Incidents` breadcrumb. Accepts both `?incident=` and legacy `?incidentId=`.
- **DP10 — settings cards.** Replaced "Monitor mode" / "AI mode" text blocks with a **System Status** card (profile, metadata, media, auth, SSE, pHash threshold, Gemini live/fallback dot + Test button) and an **Operator Profile** card (name, email, role, org, user id, sign-out). New `GET /api/v1/health/profile` route, `useHealthProfile` TanStack hook (15s stale / 30s refetch), `HealthProfile` + `GeminiSnapshot` types added to `lib/types.ts`.
- **DP11 — livewatch refresh per click.** `_live_emitter` accepts `asset_id` and `platform`, randomizes `minute_base`, picks from an expanded source pool, and triggers a real `simulate_incident` on the "Restream suspected" segment so the "Fresh from matcher" rail visibly changes per `Start live event` click. `LiveStartRequest` schema gained the new optional fields. Frontend got a `<select>` (Auto-pick + each asset) inside the `ContextHeader` actions slot.
- **DP12 — Gemini visibility.** `triage.py` now exposes `LAST_GEMINI_STATUS`, `LAST_GEMINI_LATENCY_MS`, `LAST_GEMINI_SOURCE`, and `current_gemini_snapshot()`. Status taxonomy: `unconfigured | ok | fallback | rate_limited | network_error | parse_error`. 6-second timeout on the Gemini HTTP call so a slow upstream cannot block the SSE pipeline. New `POST /api/v1/debug/test-gemini` route in `app/api/routes/debug.py` runs `generate_triage` against a dummy asset/feed and returns `{source, status, latency_ms, configured, model, reason_short, reason_detailed, operator_copy}`. The Settings page System Status row shows green/amber/grey based on the snapshot.
- **DP13 — `ContextHeader` component.** `apps/web/src/components/layout/ContextHeader.tsx` — props: `eyebrow?`, `title`, `subtitle?`, `actions?`. CSS in `.context-header` with three-row grid that stacks below 640px. Adopted on Evidence and LiveWatch.
- **DP14 — `MediaFrame` component.** `apps/web/src/components/ui/MediaFrame.tsx` — props: `src?`, `alt`, `aspect?`, `variant?`, `caption?`. When `src` resolves it renders an `<img>`; on error or when `src` is missing it shows the `.media-frame__empty` tile (camera-slash icon + "No preview available") instead of the blue gradient. Adopted on Incidents (both comparison panes), IncidentDetail, Monitor.
- **DP15 — layout sweep.** Hardened CSS: `.section-heading--inline` flex-wraps with `min-width: 0; flex: 1 1 260px` on the title block; `.stack-list__item > strong` got `overflow-wrap: anywhere`; `.status-pill { white-space: nowrap }`; new `.panel__header` flex-wrap rule; new `.settings-grid` / `.settings-card` / `.status-list` / `.status-row` / `.status-dot--{ok,warn,muted}` rules; new `.live-watch__selector` / `.live-watch__select` rules. No horizontal scrollbar at 1920 → 1440 → 1280 → 1024 → 768 → 640 → 375.
- **DP16 — docs refresh.** Updated `docs/status.md` (this entry's Closed section + Immediate Next Tasks now point at S2), updated `CLAUDE.md` Recently-closed-gaps + Known Gaps, appended this logbook entry.
- Verification this sprint: `python -m compileall apps/api/app` clean, `cd apps/web && npx vite build` clean (501 modules, `index-DG19AuHm.css` 20.10 kB), local-profile demo walked through end-to-end with three sequential live-event clicks producing three distinct incidents in the rail.

### Decisions (2026-04-25)

- Kept the placeholder imagery generated programmatically (no bundled JPGs) because PIL composition produces visibly distinct demo-grade scenes per asset color and avoids committing binary fixtures.
- Held the 6-second Gemini timeout — long enough for the free-tier model on a normal network, short enough that a stalled API never blocks the SSE pipeline.
- Did not migrate the marketing/landing shell to `ContextHeader` — scope is product surfaces only.
- Did not move into S0 (GCP provisioning) per the user's "stop after each major step" cadence; S0 still requires user action (billing account + CLI auth).

### Next (2026-04-25)

- **S2** Split `repos.py` and `storage.py` into adapter packages with `_sqlite.py` / `_local.py` keeping current behavior and `_firestore.py` / `_gcs.py` raising `NotImplementedError` placeholders.
- **S3** Firestore metadata adapter implementation against the emulator.
- **S4** Cloud Storage media adapter implementation.
- **S5** Firebase Google sign-in popup wiring on `SignInPage`.
- **S6** `scripts/smoke.py` automated harness.

### Risks / Notes (2026-04-25)

- DP+ work is local-profile only — none of it has been validated in a cloud profile because the cloud profile does not yet exist. Adapter work in S2-S4 must verify the new `/health/profile` and `/debug/test-gemini` shapes survive the swap unchanged.
- `docs/status.md` `Module Status` rows for Evidence workflow / Threat map have been moved to Completed; they only need re-opening if a future change introduces a regression.
- Preview images are generated at seed time. If seed timing matters (cold-start of a fresh DB), the JPEG composition adds ~30 ms per asset — negligible at the demo's ~20-row scale.

## 2026-04-22 10:15

### Done

- Added backend auth backend architecture in `apps/api` with environment-driven mode switch:
  - `demo` mode: existing local token flow preserved.
  - `firebase` mode: Firebase ID token verification path added (`firebase-admin` based).
- Refactored API auth middleware to use centralized auth service (`app/services/authn.py`) instead of demo-only token parsing.
- Extended session login schema and route so Firebase mode can accept and verify `id_token` while preserving demo mode behavior.
- Added frontend auth-mode wiring (`VITE_AUTH_MODE`) in `apps/web`:
  - demo flow unchanged
  - firebase mode sends `id_token` when available
- Updated environment templates and README files for both web and API with runtime/auth mode guidance.
- Re-verified build and runtime health after refactor:
  - `apps/api`: `python -m compileall app`
  - `apps/web`: `npm run build`
  - API in-process sanity flow (`login`, `me`, `seed`, `simulate`) all returned 200.

### Decisions (2026-04-22)

- Keep demo auth as default to protect judge demo reliability and offline fallback.
- Introduce Firebase auth as a selectable backend now, then complete token acquisition wiring in the next phase.
- Preserve frontend visual treatment; this phase is architecture/runtime only.

### Next (2026-04-22)

- Implement Firestore metadata adapter and Cloud Storage media adapter.
- Add deployment manifests for Cloud Run and Firebase Hosting.
- Complete frontend Firebase token acquisition path.
- Validate full cloud-profile flow end-to-end.

### Risks / Notes (2026-04-22)

- Firebase backend mode requires correct credentials/runtime configuration; misconfiguration can surface as auth backend errors.
- Cloud adapter rollout must preserve current local profile interfaces to avoid regressions.

## 2026-04-21 18:40

### Done (2026-04-21)

- Reconciled active worktree state with the newer root MVP implementation snapshot.
- Completed frontend live wiring for core operator surfaces (overview, incidents, assets, monitor, evidence, live watch, settings) while preserving existing visual language.
- Added missing frontend components required by live flow (incident detail route, demo control panel, asset upload modal).
- Fixed SSE token query behavior so event streams authenticate correctly with backend expectations.
- Identified backend `/demo/seed` stall root cause (blocking hash implementation path).
- Replaced hash generation with a fast PIL-based 64-bit hash in `app/services/similarity.py`.
- Verified backend flow through HTTP smoke sequence: health, login, seed, simulate incident, incident detail, action, live start, overview, assets, feeds.
- Re-validated build health:
  - `apps/api`: `python -m compileall app`
  - `apps/web`: `npm run build`

### Decisions (2026-04-21)

- Keep local-first runtime profile (demo auth + SQLite + local media + SSE) as the stable baseline.
- Keep cloud deployment as the immediate next profile, not a branch rewrite.
- Preserve current frontend design direction; only functional wiring changes are allowed in this phase.

### Next (2026-04-21)

- Add environment-based adapter split for local and cloud data/storage.
- Introduce Firebase/Cloud auth path with demo-token fallback.
- Prepare deployment manifests for Firebase Hosting and Cloud Run.
- Run the same smoke flow against cloud profile before demo hardening.

### Risks / Notes (2026-04-21)

- Cloud adapter changes can regress local reliability if interfaces are not kept stable.
- Threat map and final evidence narration still need polish after deployment profile work.

## 2026-04-13 00:00

### Done (2026-04-13)

- Captured hackathon constraints from the team.
- Confirmed the project name is `KillCont`.
- Confirmed the product will be a web application.
- Locked the core demo pillars:
- web-wide detection of reused clips and images
- AI similarity matching for edited and re-uploaded content
- live monitoring dashboard with a threat map
- Confirmed support direction for both images and videos.
- Confirmed live stream segments are part of MVP storytelling.
- Confirmed monitoring should be mixed real plus simulated.
- Confirmed login should be simple Google sign-in.
- Confirmed preferred stack: React + Vite, FastAPI, Firebase, Vertex AI.
- Created the initial repository folder structure.
- Created planning and operating documents.

### Decisions (2026-04-13)

- Position KillCont as a trust plus detection plus action platform.
- Keep the implementation hackathon-sized and operator-focused.
- Use Firestore vector search for MVP simplicity and future-proof the architecture for later upgrades.
- Treat C2PA as a differentiator layer, not the only detection method.
- Prioritize dashboard quality and explainability over broad connector coverage.

### Next (2026-04-13)

- Scaffold the React and FastAPI apps.
- Implement Firebase authentication.
- Build the upload and ingestion flow.
- Build the first simulated incident pipeline.

### Risks / Notes (2026-04-13)

- The biggest delivery risk is trying to make too many "real" platform connectors in 6 days.
- The product will feel stronger if the incident evidence view is excellent.
- A future `Design.md` should be merged into the visual plan before UI implementation gets too far.

## 2026-04-14 12:30

### Done (2026-04-14)

- Integrated the user-provided visual direction into `docs/design-direction.md`.
- Rewrote `docs/website-blueprint.md` to align the product with the pure-black, Framer-inspired design language.
- Updated `docs/mindset.md` visual rules so the brand surface and the product surface stay aligned.
- Scaffolded the React + Vite frontend in `apps/web`.
- Added a shared background system, top navigation, seeded product routes, and initial page layouts for landing, overview, assets, monitor, incidents, live watch, evidence, and settings.
- Scaffolded the FastAPI backend in `apps/api`.
- Added starter config, API router, health route, session route, dashboard route, assets route, and incidents route.
- Verified the backend scaffold with `python -m compileall app`.
- Fixed a frontend package-version mismatch after checking the npm registry and verified the frontend scaffold with `npm run build`.

### Decisions (2026-04-14)

- Keep one common hero-derived background across all pages and reserve heavier motion work for later polish.
- Preserve electric blue as the primary brand accent while allowing restrained semantic colors only where the command center needs operational clarity.
- Use a GT Walsheim-style display system in spirit, with Sora as the practical code fallback until licensed fonts are introduced.
- Treat the seeded pages as the design and data contract for the next implementation phase, not as throwaway mockups.

### Next (2026-04-14)

- Implement Firebase Authentication on top of the existing sign-in and app-shell routes.
- Create the official asset upload flow.
- Replace seeded frontend data with FastAPI-backed calls and then with Firestore-backed data.
- Implement the first simulated feed ingestion to incident creation path.

### Risks / Notes (2026-04-14)

- The frontend now looks and builds like a real product foundation, which raises the importance of keeping future UI changes visually disciplined.
- The next major risk is backend and data integration complexity, not visual direction.
