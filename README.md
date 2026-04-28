# KillCont

**An operator-grade web console that detects, tracks, and triages reused/pirated sports media across the web.**
*Built for the Google Solution Challenge.*

KillCont addresses the growing challenge of unauthorized sports media redistribution. By ingesting media feeds and comparing them against a registered asset library using perceptual hashing (pHash), it identifies duplicate content. It then uses **Google Gemini (2.5 Flash)** to triage incidents in real-time, delivering actionable takedown notices to an operator's dashboard via an active Server-Sent Events (SSE) bus.

---

## 🔍 How It Works: The KillCont Pipeline

The product thesis is simple: identifying pirated media shouldn't require complex training loops, and operators shouldn't spend their time manually triaging obvious infringements.

1. **Asset Registration (The Root of Trust)**: Rights holders upload official assets (video frames, images) into their organization profile. In the `services/repos`, the 64-bit **pHash** is computed and saved.
2. **Signal Ingestion (The Net)**: Simulated external platforms (YouTube, Reddit, streaming mirrors) push signals into the `feed_items` ingestion pipeline.
3. **Collision Detection (The Matcher)**: As fees arrive, `services/matcher.py` scores their perceptual hashes against the entire official asset library. An adjustable threshold (`PHASH_MATCH_THRESHOLD`, default 0.80; `PHASH_DUPLICATE_THRESHOLD` for exact copies, default 0.92) gates match progression.
4. **AI Triage (Gemini 2.5 Flash)**: Instead of handing operators raw hash matches, the incident is routed through `services/triage.py` to **Google Gemini**. Gemini evaluates contextual clues (titles, regional metadata, origin domain) to instantly classify the incident into a takedown category (e.g. "Restream", "Fair Use", "Piracy Mirror").
5. **Real-Time Delivery (The Bus)**: Actionable incidents are cast through an in-process **asyncio SSE Bus** (with bounded 100-item subscriber queues). The React frontend eagerly picks these up, bouncing new pills into the Live-Watch or the main **Incidents** pane instantly.
6. **Operator Resolution**: Operators can review the AI's logic alongside the generated Markdown evidence, clicking "Review", "Accept", or "Reject" to enforce the final takedown workflow.

---

## 🏗️ Architecture & Philosophy

KillCont is designed with a **Dual-Runtime Profile** to ensure the core demo runs flawlessly offline while seamlessly scaling to Google Cloud. We strictly segregate application boundaries so HTTP route definitions (`/api/routes/*`) and UI components never need to change. 

### The Dual Profile Routing Pattern

Through adapter seams in `app/services/profile.py`, the backend inspects local `.env` variables to dispatch the right infrastructure classes dynamically: 

- **Local Profile (`RUNTIME_PROFILE=local`)**: Runs entirely locally via `app/services/repos/_sqlite.py` (SQLite) and `app/services/storage/_local.py` (local filesystem variables under `/var`), secured via a dummy mock bearer token `killcont-demo-<userId>`. Perfect for isolated environments and offline demonstrations.
- **Public Cloud Profile (`RUNTIME_PROFILE=public`)**: Swaps seamlessly to **Google Cloud Platform** managed services via `_firestore.py` and `_gcs.py`. It leverages **Google Firestore** for nested denormalized NOSQL data, **Cloud Storage (GCS)**, Cloud Run, Firebase Auth, and Firebase Hosting. Firebase Auth verifies standard `id_tokens` mapped to actual verified Google accounts.

---

## 🚀 Core Features

* **Perceptual Hashing (pHash) Matching**: Computes 64-bit image hashes locally using `imagehash`. This bypasses the need for heavy model training, matching identical or slightly edited re-uploads instantly regardless of cropping or visual noise.
* **AI-Assisted Triage (Gemini 2.5 Flash)**: Automatically generates context-aware incident summaries and justifications, distinguishing between harmless restreams, commentary, and direct piracy. Built-in latency tracking and resilient fallback counters ensure the UI never hangs.
* **Real-time Operator Dashboard**: An active `asyncio` SSE (Server-Sent Events) pub/sub event bus pushes updates continuously. New incidents and metrics populate the React TanStack queries instantly without expensive HTTP polling.
* **Live-Watch Simulated Stream**: A dedicated mode monitoring rotating simulation rails (simulated YouTube, Reddit, Piracy Mirrors). Segments are matched dynamically giving judges a highly authentic look at the detection cascade.
* **Threat Mapping**: A geographic SVG visualization mapping out propagation arcs (e.g. tracking a pirated stream moving from US servers -> Europe servers), visualizing the blast radius of a leak instantly.
* **Frictionless Google Auth**: Integrates Firebase Authentication to allow open-access operator sign-ins during the judging period, alongside a zero-config local demo auth.

