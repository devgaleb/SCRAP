# SCRAP Drone Studio Ultimate

A working offline-first browser application for **drone fleet registration, mission route design, light-show keyframe choreography, animated 2D previews, perspective formation visualisation, CSV altitude analysis, and JSON project import/export**.

## Run

Open `app/index.html` in a modern browser, or from the `app` folder run `python -m http.server 8080` and visit `http://localhost:8080`.

No external dependencies or API keys are required. Workspace data persists in browser localStorage. Audio is loaded locally and is not persisted. Mission waypoints use normalized preview coordinates, **not GPS**. The text formation is an illustrative pattern rather than actual font outlines.

## Important limitations

This release is a functional **planning and visualization prototype**, not a certified drone-control product. It does **not** connect to real aircraft, implement ROS2/MAVLink/MAVSDK bridges, validate flight paths in physical units, offer true 3D physics, run AI models, or transmit flight commands. The provided third-party repositories are preserved in `reference/` for future engineering integration, not silently merged into a working flight stack. Never use exported trajectories as flight-ready instructions.

## Supplied source projects

- `reference/GEARdrones-main/` — embedded drone firmware and related assets.
- `reference/mrs_uav_system-ros2/` — ROS2/MRS system source.
- `reference/drone-controllers-main/` — controller library source.
- `reference/drone-control-system-master/` — C++ control system source.
- `reference/specification.txt` and `reference/blueprint.docx` — original requirements.

Source repositories may have their own licenses, build environments and hardware requirements. Review those before redistributing or compiling. Integrations need separate safety engineering, authentication, SITL testing and appropriate aviation permissions.

## Server edition (added)

This package now includes a **working authenticated FastAPI server**, persistent SQLite storage, user-scoped fleet/mission/show/telemetry/map/settings records, audit events, API documentation, a read-only preview WebSocket and an operations console. This is a **production-oriented application foundation**, not a certified production flight system. The browser visual studio still saves its data locally; the operations console stores separate server-side records. There is not yet automatic synchronization between the two interfaces.

### Run the server

Install Python 3.11+ and run `start.bat` (Windows) or `./start.sh` (Linux/macOS). Open `http://127.0.0.1:8080/operations` for the account-backed records console, `http://127.0.0.1:8080/` for the visual studio, and `/docs` for the API. Use a unique 12+ character password. Database defaults to `data/studio.sqlite3`, override with `SCRAP_DB`. Run `python -m pytest tests -q` to execute API tests.

### Security and deployment limitations

For internet exposure, deploy behind HTTPS with a reverse proxy, rate limiting, CSRF/origin controls appropriate to the deployment, secrets management, backup/restore, security monitoring and external review. Current auth uses one-day bearer tokens stored in session storage, PBKDF2 password hashes, and no login throttling. SQLite is intended for small deployments, not distributed high-availability production. The WebSocket accepts **simulation previews only**; it does not authenticate sessions and must not be exposed publicly without an authentication layer. There is no actual drone telemetry bridge, aircraft command pathway, geofencing, collision avoidance, flight certification, AI model, or automatic ROS2/MAVLink/PX4/MRS integration. Reference projects are supplied as sources for future engineering, not functioning integrations.


## Light Automation Studio
Open `/lights` when running the server. Cue-based offline LED choreography includes pulse, strobe, fade, rainbow and solid modes, presets, preview timeline, and JSON export. `/api/lights/preview` compiles bounded simulation-only frames. No flight control or physical LED adapter is provided.


---

# Safety, legal responsibilities, and deployment guide

**Document status:** Informational template, not legal advice, an insurance policy, a certification, or a guarantee against lawsuits. Obtain advice from a qualified lawyer in every jurisdiction where the software is supplied or operated. Review and adapt these terms before public or commercial distribution.

## 1. What this software does and does not do

The browser studio and lights module create visual simulations, cue schedules, and JSON exports. The server stores user records and provides simulation preview APIs. No physical aircraft or LED control is implemented in this release. Data displayed in simulation is not real telemetry. Exported routes, formations, cues and previews are **not approved flight plans or flight-ready commands**. Third-party source projects in `reference/` are provided for engineering evaluation and are not integrated operational connectors.

## 2. Operator and integrator responsibilities

Before connecting any physical aircraft or lighting controller, the person or organization responsible for the operation must independently:

