# Firmware trust and aircraft-specific verification

## Current implementation
The `/api/trust` endpoints allow operators to register Ed25519 verification public keys, record hardware/firmware compatibility evidence, and verify a canonical JSON manifest signature against a firmware SHA-256 digest supplied by the caller. Trust keys and evidence are stored persistently. No flight commands are exposed.

## Important trust boundaries
1. Registration of a public key is **not** independent verification of its manufacturer ownership. Obtain and confirm key fingerprints out of band using authenticated manufacturer channels.
2. The manifest verifier **does not receive or hash firmware bytes**. Compute SHA-256 of the actual downloaded artifact independently and compare with `artifact_sha256` in the manifest. Only a correctly signed manifest establishes that the signer endorsed that digest.
3. This process does **not** attest to firmware installed on an aircraft. Installed firmware identity needs device-specific secure boot, hardware root of trust, signed attestation, and physical tests where supported.
4. An operator-reviewed compatibility record is not proof of physical compatibility, safe flight or certification.
5. Key administration uses `SCRAP_TRUST_ADMIN_KEY` (at least 32 characters). Protect it in a secret manager; use TLS, reverse-proxy rate limiting, backups, monitoring and independent security review before network exposure.
6. Firmware signing varies by PX4/ArduPilot board and bootloader. The Ed25519 manifest scheme in this project is a **separate application-layer artifact attestation scheme**; it must not be represented as the native vendor firmware signing format.

## Setup
Install requirements with `python -m pip install -r requirements.txt`. Start as described in README. Set `SCRAP_TRUST_ADMIN_KEY` and visit `/docs`. Register a verified public key using `POST /api/trust/keys` and `x-trust-admin-key` header. Submit compatibility records using `POST /api/trust/compatibility`. Use `POST /api/trust/verify-manifest` to verify a signed manifest.

## Certification evidence checklist
- Aircraft model, serial, mass, propulsion and battery configuration
- Controller board revision, bootloader version, firmware release and hashes
- Flight envelope, operating location, airspace, weather and population exposure
- Documented command/telemetry interface with fault and stale-data handling
- Bench testing, software-in-loop, hardware-in-loop and instrumented flight trials
- Independent safety assessment, cybersecurity testing and regulatory authorization

## Scope
Planning, read-only telemetry, evidence management, artifact signature verification and offline simulation only. **Not a certified flight-control system**. Do not use as sole authority for real aircraft flight.
