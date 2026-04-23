# Graph Report - .  (2026-04-24)

## Corpus Check
- Corpus is ~40,229 words - fits in a single context window. You may not need a graph.

## Summary
- 300 nodes · 472 edges · 61 communities detected
- Extraction: 61% EXTRACTED · 39% INFERRED · 0% AMBIGUOUS · INFERRED: 183 edges (avg confidence: 0.76)
- Token cost: 100 input · 100 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Database and Repositories|Database and Repositories]]
- [[_COMMUNITY_Authentication and Configuration|Authentication and Configuration]]
- [[_COMMUNITY_Media Storage and Seeding|Media Storage and Seeding]]
- [[_COMMUNITY_Incident Management|Incident Management]]
- [[_COMMUNITY_Feeds and Similarity Match|Feeds and Similarity Match]]
- [[_COMMUNITY_Dashboard and Events Bus|Dashboard and Events Bus]]
- [[_COMMUNITY_Live Demo Simulation|Live Demo Simulation]]
- [[_COMMUNITY_Live Watch and Hooks|Live Watch and Hooks]]
- [[_COMMUNITY_Asset API Routes|Asset API Routes]]
- [[_COMMUNITY_API Initialization Module|API Initialization Module]]
- [[_COMMUNITY_Web API Client|Web API Client]]
- [[_COMMUNITY_Gemini AI Triage|Gemini AI Triage]]
- [[_COMMUNITY_API Setup Documentation|API Setup Documentation]]
- [[_COMMUNITY_Frame AST Previews|Frame AST Previews]]
- [[_COMMUNITY_Event Streaming Routes|Event Streaming Routes]]
- [[_COMMUNITY_Assets Web Page|Assets Web Page]]
- [[_COMMUNITY_Asset React Hooks|Asset React Hooks]]
- [[_COMMUNITY_Evidence Web Page|Evidence Web Page]]
- [[_COMMUNITY_Incident Detail Page|Incident Detail Page]]
- [[_COMMUNITY_Incidents Web Page|Incidents Web Page]]
- [[_COMMUNITY_Incident Detail Hooks|Incident Detail Hooks]]
- [[_COMMUNITY_Dashboard Overview Page|Dashboard Overview Page]]
- [[_COMMUNITY_Research and Trust Docs|Research and Trust Docs]]
- [[_COMMUNITY_Feed Media Previews|Feed Media Previews]]
- [[_COMMUNITY_API Health Check|API Health Check]]
- [[_COMMUNITY_Web App Root Component|Web App Root Component]]
- [[_COMMUNITY_Web App Shell Component|Web App Shell Component]]
- [[_COMMUNITY_App Background Layout|App Background Layout]]
- [[_COMMUNITY_Top Navigation Bar|Top Navigation Bar]]
- [[_COMMUNITY_Asset Upload Modal|Asset Upload Modal]]
- [[_COMMUNITY_Protected Auth Route|Protected Auth Route]]
- [[_COMMUNITY_Sign In Web Page|Sign In Web Page]]
- [[_COMMUNITY_Auth React Hook|Auth React Hook]]
- [[_COMMUNITY_Demo Control Panel|Demo Control Panel]]
- [[_COMMUNITY_Monitor Web Page|Monitor Web Page]]
- [[_COMMUNITY_Settings Web Page|Settings Web Page]]
- [[_COMMUNITY_Incident Architecture Docs|Incident Architecture Docs]]
- [[_COMMUNITY_Scoring Architecture Docs|Scoring Architecture Docs]]
- [[_COMMUNITY_PubSub Architecture Docs|PubSub Architecture Docs]]
- [[_COMMUNITY_Design Threat Blueprints|Design Threat Blueprints]]
- [[_COMMUNITY_Pillow Image Requirements|Pillow Image Requirements]]
- [[_COMMUNITY_API Router Configuration|API Router Configuration]]
- [[_COMMUNITY_API Routes Initialization|API Routes Initialization]]
- [[_COMMUNITY_Vite TypeScript Declarations|Vite TypeScript Declarations]]
- [[_COMMUNITY_Vite JavaScript Config|Vite JavaScript Config]]
- [[_COMMUNITY_Vite TypeScript Config|Vite TypeScript Config]]
- [[_COMMUNITY_Web Entry Point|Web Entry Point]]
- [[_COMMUNITY_Web Route Setup|Web Route Setup]]
- [[_COMMUNITY_Marketing Landing Page|Marketing Landing Page]]
- [[_COMMUNITY_Web Mock Data|Web Mock Data]]
- [[_COMMUNITY_Web TypeScript Types|Web TypeScript Types]]
- [[_COMMUNITY_Vertex AI Documentation|Vertex AI Documentation]]
- [[_COMMUNITY_Gemini AI Documentation|Gemini AI Documentation]]
- [[_COMMUNITY_ImageHash Requirements|ImageHash Requirements]]
- [[_COMMUNITY_React Framework Documentation|React Framework Documentation]]
- [[_COMMUNITY_Vite Tooling Documentation|Vite Tooling Documentation]]
- [[_COMMUNITY_Asset Architecture Docs|Asset Architecture Docs]]
- [[_COMMUNITY_Feed Item Architecture|Feed Item Architecture]]
- [[_COMMUNITY_Gemini Triage Architecture|Gemini Triage Architecture]]
- [[_COMMUNITY_Mindset Concepts Docs|Mindset Concepts Docs]]
- [[_COMMUNITY_Local MVP Status|Local MVP Status]]

