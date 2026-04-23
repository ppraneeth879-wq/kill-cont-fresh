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
