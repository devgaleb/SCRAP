# SCRAP Drone Studio — Safety case (DRAFT / NOT APPROVED)

## Claim C0
The software is safe for a specified flight operation. **NOT ESTABLISHED. No authorization to fly follows from this repository.**

## Evidence register
| ID | Claim | Evidence required | State |
|---|---|---|---|
| C1 | Trajectories satisfy bounded kinematic assumptions | Property-based and numerical verification, independent review | OPEN |
| C2 | Aircraft maintain safe separation in flight | HIL/SIL, latency/wind/GNSS uncertainty tests, independent monitoring | OPEN |
| C3 | Flight controls fail safely | Redundant safeguards, command authority model, hardware tests | OPEN |
| C4 | Cybersecurity protects control authority | Threat model, pen test, key lifecycle, access review | OPEN |
| C5 | Operations satisfy applicable aviation rules | Jurisdiction, operation category, approved risk assessment and permissions | OPEN |
| C6 | Configuration and test evidence are traceable | Versioned firmware, airframes, test reports and signed approvals | OPEN |

## Safety invariants
- The browser/server must never directly command aircraft in this edition.
- No simulation, model-check, or software test may be labelled certification.
- Missing telemetry, stale telemetry or unknown position must be treated as unknown, never safe.
- Failed or incomplete verification must block export marked `verified`.
- The flight operator retains independent emergency-stop / flight termination capabilities appropriate to the aircraft and operation.

## Hazard log starter
| Hazard | Example causes | Required controls |
|---|---|---|
| Loss of separation | tracking error, clock skew, GPS degradation | uncertainty margins, independent proximity monitor, validated abort behaviour |
| Uncommanded motion | authentication failure, faulty adapter | strict authority boundaries, command signing, hardware interlocks |
| Loss of link | RF interference, infrastructure failure | independently validated aircraft failsafe |
| Crowd overflight | geofence error, bad mission plan | operational exclusion zones, approvals, independent review |
| Battery exhaustion | degraded pack, unexpected wind | reserves, continuous monitoring, tested contingency |

This file is a starting template, not a safety assessment, legal advice, conformity declaration or certificate.
