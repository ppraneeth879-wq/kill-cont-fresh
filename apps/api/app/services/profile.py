"""Single source of truth for the active runtime/backend selection.

The ``repos`` and ``storage`` packages dispatch on the values exposed here at
import time so route handlers can keep importing module-level functions.

Falls back to the local profile when an unknown value is configured so a
typo in ``.env`` cannot bring the API up in a half-broken state.
"""

from __future__ import annotations

from typing import Literal

from app.core.config import get_settings


MetadataBackend = Literal["sqlite", "firestore"]
MediaBackend = Literal["local", "gcs"]


_VALID_METADATA: tuple[MetadataBackend, ...] = ("sqlite", "firestore")
_VALID_MEDIA: tuple[MediaBackend, ...] = ("local", "gcs")


def active_metadata_backend() -> MetadataBackend:
    value = (get_settings().metadata_backend or "sqlite").lower()
    if value not in _VALID_METADATA:
        return "sqlite"
    return value  # type: ignore[return-value]


def active_media_backend() -> MediaBackend:
    value = (get_settings().media_backend or "local").lower()
    if value not in _VALID_MEDIA:
        return "local"
    return value  # type: ignore[return-value]


def is_public_profile() -> bool:
    return get_settings().is_public_profile
