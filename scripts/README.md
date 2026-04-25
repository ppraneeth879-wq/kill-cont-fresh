# Scripts

Helper scripts for the KillCont demo. All scripts are run from the repo root.

## `smoke.py` — API smoke harness

Replaces the hand-typed HTTP sequence in `docs/status.md`. Exercises the full
demo pipeline (login → seed → simulate → action → live/start → overview →
assets → feeds → health/profile) against any base URL, asserting response
shapes.

### Local profile

```
python scripts/smoke.py
```

Defaults to `http://127.0.0.1:8000/api/v1` and the demo-bearer login flow.
Exits 0 on success, 1 with the failing check on the last line.

### Public profile

Get a Firebase ID token from your browser devtools (signed-in tab,
`localStorage["killcont-firebase-id-token"]`), then:

```
set SMOKE_FIREBASE_ID_TOKEN=ya29....
python scripts/smoke.py \
  --base-url https://killcont-api-xxx.a.run.app/api/v1 \
  --profile public
```

## `migrate_to_firestore.py` — SQLite → Firestore one-off

Reads `apps/api/var/app.db` and writes the same rows into the configured
Firestore project using the public-profile adapter. Intended to seed the
cloud project with the demo dataset for the first time.

```
set RUNTIME_PROFILE=public
set METADATA_BACKEND=firestore
set FIREBASE_PROJECT_ID=killcont-demo
set FIREBASE_CREDENTIALS_PATH=path\to\service-account.json
python scripts/migrate_to_firestore.py
```

Idempotent — re-running upserts the same docs by id.

## Working rules

- Scripts must be runnable on a fresh checkout with only `requirements.txt`
  installed in `apps/api/` (no extra `pip install` needed).
- No interactive prompts; everything is env-driven.
- Network failures should print the URL that failed.
