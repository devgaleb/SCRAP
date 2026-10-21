# Multi-controller integration and aircraft-specific assurance

## Scope
This edition adds a versioned, aircraft-neutral **read-only** telemetry schema, controller capability contract, schema validation endpoints and regression tests. No flight commands, arming, motor control or aircraft actuation are exposed.

## Supported integration contracts (not live adapters)
- PX4: MAVLink telemetry gateway, firmware and airframe-specific mapping needed.
- ArduPilot: MAVLink telemetry gateway, firmware and airframe-specific mapping needed.
- MRS UAV System: ROS2 subscriber gateway, ROS distribution and message types needed.
- Custom hardware: implement a gateway that translates proprietary telemetry into `TelemetryEnvelope`.

The gateways are **not** included; the above are interface specifications, not claims of hardware compatibility.

## REST contracts
- `GET /api/aircraft/controller-types`: controller discovery.
- `POST /api/aircraft/validate-capabilities`: validate declared firmware/hardware capabilities.
- `POST /api/aircraft/validate-telemetry`: validate canonical telemetry shape; does not store or transmit to aircraft.
- Existing `POST /api/bridge/telemetry`: authenticated storage of the earlier sample schema using `SCRAP_BRIDGE_KEY`; no flight commands.

## Assurance evidence per aircraft variant
1. Exact aircraft identifier, mass, propulsion, power and flight-controller hardware revision.
2. Firmware build identifier, configuration checksum and supported protocol version.
3. Sensor calibration and accuracy, clock synchronization and telemetry loss characteristics.
4. Aircraft-specific hazard analysis and independent safety monitor design.
5. Simulation and hardware-in-the-loop test results with repeatable test cases.
6. Flight test plan, qualified personnel, operating limitations and signed evidence.
7. Cybersecurity threat model, secrets rotation, gateway network segmentation and incident response.
8. Applicable regulatory approval and independent review before operational deployment.

## Non-negotiable boundaries
Do not use this software as a sole source of separation assurance, geofencing, collision avoidance, or flight-critical command authority. Continuous linear-path checks do not model tracking errors, wind, sensor latency or nonlinear aircraft dynamics. Flight control remains with independently verified onboard systems.

## Local testing
`python -m pytest tests/test_aircraft_integrations.py -q`

## Deployment security
Use HTTPS behind a reverse proxy, protect the bridge secret, restrict gateway ingress by network and identity, retain immutable audit evidence, back up the database, and review dependency vulnerabilities. Existing application authentication and operational security have not undergone independent penetration testing.
