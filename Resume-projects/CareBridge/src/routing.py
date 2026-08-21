from __future__ import annotations

PUBLIC="PUBLIC"
AUTHENTICATED_NO_VISITS="AUTHENTICATED_NO_VISITS"
AUTHENTICATED_WITH_VISIT="AUTHENTICATED_WITH_VISIT"

def resolve_app_state(current_user,visits: list[dict]) -> str:
    if current_user is None: return PUBLIC
    return AUTHENTICATED_WITH_VISIT if visits else AUTHENTICATED_NO_VISITS
