# SCRAP Drone Studio — Production Readiness and Safety Case

## Actual scope
This release is a **production-engineering foundation**, not a certified flight-control product. Existing browser-based formation authoring, backend APIs, lighting tools, and reference repositories are retained. The new trajectory verifier and telemetry bridge are real server features. No direct aircraft-command or automated flight-control endpoint is provided.

## New APIs
- `POST /api/verification/trajectory`: offline continuous closest-approach checking for piecewise-linear trajectories. Checks drone separation throughout every interval, speed and altitude bounds, ordering and fleet consistency. Reports exact segment/time of minimum separation under the linear model. **Does not prove real-world collision avoidance**.
- `POST /api/bridge/telemetry`: authenticated ingestion of live telemetry samples from a separate adapter. Set `SCRAP_BRIDGE_KEY` to a random secret of 24 or more characters before use. Supply it in the `X-Bridge-Key` header. Accepts sample timestamps within 5 minutes of server time.
- `GET /api/bridge/telemetry/{drone_id}`: latest stored sample, including a staleness flag. Same header required.

## Hardware integration
ROS2, MRS UAV, PX4, ArduPilot and MAVLink projects in `reference/` are **reference sources**, not active flight adapters. Connect an independently secured, read-only adapter to the bridge. Avoid exposing raw ROS2 DDS, MAVLink UDP, or autopilot command channels to the public Internet. Do not enable aircraft actuation without an independent flight-safety architecture.

## Required before any operational flight deployment
1. Establish aircraft make/model, firmware versions, payload and LED controller interfaces.
2. Define intended jurisdiction, operating category, airspace, location, operator competency and permits.
3. Develop a documented hazard analysis and independent emergency procedures (loss of link, battery, GPS, geofence, weather, crowd safety).
4. Add hardware-in-the-loop and software-in-the-loop test plans, failure injection and environmental test coverage.
5. Validate clock synchronization, trajectory tracking error, wind envelopes, dynamic obstacle detection and uncertainty margins.
6. Add TLS termination, encrypted secret management, external identity provider/MFA, rate limiting, centralized audit collection, database backup/restore and disaster recovery.
7. Review dependencies and third-party licences, conduct penetration testing, and define patch/incident response SLAs.
8. Complete independent review and obtain applicable approvals. Retain signed test evidence, configuration baselines and operator training records.

## Limitations of trajectory model
The verifier models constant velocity between keyframes, with no controller dynamics, wind, sensor errors, GNSS uncertainty, time skew, rotor/propeller envelopes, takeoff/landing effects or moving obstacles. A `valid=true` result is **not a flight approval**.

## Liability
Software disclaimers and licence language do not waive mandatory legal obligations or prevent lawsuits. Have local aviation and technology counsel review commercial agreements, insurance and responsibilities.