## God Nodes (most connected - your core abstractions)
1. `simulate_incident()` - 25 edges
2. `get_conn()` - 25 edges
3. `ingest_feed()` - 23 edges
4. `seed_championship_final()` - 22 edges
5. `get_settings()` - 19 edges
6. `upload_asset_media()` - 11 edges
7. `IncidentSummary` - 11 edges
8. `FeedItemSummary` - 10 edges
9. `publish()` - 10 edges
10. `get_dashboard_overview()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `_startup()` --calls--> `init_db()`  [INFERRED]
  apps\api\app\main.py → apps\api\app\services\db.py
- `app_auth()` --calls--> `authenticate_request_token()`  [INFERRED]
  apps\api\app\main.py → apps\api\app\services\authn.py
- `_org_id()` --calls--> `get_settings()`  [INFERRED]
  apps\api\app\api\routes\assets.py → apps\api\app\core\config.py
- `create_asset()` --calls--> `new_asset_id()`  [INFERRED]
  apps\api\app\api\routes\assets.py → apps\api\app\services\repos.py
- `create_asset()` --calls--> `get_conn()`  [INFERRED]
  apps\api\app\api\routes\assets.py → apps\api\app\services\db.py

## Hyperedges (group relationships)
- **Core Domain Models** — architecture_asset, architecture_feed_item, architecture_match_candidate, architecture_incident [EXTRACTED 1.00]
- **Target Cloud Stack** — api_readme_public_profile, readme_vertex_ai, readme_gemini, architecture_pubsub [INFERRED 0.85]
- **AST-172 Asset Collection** — original_ast_172, preview_ast_172, frame_1_ast_172 [INFERRED 0.95]

## Communities

### Community 0 - "Database and Repositories"
Cohesion: 0.1
Nodes (34): _db_path(), _ensure_parent(), get_conn(), init_db(), SQLite data layer for KillCont MVP.  One sqlite file at ``var/app.db``. The mo, Context-managed sqlite connection with dict rows and foreign keys on., Apply schema, idempotent. Called from FastAPI startup hook., Drop every table, recreate schema. Used by /demo/reset. (+26 more)

### Community 1 - "Authentication and Configuration"
Cohesion: 0.12
Nodes (20): auth_backend(), AuthConfigurationError, authenticate_request_token(), AuthError, AuthIdentity, _extract_bearer_raw(), verify_demo_bearer(), verify_firebase_bearer() (+12 more)

### Community 2 - "Media Storage and Seeding"
Cohesion: 0.13
Nodes (26): AssetDetail, get_asset(), upload_asset_media(), get_asset_detail(), _copy_or_generate_asset_source(), _incident_title(), _make_feed_media(), Demo seeder: plants a ready-to-demo dataset into SQLite.  Generates placeholde (+18 more)

### Community 3 - "Incident Management"
Cohesion: 0.16
Nodes (19): ActionCreate, ActionRecord, IncidentStatusUpdate, BaseModel, LiveEvent, FeedItemIngestRequest, FeedItemSummary, AssetBrief (+11 more)

### Community 4 - "Feeds and Similarity Match"
Cohesion: 0.17
Nodes (17): FeedItemListResponse, get_feed_item(), ingest_feed(), list_feeds(), _org_id(), Ingest an external feed item, run pHash match, optionally promote to incident., list_feed_items(), best_match() (+9 more)

### Community 5 - "Dashboard and Events Bus"
Cohesion: 0.17
Nodes (10): DashboardMetric, DashboardOverviewResponse, get_dashboard_overview(), _org_id(), build_dashboard_overview(), Legacy hardcoded demo data (pre-MVP).  This module is retained as a compatibil, In-process pub/sub for SSE.  Each connected client gets its own asyncio.Queue., Yield raw SSE ``data:`` frames for one client. (+2 more)

### Community 6 - "Live Demo Simulation"
Cohesion: 0.29
Nodes (9): _live_emitter(), LiveStartRequest, Demo control endpoints.  These are what the Settings → Demo Control panel talk, reset(), seed(), SeedRequest, SimulateRequest, start_live() (+1 more)

### Community 7 - "Live Watch and Hooks"
Cohesion: 0.2
Nodes (5): LiveWatchPage(), useSSE(), useDashboardOverview(), useFeeds(), useIncidents()

### Community 8 - "Asset API Routes"
Cohesion: 0.33
Nodes (7): AssetCreateRequest, AssetCreateResponse, AssetListResponse, AssetSummary, create_asset(), list_assets(), _org_id()

### Community 9 - "API Initialization Module"
Cohesion: 0.25
Nodes (1): Worker package placeholder.

### Community 10 - "Web API Client"
Cohesion: 0.29
Nodes (3): api(), ApiError, getToken()

### Community 11 - "Gemini AI Triage"
Cohesion: 0.53
Nodes (5): _build_prompt(), _canned(), generate_triage(), _parse_gemini(), Triage text generator.  Defaults to canned strings keyed by severity. If ``GEM

### Community 12 - "API Setup Documentation"
Cohesion: 0.33
Nodes (6): Demo Auth Backend, FastAPI Backend, Firebase Auth Backend, Local Runtime Profile, Public Runtime Profile, fastapi

### Community 13 - "Frame AST Previews"
Cohesion: 0.5
Nodes (4): AST-172 Frame 1, AST-172 Original Image, AST-188 Original Image, AST-172 Preview Image

### Community 14 - "Event Streaming Routes"
Cohesion: 0.67
Nodes (2): Server-Sent Events stream for the operator UI.      ``EventSource`` can't set, stream()

### Community 15 - "Assets Web Page"
Cohesion: 0.67
Nodes (0): 

### Community 16 - "Asset React Hooks"
Cohesion: 0.67
Nodes (0): 

### Community 17 - "Evidence Web Page"
Cohesion: 0.67
Nodes (0): 

### Community 18 - "Incident Detail Page"
Cohesion: 0.67
Nodes (0): 

### Community 19 - "Incidents Web Page"
Cohesion: 0.67
Nodes (0): 

### Community 20 - "Incident Detail Hooks"
Cohesion: 0.67
Nodes (0): 

### Community 21 - "Dashboard Overview Page"
Cohesion: 0.67
Nodes (0): 

### Community 22 - "Research and Trust Docs"
Cohesion: 0.67
Nodes (3): C2PA Provenance, KillCont Product, Dual Trust Model

### Community 23 - "Feed Media Previews"
Cohesion: 0.67
Nodes (3): FEED-1001 Media Image, FEED-1002 Media Image, FEED-1001 Preview Image

### Community 24 - "API Health Check"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Web App Root Component"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Web App Shell Component"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "App Background Layout"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Top Navigation Bar"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Asset Upload Modal"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Protected Auth Route"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Sign In Web Page"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Auth React Hook"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Demo Control Panel"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Monitor Web Page"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Settings Web Page"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Incident Architecture Docs"
Cohesion: 1.0
Nodes (2): Incident Domain Model, Match Candidate Domain Model

### Community 37 - "Scoring Architecture Docs"
Cohesion: 1.0
Nodes (2): Coarse Semantic Retrieval, Fine Evidence Scoring

### Community 38 - "PubSub Architecture Docs"
Cohesion: 1.0
Nodes (2): Pub/Sub Event Layer, SSE Event Bus

### Community 39 - "Design Threat Blueprints"
Cohesion: 1.0
Nodes (2): Threat Map, Framer Design Inspiration

### Community 40 - "Pillow Image Requirements"
Cohesion: 1.0
Nodes (2): Pillow, PIL-based 64-bit hash

### Community 41 - "API Router Configuration"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "API Routes Initialization"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Vite TypeScript Declarations"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Vite JavaScript Config"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Vite TypeScript Config"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Web Entry Point"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Web Route Setup"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Marketing Landing Page"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Web Mock Data"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Web TypeScript Types"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Vertex AI Documentation"
Cohesion: 1.0
Nodes (1): Vertex AI Multimodal Embeddings

### Community 52 - "Gemini AI Documentation"
Cohesion: 1.0
Nodes (1): Gemini on Vertex AI

### Community 53 - "ImageHash Requirements"
Cohesion: 1.0
Nodes (1): imagehash

### Community 54 - "React Framework Documentation"
Cohesion: 1.0
Nodes (1): React Frontend

### Community 55 - "Vite Tooling Documentation"
Cohesion: 1.0
Nodes (1): Vite

### Community 56 - "Asset Architecture Docs"
Cohesion: 1.0
Nodes (1): Asset Domain Model

### Community 57 - "Feed Item Architecture"
Cohesion: 1.0
Nodes (1): Feed Item Domain Model

### Community 58 - "Gemini Triage Architecture"
Cohesion: 1.0
Nodes (1): Gemini Incident Triage

### Community 59 - "Mindset Concepts Docs"
Cohesion: 1.0
Nodes (1): Operator-First Principle

### Community 60 - "Local MVP Status"
Cohesion: 1.0
Nodes (1): MVP Local Demo Flow

## Knowledge Gaps
- **50 isolated node(s):** `Demo control endpoints.  These are what the Settings → Demo Control panel talk`, `Server-Sent Events stream for the operator UI.      ``EventSource`` can't set`, `SQLite data layer for KillCont MVP.  One sqlite file at ``var/app.db``. The mo`, `Context-managed sqlite connection with dict rows and foreign keys on.`, `Apply schema, idempotent. Called from FastAPI startup hook.` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `API Health Check`** (2 nodes): `health.py`, `health_check()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web App Root Component`** (2 nodes): `App()`, `App.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web App Shell Component`** (2 nodes): `AppShell.tsx`, `AppShell()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `App Background Layout`** (2 nodes): `AppBackground()`, `AppBackground.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Top Navigation Bar`** (2 nodes): `TopNav.tsx`, `TopNav()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Asset Upload Modal`** (2 nodes): `AssetUploadModal.tsx`, `onSubmit()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Protected Auth Route`** (2 nodes): `ProtectedRoute.tsx`, `ProtectedRoute()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Sign In Web Page`** (2 nodes): `SignInPage.tsx`, `onSubmit()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Auth React Hook`** (2 nodes): `useAuth.ts`, `useAuth()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Demo Control Panel`** (2 nodes): `DemoControlPanel.tsx`, `DemoControlPanel()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Monitor Web Page`** (2 nodes): `MonitorPage.tsx`, `formatTime()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Settings Web Page`** (2 nodes): `SettingsPage.tsx`, `SettingsPage()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Incident Architecture Docs`** (2 nodes): `Incident Domain Model`, `Match Candidate Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Scoring Architecture Docs`** (2 nodes): `Coarse Semantic Retrieval`, `Fine Evidence Scoring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PubSub Architecture Docs`** (2 nodes): `Pub/Sub Event Layer`, `SSE Event Bus`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Design Threat Blueprints`** (2 nodes): `Threat Map`, `Framer Design Inspiration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pillow Image Requirements`** (2 nodes): `Pillow`, `PIL-based 64-bit hash`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `API Router Configuration`** (1 nodes): `router.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `API Routes Initialization`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite TypeScript Declarations`** (1 nodes): `vite.config.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite JavaScript Config`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite TypeScript Config`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web Entry Point`** (1 nodes): `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web Route Setup`** (1 nodes): `router.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Marketing Landing Page`** (1 nodes): `LandingPage.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web Mock Data`** (1 nodes): `mock-data.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web TypeScript Types`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vertex AI Documentation`** (1 nodes): `Vertex AI Multimodal Embeddings`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Gemini AI Documentation`** (1 nodes): `Gemini on Vertex AI`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ImageHash Requirements`** (1 nodes): `imagehash`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `React Framework Documentation`** (1 nodes): `React Frontend`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite Tooling Documentation`** (1 nodes): `Vite`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Asset Architecture Docs`** (1 nodes): `Asset Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Feed Item Architecture`** (1 nodes): `Feed Item Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Gemini Triage Architecture`** (1 nodes): `Gemini Incident Triage`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Mindset Concepts Docs`** (1 nodes): `Operator-First Principle`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Local MVP Status`** (1 nodes): `MVP Local Demo Flow`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Authentication and Configuration` to `Database and Repositories`, `Media Storage and Seeding`, `Incident Management`, `Feeds and Similarity Match`, `Dashboard and Events Bus`, `Asset API Routes`, `Gemini AI Triage`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `get_conn()` connect `Database and Repositories` to `Authentication and Configuration`, `Media Storage and Seeding`, `Feeds and Similarity Match`, `Dashboard and Events Bus`, `Asset API Routes`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `simulate_incident()` connect `Database and Repositories` to `Authentication and Configuration`, `Media Storage and Seeding`, `Feeds and Similarity Match`, `Live Demo Simulation`, `Gemini AI Triage`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `simulate_incident()` (e.g. with `get_settings()` and `get_asset_detail()`) actually correct?**
  _`simulate_incident()` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `get_conn()` (e.g. with `create_asset()` and `upload_asset_media()`) actually correct?**
  _`get_conn()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ingest_feed()` (e.g. with `get_settings()` and `new_feed_id()`) actually correct?**
  _`ingest_feed()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `seed_championship_final()` (e.g. with `seed()` and `reset()`) actually correct?**
  _`seed_championship_final()` has 16 INFERRED edges - model-reasoned connections that need verification._