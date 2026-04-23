from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.services.events_bus import subscribe


router = APIRouter()


@router.get("/stream")
async def stream(request: Request) -> StreamingResponse:
    """Server-Sent Events stream for the operator UI.

    ``EventSource`` can't set custom headers, so the frontend passes the bearer
    token via ``?token=...``. The auth middleware is already wired to honour
    that query parameter.
    """

    async def event_gen():
        async for chunk in subscribe():
            if await request.is_disconnected():
                break
            yield chunk

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
    return StreamingResponse(event_gen(), media_type="text/event-stream", headers=headers)
