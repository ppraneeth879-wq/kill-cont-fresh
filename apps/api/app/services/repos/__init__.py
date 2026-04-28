"""Public ``repos`` surface — dispatches to the active metadata adapter.

Routes import this package via ``from app.services import repos`` and call
``repos.list_incidents(...)`` / ``repos.new_incident_id()`` etc. The actual
implementation is selected at import time from
``app.services.profile.active_metadata_backend()``:

* ``sqlite``   → ``app.services.repos._sqlite`` (local profile)
* ``firestore`` → ``app.services.repos._firestore`` (public profile, S3+)

Backend-agnostic helpers (ID generators, ``incident_to_summary``) live in
``_common`` and are re-exported regardless of which adapter is active.
"""

from __future__ import annotations

from app.services.profile import active_metadata_backend

# Always-available pure helpers.
from ._common import (  # noqa: F401
    incident_to_summary,
    new_action_id,
    new_asset_id,
    new_candidate_id,
    new_feed_id,
    new_incident_id,
)

_backend = active_metadata_backend()

if _backend == "firestore":
    from . import _firestore as _impl
else:
    from . import _sqlite as _impl


# Re-export every adapter-bound function.
list_incidents = _impl.list_incidents
get_incident_detail = _impl.get_incident_detail
list_assets = _impl.list_assets
get_asset_detail = _impl.get_asset_detail
list_feed_items = _impl.list_feed_items
get_feed_item = _impl.get_feed_item
count_incidents_by_status = _impl.count_incidents_by_status
count_assets_by_type = _impl.count_assets_by_type
insert_action = _impl.insert_action
update_incident_status = _impl.update_incident_status
update_incident_severity = _impl.update_incident_severity
update_asset_media = _impl.update_asset_media
upsert_user = _impl.upsert_user
get_user = _impl.get_user
get_all_assets_with_phash = _impl.get_all_assets_with_phash
insert_asset = _impl.insert_asset
insert_feed_item = _impl.insert_feed_item
insert_match_candidate = _impl.insert_match_candidate
insert_incident = _impl.insert_incident


__all__ = [
    "incident_to_summary",
    "new_action_id",
    "new_asset_id",
    "new_candidate_id",
    "new_feed_id",
    "new_incident_id",
    "list_incidents",
    "get_incident_detail",
    "list_assets",
    "get_asset_detail",
    "list_feed_items",
    "get_feed_item",
    "count_incidents_by_status",
    "count_assets_by_type",
    "insert_action",
    "update_incident_status",
    "update_incident_severity",
    "update_asset_media",
    "upsert_user",
    "get_user",
    "get_all_assets_with_phash",
    "insert_asset",
    "insert_feed_item",
    "insert_match_candidate",
    "insert_incident",
]
