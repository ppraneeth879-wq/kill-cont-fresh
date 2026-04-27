# Graph Report - D:\kill-cont-fresh  (2026-04-27)

## Corpus Check
- 88 files · ~303,182 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 478 nodes · 798 edges · 84 communities detected
- Extraction: 65% EXTRACTED · 35% INFERRED · 0% AMBIGUOUS · INFERRED: 283 edges (avg confidence: 0.77)
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
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 31 edges
2. `get_conn()` - 31 edges
3. `simulate_incident()` - 29 edges
4. `seed_championship_final()` - 27 edges
5. `ingest_feed()` - 23 edges
6. `_client()` - 22 edges
7. `_score_pair()` - 18 edges
8. `_synthesize_one_match()` - 14 edges
9. `upload_asset_media()` - 13 edges
10. `IncidentSummary` - 12 edges

## Surprising Connections (you probably didn't know these)
- `app_auth()` --calls--> `authenticate_request_token()`  [INFERRED]
  D:\kill-cont-fresh\apps\api\app\main.py → apps\api\app\services\authn.py
- `get_dashboard_overview()` --calls--> `subscriber_count()`  [INFERRED]
  apps\api\app\api\routes\dashboard.py → apps\api\app\services\events_bus.py
- `_startup()` --calls--> `init_db()`  [INFERRED]
  D:\kill-cont-fresh\apps\api\app\main.py → D:\kill-cont-fresh\apps\api\app\services\db.py
- `_org_id()` --calls--> `get_settings()`  [INFERRED]
  D:\kill-cont-fresh\apps\api\app\api\routes\assets.py → D:\kill-cont-fresh\apps\api\app\core\config.py
- `create_asset()` --calls--> `new_asset_id()`  [INFERRED]
  D:\kill-cont-fresh\apps\api\app\api\routes\assets.py → D:\kill-cont-fresh\apps\api\app\services\repos\_common.py

