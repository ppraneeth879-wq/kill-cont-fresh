"""KillCont API smoke harness.

Replaces the hand-typed HTTP sequence in ``docs/status.md`` with a single
command that exercises the full demo pipeline (login -> seed -> simulate ->
action -> live/start -> overview/assets/feeds) and asserts the response
shapes that the FE depends on.

Local-profile usage::

    python scripts/smoke.py

Public-profile usage (against deployed Cloud Run + Firebase Auth)::

    set SMOKE_FIREBASE_ID_TOKEN=ya29....    # paste from FE devtools
    python scripts/smoke.py \\
      --base-url https://killcont-api-xxx.a.run.app/api/v1 \\
      --profile public

Exits 0 on success, 1 on any failure with a clear last-check line.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8000/api/v1"


class SmokeError(RuntimeError):
    pass


def _request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    body: dict | None = None,
    timeout: float = 30.0,
) -> tuple[int, dict | str]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, raw
    except urllib.error.URLError as exc:
        raise SmokeError(f"network error contacting {url}: {exc.reason}")


def _expect_ok(label: str, status: int, body):
    if status >= 300:
        raise SmokeError(f"{label}: expected 2xx, got {status} body={body!r}")


def _expect_keys(label: str, body, keys: list[str]):
    if not isinstance(body, dict):
        raise SmokeError(f"{label}: expected JSON object, got {type(body).__name__}")
    missing = [k for k in keys if k not in body]
    if missing:
        raise SmokeError(f"{label}: missing keys {missing} in {sorted(body.keys())}")


def main() -> int:
    parser = argparse.ArgumentParser(description="KillCont API smoke harness")
    parser.add_argument("--base-url", default=os.environ.get("SMOKE_BASE_URL", DEFAULT_BASE))
    parser.add_argument(
        "--profile",
        choices=("local", "public"),
        default=os.environ.get("SMOKE_PROFILE", "local"),
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    print(f"[smoke] base_url={base} profile={args.profile}")

    started = time.time()

    # --- 1) Health (public) ---
    status, body = _request("GET", f"{base}/health")
    _expect_ok("/health", status, body)
    _expect_keys("/health", body, ["status"])
    print(f"[ok] /health -> {body!r}")

    # --- 2) Login ---
    if args.profile == "public":
        firebase_token = os.environ.get("SMOKE_FIREBASE_ID_TOKEN", "")
        if not firebase_token:
            raise SmokeError("public profile requires SMOKE_FIREBASE_ID_TOKEN env var")
        login_body = {
            "email": "smoke@killcont.demo",
            "display_name": "Smoke Bot",
            "id_token": firebase_token,
        }
    else:
        login_body = {
            "email": "ops@killcont.demo",
            "display_name": "KillCont Smoke",
        }

    status, login = _request("POST", f"{base}/session/login", body=login_body)
    _expect_ok("/session/login", status, login)
    _expect_keys("/session/login", login, ["token", "user"])
    token = login["token"]
    user_id = login["user"].get("user_id") or login["user"].get("id") or "?"
    print(f"[ok] /session/login -> user={user_id}")

    # --- 3) Seed ---
    status, seed = _request(
        "POST", f"{base}/demo/seed", token=token, body={"scenario": "championship-final"}
    )
    _expect_ok("/demo/seed", status, seed)
    _expect_keys("/demo/seed", seed, ["assets", "feed_items", "incidents"])
    print(
        f"[ok] /demo/seed -> assets={seed['assets']} feeds={seed['feed_items']} incidents={seed['incidents']}"
    )

    # --- 4) Simulate incident ---
    status, sim = _request(
        "POST",
        f"{base}/demo/simulate-incident",
        token=token,
        body={},
    )
    _expect_ok("/demo/simulate-incident", status, sim)
    if not isinstance(sim, dict) or not sim.get("incident"):
        raise SmokeError(f"simulate-incident: unexpected body {sim!r}")
    incident = sim["incident"]
    incident_id = incident.get("id")
    if not isinstance(incident_id, str) or not re.match(r"^INC-\d+$", incident_id):
        raise SmokeError(f"simulate-incident: bad incident id {incident_id!r}")
    print(f"[ok] /demo/simulate-incident -> {incident_id} severity={incident.get('severity')}")

    # --- 5) Action on the new incident ---
    status, action = _request(
        "POST",
        f"{base}/incidents/{incident_id}/action",
        token=token,
        body={"type": "reviewing", "notes": "smoke"},
    )
    _expect_ok(f"/incidents/{incident_id}/action", status, action)
    print(f"[ok] /incidents/{incident_id}/action accepted")

    # --- 6) Live start (short run) ---
    status, live = _request(
        "POST",
        f"{base}/demo/live/start",
        token=token,
        body={"segments": 3, "interval_seconds": 1},
    )
    _expect_ok("/demo/live/start", status, live)
    print(f"[ok] /demo/live/start scheduled")

    # --- 7) Dashboard overview ---
    status, overview = _request("GET", f"{base}/dashboard/overview", token=token)
    _expect_ok("/dashboard/overview", status, overview)
    _expect_keys(
        "/dashboard/overview",
        overview,
        ["metrics", "recent_incidents", "active_event"],
    )
    if not isinstance(overview["recent_incidents"], list):
        raise SmokeError(
            f"overview.recent_incidents must be list: {overview['recent_incidents']!r}"
        )
    print(
        f"[ok] /dashboard/overview metrics={len(overview['metrics'])} "
        f"recent={len(overview['recent_incidents'])}"
    )

    # --- 8) Assets ---
    status, assets = _request("GET", f"{base}/assets", token=token)
    _expect_ok("/assets", status, assets)
    asset_items = assets["items"] if isinstance(assets, dict) else assets
    if not isinstance(asset_items, list) or len(asset_items) == 0:
        raise SmokeError(f"/assets returned no rows: {assets!r}")
    print(f"[ok] /assets -> {len(asset_items)} rows")

    # --- 9) Feeds ---
    status, feeds = _request("GET", f"{base}/feeds", token=token)
    _expect_ok("/feeds", status, feeds)
    feed_items = feeds["items"] if isinstance(feeds, dict) else feeds
    if not isinstance(feed_items, list) or len(feed_items) == 0:
        raise SmokeError(f"/feeds returned no rows: {feeds!r}")
    print(f"[ok] /feeds -> {len(feed_items)} rows")

    # --- 10) Health profile (DP10) ---
    status, profile = _request("GET", f"{base}/health/profile", token=token)
    _expect_ok("/health/profile", status, profile)
    _expect_keys(
        "/health/profile",
        profile,
        ["runtime_profile", "metadata_backend", "media_backend", "auth_backend"],
    )
    print(
        f"[ok] /health/profile profile={profile['runtime_profile']} "
        f"meta={profile['metadata_backend']} media={profile['media_backend']} "
        f"auth={profile['auth_backend']}"
    )

    elapsed = time.time() - started
    print(f"[smoke] all green in {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SmokeError as exc:
        print(f"[smoke] FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
