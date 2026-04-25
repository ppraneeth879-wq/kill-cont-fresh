"""Local filesystem media adapter — the local-profile implementation.

Files land under ``var/media/``. Paths stored in the DB are **relative** to
``MEDIA_DIR`` so the directory can be moved without breaking references.

Image processing helpers live in ``_common`` and are re-exported by the
package dispatcher; only the path/IO layer is local-specific.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from app.core.config import get_settings


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
    return target


def copy_file(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return dest
