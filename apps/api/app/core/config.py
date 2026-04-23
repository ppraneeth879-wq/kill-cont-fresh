from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve paths relative to the apps/api directory so the server can be started
# from any CWD without breaking the DB / media locations.
API_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "KillCont API"
    app_env: str = "development"
    app_version: str = "0.1.0"

    # Runtime profile separation:
    # - local: SQLite + local media filesystem
    # - public: Cloud deployment profile (Firestore + Cloud Storage target)
    runtime_profile: str = "local"

    # Authentication mode:
    # - demo: local bearer tokens (killcont-demo-<userId>)
    # - firebase: verify Firebase ID tokens
    auth_backend: str = "demo"

    # Cloud stubs kept for future deployment; unused in 1-day MVP.
    gcp_project_id: str = ""
    firebase_project_id: str = ""
    firebase_storage_bucket: str = ""
    firebase_credentials_path: str = ""
    vertex_location: str = "us-central1"

    # MVP local storage
    db_path: str = str(API_ROOT / "var" / "app.db")
    media_dir: str = str(API_ROOT / "var" / "media")

    # Backend adapter targets (local defaults).
    metadata_backend: str = "sqlite"
    media_backend: str = "local"

    # Matching
    phash_match_threshold: float = 0.80

    # Triage (optional)
    gemini_api_key: str = ""

    # CORS (comma-separated)
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Public web origin for deployed frontend, added to CORS when set.
    public_web_origin: str = ""

    # Demo / org
    demo_org_id: str = "org-demo-1"
    demo_default_user_id: str = "demo-user-1"

    model_config = SettingsConfigDict(
        env_file=str(API_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        origins = [o.strip() for o in self.allowed_origins.split(",") if o.strip()]
        if self.public_web_origin and self.public_web_origin not in origins:
            origins.append(self.public_web_origin)
        return origins

    @property
    def is_public_profile(self) -> bool:
        return self.runtime_profile.lower() == "public"

    @property
    def db_path_obj(self) -> Path:
        return Path(self.db_path)

    @property
    def media_dir_obj(self) -> Path:
        return Path(self.media_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
