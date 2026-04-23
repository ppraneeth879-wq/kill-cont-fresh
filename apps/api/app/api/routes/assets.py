from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile, File

from app.core.config import get_settings
from app.schemas.asset import (
    AssetCreateRequest,
    AssetCreateResponse,
    AssetDetail,
    AssetListResponse,
    AssetSummary,
)
from app.services import repos, storage
from app.services.db import get_conn
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
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO assets (id, org_id, title, asset_type, event_name, sport, "
            "   rights_owner, description, status, provenance_status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'processing', ?)",
            (
                asset_id,
                _org_id(),
                body.title,
                body.asset_type,
                body.event_name,
                body.sport,
                body.rights_owner,
                body.description,
                body.provenance_status,
            ),
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

    with get_conn() as conn:
        conn.execute(
            "UPDATE assets SET primary_path = ?, preview_path = ?, phash = ?, "
            "       status = 'watching' WHERE id = ?",
            (
                storage.relpath(primary),
                storage.relpath(preview),
                phash,
                asset_id,
            ),
        )

    updated = repos.get_asset_detail(asset_id)
    await publish("asset.updated", {"asset_id": asset_id})
    return AssetDetail(**updated)


@router.get("/{asset_id}", response_model=AssetDetail)
def get_asset(asset_id: str) -> AssetDetail:
    row = repos.get_asset_detail(asset_id)
    if not row:
        raise HTTPException(status_code=404, detail="asset not found")
    return AssetDetail(**row)
