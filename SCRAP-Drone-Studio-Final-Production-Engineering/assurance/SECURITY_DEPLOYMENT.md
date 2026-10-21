# Secure deployment baseline (not yet implemented end-to-end)

- Place application behind TLS 1.3 reverse proxy, restrict allowed origins and use secure cookies.
- Do not expose development FastAPI, ROS2 DDS or MAVLink command ports to the Internet.
- Use managed secrets, rotate bridge keys, restrict telemetry ingestion by network and identity.
- Add MFA and role-based authorization for operations; require separate human approval for any future aircraft control.
- Use immutable audit collection, dependency scanning, backup/restore drills and a patching policy.
- Threat model includes replayed telemetry, compromised browser sessions, rogue adapters, clock skew, denial of service and malicious project files.
- Do not represent this edition as penetration tested or production hardened.
