# Supabase password recovery configuration

CareBridge uses Supabase's supported recovery-token flow. In the Supabase Dashboard:

1. Set **Authentication → URL Configuration → Site URL** to the deployed CareBridge URL.
2. Add the deployed URL and `http://localhost:8501/**` to **Redirect URLs**.
3. In **Authentication → Email Templates → Reset Password**, set the action link to:

```html
<a href="{{ .RedirectTo }}?auth=reset&amp;token_hash={{ .TokenHash }}&amp;type=recovery">Reset password</a>
```

The token is single-use and is verified by Supabase before CareBridge accepts a new password. The reset request intentionally does not reveal whether an email is registered.
