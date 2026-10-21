# Verification and validation plan

## Gate 0 — requirements baseline
Identify aircraft, firmware, controller, propeller envelope, LED payload, flight mode, geography, airspace, operator and applicable regulatory route. Freeze versioned requirements and acceptance criteria.

## Gate 1 — deterministic software tests
Run `python -m unittest discover -s tests -v`. Record OS, Python version, dependency hashes, test results and commit ID. Independently review collision calculations and numeric tolerances. Add property tests, malformed-input tests and high-load testing.

## Gate 2 — software-in-the-loop
Exercise nominal flights and failures: GNSS loss, stale telemetry, time drift, network jitter, dropped packets, controller saturation, battery warnings, geofence excursions and interrupted choreography. Record actual-vs-commanded tracks and uncertainty bounds.

## Gate 3 — hardware-in-the-loop
Use an isolated test rig, appropriate supervision and aircraft-specific independent failsafes. Verify authority separation, link-loss behaviour, emergency termination, sensor faults and LED interference. Do not rely on browser availability for flight safety.

## Gate 4 — operational assessment
Complete site-specific risk assessment, insurance, operator competency, permissions, emergency planning, maintenance, flight logs and third-party independent review. Regulatory approval cannot be substituted by passing tests.

## Release decision
Only an identified accountable authority can sign off the actual aircraft and operation. The default decision is **NOT APPROVED FOR FLIGHT**.
