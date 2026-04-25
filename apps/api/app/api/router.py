from fastapi import APIRouter

from app.api.routes import (
    assets,
    dashboard,
    debug,
    demo,
    events,
    feeds,
    health,
    incidents,
    session,
)


api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(feeds.router, prefix="/feeds", tags=["feeds"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(debug.router, prefix="/debug", tags=["debug"])