## Hyperedges (group relationships)
- **Core Domain Models** — architecture_asset, architecture_feed_item, architecture_match_candidate, architecture_incident [EXTRACTED 1.00]
- **Target Cloud Stack** — api_readme_public_profile, readme_vertex_ai, readme_gemini, architecture_pubsub [INFERRED 0.85]
- **AST-172 Asset Collection** — original_ast_172, preview_ast_172, frame_1_ast_172 [INFERRED 0.95]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (61): new_feed_id(), get_conn(), Context-managed sqlite connection with dict rows and foreign keys on., _org_id(), _pick_asset(), simulate_incident(), FeedItemIngestRequest, FeedItemListResponse (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (37): ActionCreate, ActionRecord, IncidentStatusUpdate, AssetCreateRequest, AssetCreateResponse, AssetDetail, AssetListResponse, AssetMatchSummary (+29 more)

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (34): Server-Sent Events stream for the operator UI.      ``EventSource`` can't set, stream(), _client(), count_assets_by_type(), count_incidents_by_status(), _doc_to_dict(), _ensure_admin_app(), get_all_assets_with_phash() (+26 more)

### Community 3 - "Community 3"
Cohesion: 0.12
Nodes (28): upload_asset_media(), coords_for_region(), City -> (lat, lng) lookup used by the demo/seed pipelines.  Keeps lat/lng deriva, Resolve the first recognizable city in a region string.      Accepts free-form v, derive_repost(), generate_placeholder_image(), is_cloud_backend(), make_frame_strip() (+20 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (20): auth_backend(), AuthConfigurationError, authenticate_request_token(), AuthError, AuthIdentity, _extract_bearer_raw(), verify_demo_bearer(), verify_firebase_bearer() (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.1
Nodes (13): api(), apiBase(), ApiError, authMode(), getToken(), prepareNotice(), _config(), _ensureApp() (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (19): asset_dir(), _bucket(), copy_file(), _ensure_dir(), feed_dir(), media_root(), public_url_for(), Cloud Storage media adapter — public-profile implementation.  Strategy: keep a l (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (10): incident_to_summary(), new_action_id(), new_asset_id(), new_candidate_id(), new_incident_id(), _pct(), _rand_suffix(), Shape a joined incident row into the FE-facing summary format.      Expected key (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (12): _db_path(), _ensure_parent(), init_db(), SQLite data layer for KillCont MVP.  One sqlite file at ``var/app.db``. The mo, Apply schema, idempotent. Called from FastAPI startup hook., Drop every table, recreate schema. Used by /demo/reset., reset_db(), public_url_for() (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (7): LiveWatchPage(), useSSE(), useAssets(), useDashboardOverview(), useFeeds(), useIncidents(), useSidebarBadges()

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (13): _live_emitter(), LiveStartRequest, Demo control endpoints.  These are what the Settings → Demo Control panel talk, reset(), seed(), SeedRequest, SimulateRequest, start_live() (+5 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (11): Operator-facing debug endpoints.  Today this router only exposes a Gemini reacha, Run a single real Gemini call (or fallback) and report the outcome.      The Set, test_gemini(), TestGeminiRequest, health_profile(), _build_prompt(), _canned(), current_gemini_snapshot() (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (10): _clamp(), derive_repost(), generate_placeholder_image(), make_frame_strip(), Backend-agnostic image processing helpers.  PIL composition does not care whethe, Render a simulated sports-media composition for the demo.      Avoids the flat-c, Fake a keyframe strip from a single still by applying slight variations.      Fo, Create a visually-similar-but-tampered variant for the simulator.      Adds a cr (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.62
Nodes (6): _expect_keys(), _expect_ok(), main(), KillCont API smoke harness.  Replaces the hand-typed HTTP sequence in ``docs/sta, _request(), SmokeError

### Community 14 - "Community 14"
Cohesion: 0.33
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (6): Demo Auth Backend, FastAPI Backend, Firebase Auth Backend, Local Runtime Profile, Public Runtime Profile, fastapi

### Community 16 - "Community 16"
Cohesion: 0.4
Nodes (2): TopNav(), useAuth()

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (0): 

### Community 18 - "Community 18"
Cohesion: 0.5
Nodes (4): AST-172 Frame 1, AST-172 Original Image, AST-188 Original Image, AST-172 Preview Image

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (2): onSubmit(), validateFile()

### Community 22 - "Community 22"
Cohesion: 0.67
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 0.67
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 0.67
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 0.67
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 0.67
Nodes (3): C2PA Provenance, KillCont Product, Dual Trust Model

### Community 27 - "Community 27"
Cohesion: 0.67
Nodes (3): FEED-1001 Media Image, FEED-1002 Media Image, FEED-1001 Preview Image

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
Nodes (2): Incident Domain Model, Match Candidate Domain Model

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (2): Coarse Semantic Retrieval, Fine Evidence Scoring

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (2): Pub/Sub Event Layer, SSE Event Bus

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (2): Pillow, PIL-based 64-bit hash

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (2): Threat Map, Framer Design Inspiration

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

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
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (0): 

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Insert a match_candidate, promote to incident when warranted, and     return the

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Demo-only path. Generate a derived feed item from the asset's     primary so an

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Insert an incident with denormalized fields for fast list reads.

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Insert a fully-formed asset row. Caller fills every column.      Expected keys:

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Insert a feed-item row.      Expected keys: id, org_id, source_type, source_plat

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Insert a match-candidate row.      Expected keys: id, feed_item_id, asset_id, si

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Insert a fully-formed incident row.      Expected keys: id, org_id, asset_id, fe

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Context-managed sqlite connection with dict rows and foreign keys on.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Apply schema, idempotent. Called from FastAPI startup hook.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Drop every table, recreate schema. Used by /demo/reset.

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Insert a fully-formed asset row. Caller fills every column.      Expected keys:

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Insert a feed-item row.      Expected keys: id, org_id, source_type, source_plat

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Insert a match-candidate row.      Expected keys: id, feed_item_id, asset_id, si

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Insert a fully-formed incident row.      Expected keys: id, org_id, asset_id, fe

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Drop every table, recreate schema. Used by /demo/reset.

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Thin query helpers shared across route handlers.  Not a full ORM — just the co

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Shape a joined incident row into the FE-facing summary format.      Expected k

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Local filesystem storage for uploads and simulated/derivative media.  Files la

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Fake a keyframe strip from a single still by applying slight variations.

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Create a visually-similar-but-tampered variant for the simulator.      Adds a

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Used by the seeder when no real image files are present.

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Vertex AI Multimodal Embeddings

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Gemini on Vertex AI

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): imagehash

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): React Frontend

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Vite

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Asset Domain Model

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Feed Item Domain Model

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): Gemini Incident Triage

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): Operator-First Principle

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): MVP Local Demo Flow

## Knowledge Gaps
- **105 isolated node(s):** `Operator-facing debug endpoints.  Today this router only exposes a Gemini reacha`, `Run a single real Gemini call (or fallback) and report the outcome.      The Set`, `Demo control endpoints.  These are what the Settings → Demo Control panel talk`, `Server-Sent Events stream for the operator UI.      ``EventSource`` can't set`, `One row of matcher output surfaced back to the upload caller.      The fronten` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 28`** (2 nodes): `App()`, `App.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (2 nodes): `AppBackground()`, `AppBackground.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (2 nodes): `TriageSourceChip.tsx`, `TriageSourceChip()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `ProtectedRoute.tsx`, `ProtectedRoute()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (2 nodes): `DemoControlPanel.tsx`, `DemoControlPanel()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (2 nodes): `MonitorPage.tsx`, `formatTime()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (2 nodes): `useHealthProfile.ts`, `useHealthProfile()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (2 nodes): `Incident Domain Model`, `Match Candidate Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (2 nodes): `Coarse Semantic Retrieval`, `Fine Evidence Scoring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (2 nodes): `Pub/Sub Event Layer`, `SSE Event Bus`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (2 nodes): `Pillow`, `PIL-based 64-bit hash`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (2 nodes): `Threat Map`, `Framer Design Inspiration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `router.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `vite.config.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `AppShell.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `router.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `ContextHeader.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `MediaFrame.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `LandingPage.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `mock-data.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `types.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Insert a match_candidate, promote to incident when warranted, and     return the`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Demo-only path. Generate a derived feed item from the asset's     primary so an`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Insert an incident with denormalized fields for fast list reads.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Insert a fully-formed asset row. Caller fills every column.      Expected keys:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Insert a feed-item row.      Expected keys: id, org_id, source_type, source_plat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Insert a match-candidate row.      Expected keys: id, feed_item_id, asset_id, si`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Insert a fully-formed incident row.      Expected keys: id, org_id, asset_id, fe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Context-managed sqlite connection with dict rows and foreign keys on.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Apply schema, idempotent. Called from FastAPI startup hook.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Drop every table, recreate schema. Used by /demo/reset.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Insert a fully-formed asset row. Caller fills every column.      Expected keys:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Insert a feed-item row.      Expected keys: id, org_id, source_type, source_plat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Insert a match-candidate row.      Expected keys: id, feed_item_id, asset_id, si`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Insert a fully-formed incident row.      Expected keys: id, org_id, asset_id, fe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Drop every table, recreate schema. Used by /demo/reset.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Thin query helpers shared across route handlers.  Not a full ORM — just the co`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Shape a joined incident row into the FE-facing summary format.      Expected k`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Local filesystem storage for uploads and simulated/derivative media.  Files la`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Fake a keyframe strip from a single still by applying slight variations.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Create a visually-similar-but-tampered variant for the simulator.      Adds a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Used by the seeder when no real image files are present.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Vertex AI Multimodal Embeddings`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Gemini on Vertex AI`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `imagehash`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `React Frontend`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Vite`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `Asset Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `Feed Item Domain Model`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `Gemini Incident Triage`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `Operator-First Principle`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `MVP Local Demo Flow`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 8`, `Community 11`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Why does `get_conn()` connect `Community 0` to `Community 8`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `simulate_incident()` connect `Community 0` to `Community 3`, `Community 4`, `Community 7`, `Community 10`, `Community 11`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `get_settings()` (e.g. with `_org_id()` and `_org_id()`) actually correct?**
  _`get_settings()` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `get_conn()` (e.g. with `create_asset()` and `upload_asset_media()`) actually correct?**
  _`get_conn()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `simulate_incident()` (e.g. with `get_settings()` and `get_asset_detail()`) actually correct?**
  _`simulate_incident()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `seed_championship_final()` (e.g. with `seed()` and `reset()`) actually correct?**
  _`seed_championship_final()` has 21 INFERRED edges - model-reasoned connections that need verification._