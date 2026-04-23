"""Triage text generator.

Defaults to canned strings keyed by severity. If ``GEMINI_API_KEY`` is set in
the environment, attempts a single HTTPS call to Gemini 1.5 Flash and parses
the JSON payload. Any failure falls back to the canned strings, so the demo
never blocks on a network call.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import get_settings


CANNED_BY_SEVERITY: dict[str, tuple[str, str, str]] = {
    "strike": (
        "High-confidence unauthorized repost. Credential stripped.",
        "Keyframes align with the protected clip, provenance is missing, and the upload sits on a known mirror with growing reach. Recommend escalation and notice preparation.",
        "Escalate. Prepare takedown notice and assign to legal review.",
    ),
    "monitor": (
        "Edited derivative with strong structural match. Moderate spread.",
        "Visual structure matches the official asset but overlays/crops suggest commentary. Spread is moderate across 2 repost sources. Worth watching before escalation.",
        "Add to watchlist. Re-evaluate if spread accelerates in the next 2 hours.",
    ),
    "verified": (
        "Likely fan engagement. Low spread, humorous intent.",
        "Short derivative with clear commentary context. Match score moderate, spread low, no commercial signals. Safe to log for visibility.",
        "No action needed. Keep visible for auditor reporting.",
    ),
}


def _canned(severity: str) -> dict[str, str]:
    short, detailed, op_copy = CANNED_BY_SEVERITY.get(severity, CANNED_BY_SEVERITY["monitor"])
    return {
        "reason_short": short,
        "reason_detailed": detailed,
        "operator_copy": op_copy,
    }


def _build_prompt(asset: dict, feed_item: dict, score: float, severity: str) -> str:
    return (
        "You are KillCont's triage assistant. Given a suspected match between a "
        "protected sports asset and a feed item, produce a strict JSON object with "
        'keys "reason_short" (<=15 words), "reason_detailed" (<=60 words), '
        '"operator_copy" (<=25 words, paste-ready recommendation). '
        f"Asset: {asset.get('title')} ({asset.get('asset_type')}, provenance={asset.get('provenance_status')}). "
        f"Feed item: platform={feed_item.get('source_platform')}, region={feed_item.get('source_region')}, "
        f"caption={feed_item.get('caption')}. "
        f"Similarity score: {score:.2f}. Severity tier: {severity}."
    )


def _parse_gemini(payload: dict[str, Any]) -> dict[str, str] | None:
    try:
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        obj = json.loads(text)
        return {
            "reason_short": str(obj.get("reason_short", "")).strip(),
            "reason_detailed": str(obj.get("reason_detailed", "")).strip(),
            "operator_copy": str(obj.get("operator_copy", "")).strip(),
        }
    except (KeyError, IndexError, ValueError, TypeError):
        return None


async def generate_triage(
    asset: dict,
    feed_item: dict,
    score: float,
    severity: str,
) -> dict[str, str]:
    settings = get_settings()
    key = settings.gemini_api_key
    if key:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}",
                    json={
                        "contents": [
                            {"parts": [{"text": _build_prompt(asset, feed_item, score, severity)}]}
                        ],
                        "generationConfig": {"responseMimeType": "application/json"},
                    },
                )
                if resp.status_code == 200:
                    parsed = _parse_gemini(resp.json())
                    if parsed and parsed["reason_short"]:
                        return parsed
        except Exception:
            # Fall through to canned — demo must not be blocked by a network call.
            pass
    return _canned(severity)