---

## 💻 Tech Stack

**Backend**
- Python 3.11+, FastAPI, Uvicorn
- Data Processing: `imagehash`, PIL (Image manipulation & Preview generation)
- AI layer: `google-genai` (Gemini 2.5 Flash)
- Data Layers: Google Firestore (NoSQL Denormalized), SQLite (6 canonical tables)
- In-process Asyncio 100-queue Pub/Sub (Realtime SSE)

**Frontend**
- React 19, Vite 8, TypeScript
- Data Fetching: TanStack Query (with hybrid SSE Cache Invalidation)
- Auth: Custom Bearer Auth Interceptor / Firebase Auth SDK

**Infrastructure**
- Docker (Python 3.12-slim, libjpeg62-turbo, zlib1g)
- Google Cloud Run (Backend Hosting, concurrent worker execution)
- Firebase Hosting (React SPA Hosting)

---

## 📂 Repository Layout

```text
kill-cont-fresh/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/routes/     # Endpoints (assets, feeds, incidents, dashboard, demo, SSE)
│   │   │   ├── core/config.py  # Pydantic App Settings
│   │   │   ├── services/       # Auth, DB adapters (SQLite/Firestore), GCS adapters, Triage
│   │   │   └── schemas/        # Pydantic Response Models
│   │   ├── var/                # Local SQLite DB & Uploads (Git-ignored)
│   │   ├── Dockerfile          # Cloud Run container definition
│   │   └── requirements.txt
│   └── web/                    # React 19 + Vite Frontend
│       ├── src/
│       │   ├── app/            # SPA Router (Marketing vs Product Shell)
│       │   ├── features/       # Domain views: assets, incidents, live-watch, evidence, auth
│       │   └── lib/            # API fetchers, SSE bindings, Mock Data, Firebase init
│       └── firebase.json       # Firebase Hosting config
├── docs/                       # Architecture, logs, and hackathon design docs
├── infra/google-cloud/         # Cloud Run & Firebase Deployment scripts 
├── packages/                   # Shared contracts & design system (stubs)
└── scripts/                    # Test harnesses (smoke.py) & migration utilities
```

---

## ⚙️ Quick Start (Local Demo MVP)

The local profile allows full end-to-end evaluation without setting up GCP credentials.

### 1. Configure the Environment
Inside `apps/api/.env`:
```ini
RUNTIME_PROFILE=local
AUTH_BACKEND=demo
METADATA_BACKEND=sqlite
MEDIA_BACKEND=local
# Optional: Get live classifications
GEMINI_API_KEY=AIzaSy... 
```

Inside `apps/web/.env`:
```ini
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_AUTH_MODE=demo
```

### 2. Start the Backend
```bash
cd apps/api
python -m pip install -r requirements.txt
# Run the FastAPI server locally
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 3. Start the Frontend
```bash
cd apps/web
npm install
# Run the Vite dev server
npm run dev
# The web app will be available on http://localhost:5173
```

### 4. Run the Demo Simulation
Using the built-in HTTP endpoints, you can trigger the end-to-end evaluation flow. Alternatively, run the smoke test:
```bash
cd scripts
python smoke.py --profile local --base-url http://localhost:8000/api/v1
```
Or execute manual API requests:
1. **Seed Data:** `POST http://localhost:8000/api/v1/demo/seed`
2. **Simulate Incident:** `POST http://localhost:8000/api/v1/demo/simulate-incident`
3. **Start Live Feed:** `POST http://localhost:8000/api/v1/demo/live/start`

Check the frontend dashboard to see the localized data populate in real-time. Wait a few seconds to see Gemini auto-triage the simulated incidents!

---

## ☁️ Cloud Deployment (Google Cloud)

If you'd like to push KillCont to Google Cloud's free tier, we have included the deployment bash stubs in `infra/google-cloud/` which mirror our production deployment path.

1. Install the `gcloud` and `firebase` CLIs.
2. Ensure Firebase Firestore, Storage, and Authentication components are enabled.
3. Configure `apps/api/.env` and `apps/web/.env.production` respectively to point to `RUNTIME_PROFILE=public` and `VITE_AUTH_MODE=firebase`.
4. Deploy the backend to Cloud Run:
```bash
cd infra/google-cloud
./deploy-api.sh
```
5. Deploy the React SPA to Firebase Hosting (Ensure backend `PUBLIC_WEB_ORIGIN` matches Firebase to avoid CORS issues):
```bash
./deploy-web.sh
```

- [Architecture & Philosophy](docs/architecture.md)
- [Design Direction](docs/design-direction.md)
- [Logbook & Checkpoints](docs/logbook.md)
- [Status Tracker](docs/status.md)

