# Certification and approval matrix

**Status: no aircraft certified, no flight authorisation granted.** These fields must be filled with verified aircraft-specific evidence, not assumed.

| Area | Required evidence | Accountable reviewer |
|---|---|---|
| Aircraft and hardware | Serial, mass, controller board revision, wiring and redundancy | Aircraft integrator |
| Firmware | Exact version, signed build/provenance SHA-256, configuration and change control | Firmware maintainer |
| Intended operation | Indoor/outdoor, VLOS/BVLOS, site, altitude, airspace, crowd exposure, weather limits | Operator |
| Regulatory basis | Country, aviation authority, operating category, approvals, insurance and pilot competency | Aviation compliance specialist |
| Safety | Hazard analysis, geofencing, emergency response, loss-of-link and recovery | Independent safety assessor |
| Software | Requirements traceability, static analysis, security review, unit/integration tests | Software assurance team |
| Verification | SITL, HIL, ground tests, controlled flight tests, anomaly closure | Independent test team |
| Release | Signed release approval and operational restrictions | Responsible accountable person |

## UK considerations

For operations in the United Kingdom, determine the applicable UK CAA rules and permissions for the specific operation. Do not assume that light shows, swarms, BVLOS flights or operations near people are automatically authorised. Check the current CAA guidance and obtain professional advice. Other jurisdictions require separate assessments.

## Integration boundary

All adapters are read-only by default. There is no arming, take-off, landing, motor or navigation command API in this release. Firmware versions and approval references are recorded, not independently attested.
