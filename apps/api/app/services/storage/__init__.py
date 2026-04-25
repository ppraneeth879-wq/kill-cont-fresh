"""Public ``storage`` surface — dispatches to the active media adapter.

Routes import this package via ``from app.services import storage`` and call
``storage.asset_dir(...)`` / ``storage.make_preview(...)`` / etc. The
path-and-IO layer is selected at import time from
``app.services.profile.active_media_backend()``:

* ``local`` → ``app.services.storage._local`` (filesystem under ``var/media``)
* ``gcs``   → ``app.services.storage._gcs`` (Cloud Storage, S4+)

Image-processing helpers (``make_preview``, ``derive_repost``,
``generate_placeholder_image``, ``make_frame_strip``) are storage-agnostic
PIL work and are always re-exported from ``_common`` regardless of which
adapter is active.
"""

from __future__ import annotations

from app.services.profile import active_media_backend

# Always-available pure image helpers (raw, path-only).
from ._common import (  # noqa: F401
    PREVIEW_SIZE,
    FRAME_STRIP_COUNT,
    derive_repost as _raw_derive_repost,
    generate_placeholder_image as _raw_generate_placeholder_image,
    make_frame_strip as _raw_make_frame_strip,
    make_preview as _raw_make_preview,
)

_backend = active_media_backend()

if _backend == "gcs":
    from . import _gcs as _impl
else:
    from . import _local as _impl


# Re-export every adapter-bound function.
media_root = _impl.media_root
asset_dir = _impl.asset_dir
feed_dir = _impl.feed_dir
relpath = _impl.relpath
save_bytes = _impl.save_bytes
copy_file = _impl.copy_file


def upload_existing(path):
    """Public-profile only: mirror a PIL-written file to GCS.

    No-op in local profile (returns ``None``). Routes that compose multiple
    PIL steps (seeder, simulate-incident) call this after each step so the
    cloud bucket stays in sync without changing the existing path-based
    image-processing helpers.
    """

    if hasattr(_impl, "upload_existing"):
        return _impl.upload_existing(path)
    return None


def upload_directory(path):
    """Public-profile only: bulk-upload a directory tree (e.g. frame strips)."""

    if hasattr(_impl, "upload_directory"):
        return _impl.upload_directory(path)
    return 0


def public_url_for(rel):
    """Public-profile only: GCS URL for a media relpath. Empty in local."""

    if hasattr(_impl, "public_url_for"):
        return _impl.public_url_for(rel)
    return ""


def is_cloud_backend() -> bool:
    return _backend == "gcs"


# ---- PIL helper wrappers (auto-upload in cloud profile) ----

def make_preview(src, dest):
    out = _raw_make_preview(src, dest)
    if out is not None and is_cloud_backend():
        upload_existing(out)
    return out


def make_frame_strip(src, dest_dir, count=FRAME_STRIP_COUNT):
    out = _raw_make_frame_strip(src, dest_dir, count)
    if out and is_cloud_backend():
        upload_directory(dest_dir)
    return out


def derive_repost(src, dest, label="REPOST"):
    out = _raw_derive_repost(src, dest, label)
    if out is not None and is_cloud_backend():
        upload_existing(out)
    return out


def generate_placeholder_image(dest, color, label):
    out = _raw_generate_placeholder_image(dest, color, label)
    if out is not None and is_cloud_backend():
        upload_existing(out)
    return out


__all__ = [
    "PREVIEW_SIZE",
    "FRAME_STRIP_COUNT",
    "derive_repost",
    "generate_placeholder_image",
    "make_frame_strip",
    "make_preview",
    "media_root",
    "asset_dir",
    "feed_dir",
    "relpath",
    "save_bytes",
    "copy_file",
    "upload_existing",
    "upload_directory",
    "public_url_for",
    "is_cloud_backend",
]


# Sanity check: make sure wrappers shadow raw helpers in this module's
# public surface. Module-level definitions above already do this; we keep
# this assertion as a safety net for any future refactor.
assert make_preview is not _raw_make_preview
