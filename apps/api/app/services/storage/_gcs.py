"""Cloud Storage media adapter — public-profile implementation.

Strategy: keep a local mirror under ``MEDIA_DIR`` (on Cloud Run this is
``/tmp/var/media`` per ``.dockerignore`` + Dockerfile defaults) so the
PIL helpers in ``_common`` continue to work against ``Path`` objects
unchanged. After every ``save_bytes`` / ``copy_file``, the mirrored file
is also uploaded to the configured GCS bucket. Reads still happen from
the local mirror inside the same request lifetime; the FE fetches media
through the API's ``/media`` route, which in public profile redirects to
the GCS object's HTTPS URL (configured in ``main.py``).

Trade-off: every PIL pipeline step writes locally first then uploads.
For hackathon-scale traffic (≤10 incidents/minute) the extra latency is
negligible compared to the 6-second Gemini call already in the path.
The simplification keeps ``_common`` adapter-agnostic.

Bucket layout mirrors the ``relpath()`` convention: ``assets/{asset_id}/...``,
``feeds/{feed_id}/...``. So a file at ``media_dir / "assets/AST-1/preview.jpg"``
lives at ``gs://<bucket>/assets/AST-1/preview.jpg``.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from app.core.config import get_settings


# ---------- Lazy GCS client init ----------

_BUCKET = None  # cached google.cloud.storage.Bucket instance


def _bucket():
    """Return a cached GCS Bucket handle, initialising on first use."""

    global _BUCKET
    if _BUCKET is not None:
        return _BUCKET

    from google.cloud import storage  # local import — keeps cold-start cheap in local profile

    settings = get_settings()
    bucket_name = settings.firebase_storage_bucket
    if not bucket_name:
        raise RuntimeError(
            "MEDIA_BACKEND=gcs requires FIREBASE_STORAGE_BUCKET to be set"
        )

    if settings.firebase_credentials_path:
        client = storage.Client.from_service_account_json(
            settings.firebase_credentials_path,
            project=settings.gcp_project_id or settings.firebase_project_id,
        )
    else:
        client = storage.Client(project=settings.gcp_project_id or settings.firebase_project_id)

    _BUCKET = client.bucket(bucket_name)
    return _BUCKET


def _upload_path(path: Path) -> Optional[str]:
    """Upload a local file to GCS at its relpath. Returns the blob name."""

    try:
        rel = relpath(path)
    except ValueError:
        # Path is outside media_root — refuse to upload.
        return None
    blob = _bucket().blob(rel)
    blob.upload_from_filename(str(path))
    return rel


# ---------- Path layer (mirrors local FS for PIL helpers) ----------

def media_root() -> Path:
    root = get_settings().media_dir_obj
    root.mkdir(parents=True, exist_ok=True)
    return root


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def asset_dir(asset_id: str) -> Path:
    return _ensure_dir(media_root() / "assets" / asset_id)


def feed_dir(feed_item_id: str) -> Path:
    return _ensure_dir(media_root() / "feeds" / feed_item_id)


def relpath(abs_path: Path) -> str:
    return str(abs_path.relative_to(media_root())).replace("\\", "/")


def save_bytes(target: Path, data: bytes) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    _upload_path(target)
    return target


def copy_file(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    _upload_path(dest)
    return dest


def upload_existing(path: Path) -> Optional[str]:
    """Upload a file that PIL wrote directly via ``Image.save(path)``.

    Routes that orchestrate multi-step pipelines (e.g. ``simulate_incident``,
    seeder) call ``make_preview`` / ``make_frame_strip`` / etc. — those write
    via PIL straight to ``Path`` and bypass ``save_bytes``. Call this after
    each such step in public profile to mirror the file to GCS.
    """

    if not path.exists():
        return None
    return _upload_path(path)


def upload_directory(path: Path) -> int:
    """Upload every file under ``path`` to GCS (recursive). Returns count."""

    if not path.exists():
        return 0
    count = 0
    for child in path.rglob("*"):
        if child.is_file():
            _upload_path(child)
            count += 1
    return count


def public_url_for(rel: str) -> str:
    """Return the HTTPS URL the browser hits for a media path.

    For the demo profile the bucket is set to public-read on previews
    (see ``infra/google-cloud/storage.rules``), so a direct URL is fine.
    """

    settings = get_settings()
    bucket_name = settings.firebase_storage_bucket
    return f"https://storage.googleapis.com/{bucket_name}/{rel}"
