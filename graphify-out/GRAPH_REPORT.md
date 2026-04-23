# Graph Report - D:\kill-cont-fresh  (2026-04-24)

## Corpus Check
- 68 files · ~64,469 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 300 nodes · 472 edges · 61 communities detected
- Extraction: 61% EXTRACTED · 39% INFERRED · 0% AMBIGUOUS · INFERRED: 183 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]

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

### Community 0 - "Community 0"
Cohesion: 0.1
Nodes (34): _db_path(), _ensure_parent(), get_conn(), init_db(), SQLite data layer for KillCont MVP.  One sqlite file at ``var/app.db``. The mo, Context-managed sqlite connection with dict rows and foreign keys on., Apply schema, idempotent. Called from FastAPI startup hook., Drop every table, recreate schema. Used by /demo/reset. (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (20): auth_backend(), AuthConfigurationError, authenticate_request_token(), AuthError, AuthIdentity, _extract_bearer_raw(), verify_demo_bearer(), verify_firebase_bearer() (+12 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (26): AssetDetail, get_asset(), upload_asset_media(), get_asset_detail(), _copy_or_generate_asset_source(), _incident_title(), _make_feed_media(), Demo seeder: plants a ready-to-demo dataset into SQLite.  Generates placeholde (+18 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (19): ActionCreate, ActionRecord, IncidentStatusUpdate, BaseModel, LiveEvent, FeedItemIngestRequest, FeedItemSummary, AssetBrief (+11 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (17): FeedItemListResponse, get_feed_item(), ingest_feed(), list_feeds(), _org_id(), Ingest an external feed item, run pHash match, optionally promote to incident., list_feed_items(), best_match() (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (10): DashboardMetric, DashboardOverviewResponse, get_dashboard_overview(), _org_id(), build_dashboard_overview(), Legacy hardcoded demo data (pre-MVP).  This module is retained as a compatibil, In-process pub/sub for SSE.  Each connected client gets its own asyncio.Queue., Yield raw SSE ``data:`` frames for one client. (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (9): _live_emitter(), LiveStartRequest, Demo control endpoints.  These are what the Settings → Demo Control panel talk, reset(), seed(), SeedRequest, SimulateRequest, start_live() (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.2
Nodes (5): LiveWatchPage(), useSSE(), useDashboardOverview(), useFeeds(), useIncidents()

### Community 8 - "Community 8"
Cohesion: 0.33
Nodes (7): AssetCreateRequest, AssetCreateResponse, AssetListResponse, AssetSummary, create_asset(), list_assets(), _org_id()

### Community 9 - "Community 9"
Cohesion: 0.25
Nodes (1): Worker package placeholder.

### Community 10 - "Community 10"
Cohesion: 0.29
Nodes (3): api(), ApiError, getToken()

### Community 11 - "Community 11"
Cohesion: 0.53
Nodes (5): _build_prompt(), _canned(), generate_triage(), _parse_gemini(), Triage text generator.  Defaults to canned strings keyed by severity. If ``GEM

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (6): Demo Auth Backend, FastAPI Backend, Firebase Auth Backend, Local Runtime Profile, Public Runtime Profile, fastapi

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (4): AST-172 Frame 1, AST-172 Original Image, AST-188 Original Image, AST-172 Preview Image

### Community 14 - "Community 14"
Cohesion: 0.67
Nodes (2): Server-Sent Events stream for the operator UI.      ``EventSource`` can't set, stream()

### Community 15 - "Community 15"
Cohesion: 0.67
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (0): 

### Community 18 - "Community 18"
Cohesion: 0.67
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 0.67
Nodes (0): 

### Community 22 - "Community 22"
Cohesion: 0.67
Nodes (3): C2PA Provenance, KillCont Product, Dual Trust Model

### Community 23 - "Community 23"
Cohesion: 0.67
Nodes (3): FEED-1001 Media Image, FEED-1002 Media Image, FEED-1001 Preview Image

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (2): Incident Domain Model, Match Candidate Domain Model

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (2): Coarse Semantic Retrieval, Fine Evidence Scoring

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (2): Pub/Sub Event Layer, SSE Event Bus

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (2): Threat Map, Framer Design Inspiration

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (2): Pillow, PIL-based 64-bit hash

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Vertex AI Multimodal Embeddings

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Gemini on Vertex AI

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): imagehash

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): React Frontend

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Vite

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Asset Domain Model

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Feed Item Domain Model

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Gemini Incident Triage

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Operator-First Principle

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): MVP Local Demo Flow

## Knowledge Gaps
- **50 isolated node(s):** `Demo control endpoints.  These are what the Settings → Demo Control panel talk`, `Server-Sent Events stream for the operator UI.      ``EventSource`` can't set`, `SQLite data layer for KillCont MVP.  One sqlite file at ``var/app.db``. The mo`, `Context-managed sqlite connection with dict rows and foreign keys on.`, `Apply schema, idempotent. Called from FastAPI startup hook.` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 24`** (2 nodes): `health.py`, `health_check()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (2 nodes): `App()`, `App.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (2 nodes): `AppShell.tsx`, `AppShell()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (2 nodes): `AppBackground()`, `AppBackground.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (2 nodes): `TopNav.tsx`, `TopNav()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (2 nodes): `AssetUploadModal.tsx`, `onSubmit()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (2 nodes): `ProtectedRoute.tsx`, `ProtectedRoute()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `SignInPage.tsx`, `onSubmit()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (2 nodes): `useAuth.ts`, `useAuth()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (2 nodes): `DemoControlPanel.tsx`, `DemoControlPanel()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (2 nodes): `MonitorPage.tsx`, `formatTime()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (2 nodes): `SettingsPage.tsx`, `SettingsPage()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (2 nodes): `Incident Domain Model`, `Match Candidate Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (2 nodes): `Coarse Semantic Retrieval`, `Fine Evidence Scoring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `Pub/Sub Event Layer`, `SSE Event Bus`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `Threat Map`, `Framer Design Inspiration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `Pillow`, `PIL-based 64-bit hash`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `router.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `vite.config.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `router.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `LandingPage.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `mock-data.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Vertex AI Multimodal Embeddings`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Gemini on Vertex AI`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `imagehash`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `React Frontend`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Vite`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Asset Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Feed Item Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Gemini Incident Triage`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Operator-First Principle`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `MVP Local Demo Flow`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 8`, `Community 11`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `get_conn()` connect `Community 0` to `Community 1`, `Community 2`, `Community 4`, `Community 5`, `Community 8`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `simulate_incident()` connect `Community 0` to `Community 1`, `Community 2`, `Community 4`, `Community 6`, `Community 11`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `simulate_incident()` (e.g. with `get_settings()` and `get_asset_detail()`) actually correct?**
  _`simulate_incident()` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `get_conn()` (e.g. with `create_asset()` and `upload_asset_media()`) actually correct?**
  _`get_conn()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ingest_feed()` (e.g. with `get_settings()` and `new_feed_id()`) actually correct?**
  _`ingest_feed()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `seed_championship_final()` (e.g. with `seed()` and `reset()`) actually correct?**
  _`seed_championship_final()` has 16 INFERRED edges - model-reasoned connections that need verification._