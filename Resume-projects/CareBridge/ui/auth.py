from __future__ import annotations
import streamlit as st
from src.auth import AuthError, SupabaseAuth, validate_signup
from ui.components import marketing_nav

def auth_screen(auth: SupabaseAuth,mode: str="signin"):
    marketing_nav()
    left,right=st.columns([1,1],gap="large")
    with left:
        st.markdown('''<div class="auth-story"><div class="mk-eyebrow">CareBridge account</div><h1>Keep every visit workspace connected to you.</h1><p>Return to preparation tasks, records, questions, and reviewed briefs across sessions.</p><div class="auth-point">✓ Organized visit preparation</div><div class="auth-point">✓ User-scoped record search</div><div class="auth-point">✓ Persistent reviewed visit briefs</div></div>''',unsafe_allow_html=True)
    with right:
        if mode=="signup":
            st.markdown('<div class="auth-head"><div class="cb-step">Create account</div><h1>Start preparing</h1><p>Your account keeps visits separated and available when you return.</p></div>',unsafe_allow_html=True)
            with st.form("signup"):
                first=st.text_input("First name",max_chars=80); email=st.text_input("Email"); password=st.text_input("Password",type="password"); confirm=st.text_input("Confirm password",type="password"); submitted=st.form_submit_button("Create Account",type="primary",width="stretch")
            if submitted:
                try:
                    validate_signup(email,password,confirm,first); response=auth.sign_up(email,password,first); user=auth.user(response)
                    if getattr(response,"session",None) and user: return ("authenticated",user)
                    st.error("The account was created, but automatic sign-in is disabled because Supabase still requires email confirmation. Turn off Confirm email in Supabase Authentication settings, then create the account again.")
                except AuthError as exc: st.error(str(exc))
            if st.button("Already have an account? Sign In",width="stretch"): return ("mode","signin")
        else:
            st.markdown('<div class="auth-head"><div class="cb-step">Welcome back</div><h1>Sign in to CareBridge</h1><p>Continue preparing your saved visits.</p></div>',unsafe_allow_html=True)
            with st.form("signin"):
                email=st.text_input("Email"); password=st.text_input("Password",type="password"); submitted=st.form_submit_button("Sign In",type="primary",width="stretch")
            if submitted:
                try:
                    response=auth.sign_in(email,password); user=auth.user(response)
                    if user: return ("authenticated",user)
                    st.error("CareBridge could not restore the authenticated user.")
                except AuthError as exc: st.error(str(exc))
            if st.button("New to CareBridge? Create Account",width="stretch"): return ("mode","signup")
    return None