- Confirm applicable aviation laws, airspace restrictions, authorizations, registration, pilot competency, insurance, privacy and data-protection obligations.
- Assess the site, public access, weather, aircraft airworthiness, radio interference, lighting visibility, and nearby people, property, and other airspace users.
- Establish suitable separation distances, exclusion areas, crew roles, communication plans, incident procedures, and an emergency stop / return / landing process appropriate to the equipment.
- Test adapters, aircraft firmware, synchronization, LED cues, and communication-loss behavior in isolated simulation and controlled authorized environments before deployment.
- Perform independent engineering review and safety validation of geofencing, collision prevention, battery limits, failsafes and human override before any real-world operation.
- Maintain operational logs, training, maintenance records, and approvals required by law or contracts.

Do not rely on the application alone for collision avoidance, aircraft separation, flight authorization, emergency response, or compliance decisions. Do not fly or conduct public drone shows using this prototype as a flight-control system.

## 3. UK and international regulatory considerations

In the United Kingdom, consult the current UK Civil Aviation Authority (CAA) rules for unmanned aircraft, applicable operating categories, permissions, and airspace restrictions. A public synchronized drone display may require approvals beyond those for ordinary drone flights. Rules differ outside the UK and can change. The software does not check or guarantee compliance with any jurisdiction's requirements.

## 4. Proposed responsibility allocation for commercial terms

A commercial licence or customer agreement may state that the customer/operator is responsible for planning, permits, flight crew, site safety, hardware maintenance, training, insurance and regulatory compliance, while the software supplier describes the software's actual functionality, known limitations, security commitments, support obligations and any agreed warranties. Any limitation of liability or indemnity must be drafted for the relevant jurisdiction and cannot exclude liabilities that law prohibits excluding. Do not describe this README as a binding agreement automatically accepted by all users.

**Suggested notice for a future terms-of-service review (not final legal wording):**

> SCRAP Drone Studio is provided for planning, design, record management, and simulation unless a separately documented and validated hardware integration is expressly supplied. The customer is responsible for obtaining required approvals and ensuring safe, lawful operation of any aircraft or lighting equipment. The provider makes no representation that simulation output is safe or authorized for real-world flight. Any warranties, exclusions, indemnities and liability limits are governed by the applicable signed agreement and mandatory law.

A lawyer should review customer acceptance flows, consumer-rights protections, negligence, product liability, data-protection duties, security obligations, and enforceability before commercial release. A disclaimer does not prevent someone filing a claim and does not automatically defeat one.

## 5. Setup and operating instructions

### Local visual studio

Open `app/index.html` in a modern browser. Local design data is held in browser storage and may be lost when the browser is cleared. Export JSON backups regularly. Do not treat the editor's normalized preview coordinates as GPS coordinates.

### Server

Install Python 3.11+ and the dependencies in `requirements.txt`. Use `start.bat` on Windows or `./start.sh` on Linux/macOS where available. Visit `http://127.0.0.1:8080/` for the studio, `/operations` for account-backed records, `/lights` for lighting cues, and `/docs` for the API. Keep the default service bound to a trusted local network only.

### Light automation

Open `/lights`, create cues, choose effects and timings, preview the simulated sequence, and export the show data. The preview compiler at `/api/lights/preview` creates simulation frames only. There is no physical LED transmitter or real-aircraft synchronization. Verify any future adapter's timing, current/power limits, communications, and safe-failure behavior independently.

### Testing

Run `python -m pytest tests -q` from the project root with test dependencies installed. Passing these tests is not flight certification or proof of safety. Confirm startup scripts and dependency compatibility on the target operating system.

## 6. Security checklist before internet deployment

- Add TLS/HTTPS, secure reverse-proxy configuration, authentication for every WebSocket, and strict CORS/origin controls.
- Add login throttling, secure token rotation, authorization tests, secrets management, logging, vulnerability scanning, and independent penetration testing.
- Implement database backups and tested recovery procedures, monitoring, incident response, and software update controls.
- Keep hardware command pathways isolated from public-facing endpoints. Require explicit authorization and independent safety controls for any future real-world control feature.
- Create a privacy notice and data-retention policy where user accounts, telemetry, logs, video, or location data are collected.

**Do not expose the current server directly to the public internet.** Its unauthenticated simulation WebSocket and other documented security gaps require remediation.

## 7. Third-party software and intellectual property

The bundled `reference/` projects may be subject to separate licences, notices, attribution, patents, and redistribution restrictions. Audit each repository's actual licence and dependencies before distributing or selling the combined package. Inclusion does not establish permission to relicense another author's work.

