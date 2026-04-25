"""Operator-facing debug endpoints.

Today this router only exposes a Gemini reachability test used by the
Settings page. Keep it narrow — never return secrets, never log the user's
API key, and always fall through to the canned path so the UI stays alive.
"""

from __future__ import annotations

import time
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import triage


router = APIRouter()


class TestGeminiRequest(BaseModel):
    severity: Literal["strike", "monitor", "verified"] = "monitor"


@router.post("/test-gemini")
async def test_gemini(body: TestGeminiRequest) -> dict:
    """Run a single real Gemini call (or fallback) and report the outcome.

    The Settings page wires a "Test Gemini" button to this endpoint. The
    response includes the detected source (`gemini` or `fallback`), the
    reason text that was generated, the latency of the network call, and
    the module-level status so the UI can show a status dot without
    having to ping /health/profile twice.
    """

    dummy_asset = {
        "title": "Championship Final — Trophy Lift",
        "asset_type": "image",
        "provenance_status": "verified",
    }
    dummy_feed = {
        "source_platform": "piracy-mirror",
        "source_region": "Singapore -> London",
        "caption": "Rebroadcast highlight",
    }
    t0 = time.perf_counter()
    result = await triage.generate_triage(dummy_asset, dummy_feed, 0.88, body.severity)
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    snapshot = triage.current_gemini_snapshot()
    return {
        "source": snapshot["last_source"],
        "status": snapshot["status"],
        "latency_ms": snapshot["last_latency_ms"] or latency_ms,
        "configured": snapshot["configured"],
        "model": snapshot["model"],
        "reason_short": result["reason_short"],
        "reason_detailed": result["reason_detailed"],
        "operator_copy": result["operator_copy"],
    }
