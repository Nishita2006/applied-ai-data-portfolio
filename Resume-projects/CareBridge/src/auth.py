from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any

EMAIL=re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
class AuthError(RuntimeError): pass

@dataclass
class AuthUser:
    id: str
    email: str
    first_name: str = ""

def validate_signup(email: str,password: str,confirm: str,first_name: str) -> None:
    if not first_name.strip(): raise AuthError("Enter your first name.")
    if not EMAIL.match(email.strip()): raise AuthError("Enter a valid email address.")
    if len(password)<8: raise AuthError("Use at least 8 characters for your password.")
    if password!=confirm: raise AuthError("Passwords do not match.")

class SupabaseAuth:
    def __init__(self,client: Any): self.client=client
    def sign_up(self,email: str,password: str,first_name: str):
        validate_signup(email,password,password,first_name)
        try:
            available=self.client.rpc("is_first_name_available",{"candidate":first_name.strip()}).execute().data
            if available is not True: raise AuthError("That name is already registered. Enter a different name.")
            return self.client.auth.sign_up({"email":email.strip(),"password":password,"options":{"data":{"first_name":first_name.strip()}}})
        except AuthError: raise
        except Exception as exc: raise AuthError(self._friendly(exc,"CareBridge could not create that account.")) from exc
    def sign_in(self,email: str,password: str):
        if not EMAIL.match(email.strip()) or not password: raise AuthError("Enter a valid email and password.")
        try: return self.client.auth.sign_in_with_password({"email":email.strip(),"password":password})
        except Exception as exc: raise AuthError(self._friendly(exc,"The email or password was not accepted.")) from exc
    def sign_out(self) -> None:
        try: self.client.auth.sign_out()
        except Exception: pass
    @staticmethod
    def user(response: Any) -> AuthUser | None:
        raw=getattr(response,"user",None)
        if not raw: return None
        metadata=getattr(raw,"user_metadata",{}) or {}
        return AuthUser(str(raw.id),str(getattr(raw,"email","") or ""),str(metadata.get("first_name","") or ""))
    @staticmethod
    def _friendly(exc: Exception,fallback: str) -> str:
        text=str(exc).lower()
        if "already registered" in text or "already exists" in text: return "That email or name is already registered. Sign in, or use different account details."
        if "email not confirmed" in text: return "This Supabase project still requires email verification. Turn off Confirm email in Supabase Authentication settings."
        if "invalid login" in text or "invalid credentials" in text: return "Sign-in failed. Check your email and password, or create an account if you have not registered."
        if "your-project-id.supabase.co" in text or "name resolution" in text or "getaddrinfo" in text or "could not resolve" in text:
            return "Supabase is not configured yet. Replace the placeholder SUPABASE_URL in Streamlit secrets with your project URL."
        if "signup is disabled" in text or "signups not allowed" in text: return "Account creation is disabled in Supabase Auth settings."
        if "database error saving new user" in text: return "Supabase could not save the new user. Apply the CareBridge Supabase schema and check the Auth logs."
        if "invalid api key" in text or "invalid jwt" in text: return "The Supabase project URL or anonymous key is invalid. Check Streamlit secrets."
        if "rate" in text: return "Too many attempts were made. Wait a few minutes, then try again."
        return fallback
