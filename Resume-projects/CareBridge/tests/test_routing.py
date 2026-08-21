from types import SimpleNamespace
from src.routing import AUTHENTICATED_NO_VISITS, AUTHENTICATED_WITH_VISIT, PUBLIC, resolve_app_state

def test_public_state_has_no_authenticated_user():
    assert resolve_app_state(None,[])==PUBLIC

def test_authenticated_user_without_visits_never_routes_to_public():
    assert resolve_app_state(SimpleNamespace(id="user-a"),[])==AUTHENTICATED_NO_VISITS

def test_authenticated_user_with_visit_routes_to_workspace():
    assert resolve_app_state(SimpleNamespace(id="user-a"),[{"id":"visit-a"}])==AUTHENTICATED_WITH_VISIT
