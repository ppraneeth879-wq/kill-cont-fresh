# API

Current backend stack:

- FastAPI
- Pydantic settings
- SQLite metadata store
- Local media filesystem storage
- SSE event stream for live updates
- Pillow + image fingerprinting for similarity matching

## Runtime Profiles

- Local profile (default):
  - metadata backend: sqlite
  - media backend: local filesystem
- Public profile (target):
  - metadata backend: firestore
  - media backend: cloud storage

Profile selection is controlled via environment variables in `.env`.

## Auth Backends

- `demo` (default): local bearer tokens (`killcont-demo-<userId>`) for fast offline demo flow.
- `firebase`: Firebase ID token verification via `firebase-admin`.

`AUTH_BACKEND` in `.env` controls this behavior. Route contracts remain unchanged.

## Local Run

1. Install dependencies from `requirements.txt`.
2. Copy `.env.example` to `.env` and keep local defaults.
3. Run the API:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Module Layout

```text
app/
  api/
  core/
  domain/
  schemas/
  services/
  workers/
```

Guiding principle:

- keep heavy media work asynchronous and keep request handlers thin.
