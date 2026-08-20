from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    supabase_url: str | None
    supabase_anon_key: str | None
    local_mode: bool
    app_url: str

    @property
    def supabase_ready(self) -> bool:
        return bool(
            self.supabase_url
            and self.supabase_anon_key
            and "your-project-id" not in self.supabase_url.lower()
            and self.supabase_url.lower().startswith("https://")
        )

def load_config(secrets=None) -> AppConfig:
    def value(name: str) -> str | None:
        try:
            found=secrets.get(name) if secrets is not None else None
        except Exception: found=None
        return str(found) if found else os.getenv(name)
    return AppConfig(
        value("SUPABASE_URL"), value("SUPABASE_ANON_KEY"),
        str(value("CAREBRIDGE_LOCAL_MODE") or "").lower() in {"1","true","yes"},
        str(value("CAREBRIDGE_APP_URL") or "https://carebridge-ai.streamlit.app").rstrip("/"),
    )
