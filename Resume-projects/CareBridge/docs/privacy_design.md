# Privacy design

- Minimize optional data collection and begin every new database in a clean empty state.
- Scope every query by patient identity before search or generation.
- Encrypt transport and managed storage in a production deployment.
- Use short-lived sessions, least-privilege roles, explicit consent, and expiring shares.
- Record access, exports, grants, revocations, and administrative overrides in append-only audit logs.
- Never log raw document text, medication lists, or assistant prompts in general application logs.
- Provide deletion, export, consent withdrawal, and sharing-revocation controls.

This portfolio build is not production-certified for protected health information.
