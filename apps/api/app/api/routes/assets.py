from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile, File

from app.core.config import get_settings
from app.schemas.asset import (
    AssetCreateRequest,
    AssetCreateResponse,
    AssetDetail,
    AssetListResponse,
    AssetMatchSummary,
    AssetSummary,
)
from app.services import repos, storage
from app.services.events_bus import publish
from app.services.similarity import compute_phash


router = APIRouter()


def _org_id() -> str:
    return get_settings().demo_org_id


@router.get("", response_model=AssetListResponse)
def list_assets(request: Request) -> AssetListResponse:
    rows = repos.list_assets(_org_id())
    return AssetListResponse(items=[AssetSummary(**r) for r in rows])


@router.post("", response_model=AssetCreateResponse)
def create_asset(body: AssetCreateRequest) -> AssetCreateResponse:
    asset_id = repos.new_asset_id()
    # Bundle G: route through the adapter so this works in both sqlite
    # (local) and firestore (cloud) profiles. Was raw SQL via get_conn()
    # which silently bypassed Firestore on Cloud Run -> upload step
    # subsequently 404'd because the row was nowhere to be found.
    repos.insert_asset(
        {
            "id": asset_id,
            "org_id": _org_id(),
            "title": body.title,
            "asset_type": body.asset_type,
            "event_name": body.event_name,
            "sport": body.sport,
            "rights_owner": body.rights_owner,
            "description": body.description,
            "status": "processing",
            "provenance_status": body.provenance_status,
            "primary_path": None,
            "preview_path": None,
            "phash": None,
        }
    )
    return AssetCreateResponse(
        id=asset_id,
        upload_url=f"/api/v1/assets/{asset_id}/upload",
    )


@router.post("/{asset_id}/upload", response_model=AssetDetail)
async def upload_asset_media(
    asset_id: str,
    file: UploadFile = File(...),
) -> AssetDetail:
    asset = repos.get_asset_detail(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")

    folder = storage.asset_dir(asset_id)
    ext = Path(file.filename or "upload.jpg").suffix.lower() or ".jpg"
    primary = folder / f"original{ext}"
    storage.save_bytes(primary, await file.read())

    preview = folder / "preview.jpg"
    storage.make_preview(primary, preview)
    storage.make_frame_strip(primary, folder / "frames")

    try:
        phash = compute_phash(primary)
    except Exception:
        phash = None

    # Bundle G: adapter-clean (was raw SQL via get_conn()).
    repos.update_asset_media(
        asset_id=asset_id,
        primary_path=storage.relpath(primary),
        preview_path=storage.relpath(preview),
        phash=phash,
    )

    # Bundle B: run the on-upload matcher against existing feed items.
    # Never let a matcher bug block the asset registration itself.
    from app.services import matcher

    try:
        matches = await matcher.match_asset_against_feeds(asset_id)
    except Exception:
        matches = []

    updated = repos.get_asset_detail(asset_id)
    await publish("asset.updated", {"asset_id": asset_id})

    detail = AssetDetail(**updated)
    detail.matches = [AssetMatchSummary(**m) for m in matches]
    return detail


@router.get("/{asset_id}", response_model=AssetDetail)
def get_asset(asset_id: str) -> AssetDetail:
    row = repos.get_asset_detail(asset_id)
    if not row:
        raise HTTPException(status_code=404, detail="asset not found")
    return AssetDetail(**row)
