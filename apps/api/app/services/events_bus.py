"""In-process pub/sub for SSE.

Each connected client gets its own asyncio.Queue. ``publish()`` fans a message
out to every live queue. Queues are bounded — if a slow client backs up, we
drop messages rather than blocking the publisher.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator


_subscribers: set[asyncio.Queue[str]] = set()


async def publish(event_type: str, data: dict[str, Any]) -> None:
    payload = json.dumps({"type": event_type, "data": data}, default=str)
    for q in list(_subscribers):
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            # Drop the message for slow clients. Better than stalling everyone.
            continue


async def subscribe() -> AsyncIterator[str]:
    """Yield raw SSE ``data:`` frames for one client."""

    q: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
    _subscribers.add(q)
    try:
        # Initial hello so the client sees the connection immediately.
        yield 'data: {"type":"hello","data":{}}\n\n'
        while True:
            try:
                msg = await asyncio.wait_for(q.get(), timeout=15.0)
                yield f"data: {msg}\n\n"
            except asyncio.TimeoutError:
                # Keep-alive comment frame to defeat proxy/browser idle timeouts.
                yield ": keep-alive\n\n"
    finally:
        _subscribers.discard(q)


def subscriber_count() -> int:
    return len(_subscribers)
