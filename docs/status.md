# KillCont Status

Last updated: 2026-04-22

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
| Evidence workflow | In progress | Evidence view reads incident detail data, needs final narrative polish |
| Threat map | In progress | Visual and data placeholders exist, full interactive map pending |
| Public cloud profile | In progress | Auth/profile foundations complete; storage/metadata adapters and deploy manifests pending |
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

## Immediate Next Tasks

1. Add Firestore metadata adapter behind current repository interfaces.
2. Add Cloud Storage media adapter behind current storage interfaces.
3. Add deploy configs for Cloud Run (API) and Firebase Hosting (web).
4. Integrate Firebase token acquisition path in frontend sign-in runtime flow.
5. Re-run end-to-end smoke validation on the cloud profile.

## Verification Completed

- `apps/web`: `npm run build`
- `apps/api`: `python -m compileall app`
- API smoke validation (HTTP): health/login/seed/simulate/action/live-start/dashboard/assets/feeds all returned 200
- API sanity validation (in-process): login/me/seed/simulate returned 200 after auth backend refactor

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