## 8. Incident and support policy

If a defect, unexpected behavior, or suspected security compromise occurs, stop using the affected feature, preserve relevant logs without exposing private data, notify the responsible operator or administrator, and investigate before resuming. Report suspected safety-critical defects to the software maintainer and follow applicable reporting requirements. Do not conceal known defects or claim unverified flight readiness.

## 9. Release-readiness checklist

- [ ] Legal counsel has reviewed distribution terms and jurisdiction-specific liability language.
- [ ] Third-party licences and dependencies have been audited.
- [ ] All advertised integrations have real end-to-end tests, not simulated substitutes.
- [ ] Security audit, backup/restore, authentication and access controls are complete.
- [ ] Independent hardware, flight and emergency-response validation is complete before physical use.
- [ ] Regulatory permissions, operator training and insurance have been confirmed for each operation.
- [ ] Customer documentation clearly distinguishes simulation, beta, and certified capabilities.

**Bottom line:** This package is suitable as a development foundation and offline simulation tool. It is not presently a certified production drone-flight platform. Neither this README nor a waiver makes the developer immune from legal claims.

## Advanced Engineering Studio (new)

Open `/advanced` after starting the server. This is an implemented parametric choreography workspace with circle, grid, helix and heart formation generation, 3D coordinate keyframes, JSON import, keyframe validation, and ZIP exports with SHA-256 manifests. The API endpoints are POST `/api/studio/generate`, `/api/studio/validate`, and `/api/studio/export`. Open `/docs` for schemas. These tools perform real calculations and create downloadable project data; they are not fake UI controls.

Validation checks keyframe drone counts, duplicated timestamps, pointwise drone separation, maximum keyframe-to-keyframe average speed, and altitude thresholds. **It does not guarantee collision-free trajectories between keyframes, aircraft compatibility, legal compliance, safe weather, or permission to fly.** Exports intentionally do not include executable aircraft commands. Flight-critical integrations must be separately engineered, tested and authorized. The API currently has no hardware command interface. No disclaimer alone eliminates developer or operator legal liability.

For production deployments: terminate HTTPS at a reverse proxy, restrict network exposure, enable backups and log rotation, perform security review, configure proper identity/role management, test your integration adapters in simulation, and complete a safety case before connecting aircraft. The SQLite backend is suited to smaller single-instance deployments; a managed database and migration strategy are recommended for multi-instance installations.


## Safety assurance edition
Read `assurance/SAFETY_CASE.md`, `assurance/VALIDATION_PLAN.md`, `assurance/SECURITY_DEPLOYMENT.md`, and `assurance/EVIDENCE_REGISTER.json`. This package is **NOT CERTIFIED** and **NOT APPROVED FOR FLIGHT**. The additional automated tests are limited offline checks and do not constitute flight validation.


## Multi-controller integration edition
See [MULTI_CONTROLLER_INTEGRATION.md](MULTI_CONTROLLER_INTEGRATION.md) for controller contracts, endpoints, evidence requirements and safety boundaries. The edition adds validation interfaces, **not** live flight adapters or certification.


## Final production engineering extension (2026-10-21)

New authenticated REST routes under `/api/assurance`: `GET /requirements`, `POST /aircraft`, `GET /aircraft`, `POST /evidence`, and `GET /readiness/{aircraft_id}`. Register exact aircraft models, serial numbers, controller hardware revisions, firmware versions and SHA-256 hashes, operating environments, jurisdictions, regulatory categories and approval references. Attach traceable verification evidence with reviewer and method. The readiness report always states certification and flight release are **not granted**.

See `assurance/CERTIFICATION_MATRIX.md`, `assurance/RELEASE_GATE.md`, and `assurance/AIRCRAFT_CONFIGURATION_TEMPLATE.json`. This is a real evidence registry, not a certification authority, and not a live flight controller.

## Universal firmware trust upgrade
See [FIRMWARE_TRUST_AND_FLIGHT_ASSURANCE.md](FIRMWARE_TRUST_AND_FLIGHT_ASSURANCE.md) for operator key registration, signed artifact manifest verification, controller compatibility records, limitations, and deployment controls. API endpoints: `POST /api/trust/keys`, `POST /api/trust/compatibility`, `GET /api/trust/compatibility`, `POST /api/trust/verify-manifest`. These features do not verify installed firmware or authorize aircraft flight.
