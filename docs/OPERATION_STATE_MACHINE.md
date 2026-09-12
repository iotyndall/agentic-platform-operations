# Operation Controller and State Machine

## Purpose

The operation controller is the deterministic spine of the autonomous engineering loop.

Agents may observe, classify, reproduce, repair, review, and learn. They do not advance their own authority. A state transition occurs only when machine-verifiable evidence satisfies the controller's requirements.

This implements the control-plane rule:

> Agents reason. Deterministic software grants authority. Evidence moves the state machine forward.

The controller has **no network, repository-write, merge, deploy, or rollback authority**. It validates one operation record and emits the next record. GitHub workflows and project adapters remain responsible for executing already-authorized actions.

## Canonical lifecycle

```text
observed
  ↓
oriented
  ↓
decided
  ↓
reproducing
  ↓
evidence_frozen
  ↓
repairing
  ↓
verifying
  ↓
reviewed
  ↓
release_authorized
  ↓
deployed
  ↓
production_probation
  ├─────────────── healthy ──────→ learning ──────→ closed
  │
  └→ rollback_authorized
          ↓
       rolled_back
          ↓
     recovery_verified ──────────→ learning ──────→ closed
```

Any active state may instead transition to `escalated` when evidence or policy is ambiguous. `closed` and `escalated` are terminal.

The controller intentionally does not support skipping intermediate states. A successful model response is not evidence for a later authority state.

## Immutable bindings

The genesis event binds the operation's identity as hashed evidence:

- `operation_id`;
- `repository`;
- `incident_issue`;
- `source_type`;
- `signal`;
- optional `production_before_sha`.

The validator replays those values from the genesis event and compares them with the top-level record. A complete evidence chain therefore cannot be relabeled onto a different operation, repository, or incident without invalidating validation.

The record then binds six important code identities:

- `production_before_sha` — release believed healthy before the operation;
- `reproduction_sha` — immutable red reproduction evidence;
- `candidate_sha` — proposed repaired code;
- `reviewed_sha` — exact candidate independently reviewed;
- `deployed_sha` — exact candidate released to production;
- `prior_known_good_sha` — rollback target authorized after a failed probation.

Transitions enforce identity, not branch names. Repair must consume the exact frozen reproduction SHA; independent review must PASS the exact candidate SHA; CI and release evidence must reference that same candidate SHA; deployment must deploy that candidate; healthy probation must verify the deployed SHA; rollback must restore the authorized known-good SHA; and recovery verification must verify that rollback target.

A branch moving after review therefore invalidates the evidence chain rather than silently inheriting approval.

## Deterministic terminal outcome

The controller also binds `resolution_path` when the operation enters `learning`:

- `healthy` when learning follows a healthy production probation;
- `rolled_back` when learning follows `recovery_verified`.

Closure evidence must match that bound path. The terminal result therefore cannot be rewritten later as a different outcome merely by changing the closure summary.

## Hash-chained event history

Every operation transition appends an event containing its sequence number, prior and next states, deterministic actor identity, evidence object, previous event SHA-256, and current event SHA-256.

The digest is calculated over canonical JSON excluding the event's own digest. The controller replays the complete history on every validation. If earlier evidence, a state, sequence number, identity field, or digest link changes, validation fails.

This is tamper-evident rather than a replacement for GitHub audit logs or cryptographic artifact attestation. Later versions can sign or attest the event chain without changing the state-machine semantics.

## Evidence required by state

| Target state | Minimum deterministic evidence |
| --- | --- |
| `observed` | operation/repository/incident identity + source type + signal + optional known-good production SHA |
| `oriented` | kind, severity, confidence |
| `decided` | autonomy level, risk, authorization |
| `reproducing` | reproduction branch |
| `evidence_frozen` | full reproduction SHA, RED result, tests-only proof |
| `repairing` | repair branch + exact frozen reproduction SHA |
| `verifying` | candidate SHA + proof reproduction evidence was unchanged |
| `reviewed` | exact candidate SHA + PASS + engineering-ready |
| `release_authorized` | candidate SHA = CI SHA = reviewed SHA + release authorization |
| `deployed` | exact candidate SHA + production environment + deployment id |
| `production_probation` | start time + required production checks |
| `healthy` | PASS production verification bound to deployed SHA + evidence hash |
| `rollback_authorized` | deployed SHA + distinct prior-known-good SHA + authorization + schema compatibility |
| `rolled_back` | successful rollback to authorized target |
| `recovery_verified` | PASS production verification bound to rollback target |
| `learning` | nonempty lesson/summary + nonempty durable improvement reference; controller binds resolution path |
| `closed` | resolution matching the bound completed path + summary |
| `escalated` | explicit escalation reason |

These checks complement, rather than replace, the existing release, rollback, security, SLO, and environment gates.

## CLI

Initialize:

```bash
python scripts/operation_controller.py init \
  --operation-id op-2026-000184 \
  --repository owner/service \
  --incident-issue 184 \
  --source-type synthetic \
  --signal 'critical journey failed' \
  --production-before-sha <40-char-sha> \
  --output operation.json
```

Advance one state:

```bash
python scripts/operation_controller.py transition \
  --record operation.json \
  --to oriented \
  --evidence '{"classification":{"kind":"incident","severity":"P1","confidence":0.98}}' \
  --output operation.next.json
```

Validate a persisted record:

```bash
python scripts/operation_controller.py validate --record operation.json
```

The command exits non-zero on malformed JSON, a broken hash chain, an illegal state transition, stale SHA evidence, missing genesis or transition evidence, identity relabeling, closure-path mismatch, or top-level fields that disagree with replayed history.

## Production probation

`deployed` is deliberately not equivalent to `done`.

The next mandatory state is `production_probation`. During probation, the application-specific workflow should execute the critical journeys declared in `.agentic/platform-ops.json`, along with the telemetry/SLO checks appropriate to that service.

If those checks pass for the exact deployed SHA, the operation may enter `healthy`.

If they fail at the configured threshold and the existing rollback gate authorizes recovery, the operation enters `rollback_authorized`. Recovery then follows the known-good release path before diagnosis continues.

This encodes the operational priority:

> Recover first. Diagnose second.

Forward repair remains a new bounded engineering operation; production recovery does not grant an agent permission to improvise directly against production.

## Workflow integration order

This change establishes the controller semantics and CI proof. The next wiring step should be incremental:

1. incident intake creates the initial `observed` record;
2. triage/reproduction/repair/review workflows append controller events;
3. release gate records `release_authorized`;
4. deployment records `deployed` and immediately enters `production_probation`;
5. post-deploy verification records `healthy` or publishes rollback evidence;
6. rollback workflow records authorization, rollback, and recovery verification;
7. learning/closure records the durable lesson and closes the operation.

Until persistence is wired end-to-end, existing workflow evidence remains authoritative. The controller must not be treated as a release bypass.

## Autonomy ladder

The operation record also creates a future foundation for earned autonomy:

- **Level 0 — Observe:** diagnosis only.
- **Level 1 — Repair:** bounded reproduction/repair; human release.
- **Level 2 — Release:** eligible low-risk classes may release after deterministic gates.
- **Level 3 — Recover:** eligible classes may release, enter probation, and execute pre-authorized rollback.

Autonomy should be granted by failure class and accumulated evidence, never by model self-assessment alone.
