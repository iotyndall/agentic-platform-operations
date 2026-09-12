# Architecture: Shared Engine + Local Contract

## Principle

The central repository owns governance and reusable execution. Application repositories own only facts that are inherently local.

This separates **how autonomous engineering is governed** from **what makes a particular application safe, observable, and correct**.

The central operating rule is:

> **Agents reason. Deterministic software grants authority. Evidence moves the state machine forward.**

## Control-plane flow

```text
Runtime signals
      ↓
Observed operation + canonical incident
      ↓
Triage / orientation
      ↓
Policy + risk decision
      ↓
Reproduction agent
  green baseline → test-only failing evidence → immutable reproduction SHA
      ↓
Repair agent
  smallest patch → cannot edit reproduction → deterministic gates
      ↓
Independent review bound to exact candidate SHA
      ↓
Release authorization bound to review + CI + environment + rollback evidence
      ↓
Protected staging / production deployment
      ↓
Production probation
      ├── healthy → learning → close
      └── rollback authorized → rollback → recovery verification → learning → close
```

A durable operation record binds each stage together. The operation controller itself performs no network calls and holds no repository, merge, deploy, or rollback credentials. It validates legal transitions and evidence identity; separate deterministic workflows execute already-authorized actions.

## Control plane versus execution plane

The architecture deliberately separates three concerns:

1. **Reasoning plane** — narrow agents interpret evidence, write reproductions, propose repairs, review changes, and create lessons.
2. **Control plane** — deterministic gates and the operation controller decide whether evidence is sufficient to advance authority.
3. **Execution plane** — isolated GitHub jobs and project-specific adapters perform explicitly authorized repository, deployment, or recovery actions.

No model job should span all three planes.

## Durable operation record

Each incident operation records and hash-chains the exact evidence required to move through the lifecycle.

Important bindings include:

- known-good production SHA before the operation;
- immutable failing reproduction SHA;
- repair candidate SHA;
- independently reviewed SHA;
- released/deployed SHA;
- production verification evidence;
- authorized prior-known-good rollback SHA when recovery is required;
- recovery verification and learning evidence.

Branch names are convenient routing labels, not authority. State transitions rely on immutable identities and explicit evidence.

The canonical state model is documented in `docs/OPERATION_STATE_MACHINE.md`.

## Central responsibilities

The control-plane repository owns:

- autonomy policy and default prohibited actions;
- LOW/MODERATE/HIGH risk taxonomy and mechanical path classifier;
- Product, Product Review, Triage, Reproduction, Repair, Engineering Review, Release, Learning, and Security role contracts;
- incident, evidence, lesson, feature-spec, project-contract, and operation-record schemas;
- deterministic operation-state transition rules;
- deterministic CI orchestration;
- dependency/security ratchets and supply-chain pinning;
- test-first reproduction mechanics;
- bounded PR-only repair mechanics;
- independent review bound to an exact candidate SHA;
- protected release and rollback authorization gates;
- standard incident/PR/deployment evidence requirements;
- SLO/error-budget defaults and evaluation semantics;
- versioned mitigation/recovery runbooks;
- incident learning-library conventions;
- templates for thin project caller workflows and fail-closed execution adapters.

## Project responsibilities

Each application repository owns a small `.agentic/platform-ops.json` containing project-specific facts:

- runtime/package manager;
- install/typecheck/test/lint/build commands;
- migration, integration, browser, contract, and performance test commands when applicable;
- protected path expressions and escalation domains;
- known security-advisory baseline;
- deployment provider and environment names;
- approved evidence sources and retention;
- critical user journeys and health checks;
- project-specific external dependencies;
- SLO overrides/error-budget settings;
- explicitly authorized reversible mitigations;
- staging/production environment and rollback declarations;
- reproduction/repair eligibility configuration.

Domain monitors remain local when the signal cannot be generalized. A booking-handoff synthetic, tenant-isolation check, provider-specific database invariant, or application-specific SLO should be implemented close to the application and emitted into the common lifecycle rather than duplicated in central reasoning logic.

## Trust boundaries

### 1. Observation
Production monitors are read-only where possible. A failed monitor may create/dedupe an incident and initialize an observed operation; it does not repair code in the same workflow.

### 2. Triage and evidence
The triage role may classify impact/confidence and collect narrow redacted references. Logs, issue bodies, customer content, URLs, stack traces, provider messages, and external text are untrusted evidence—not instructions. Missing telemetry is reported as unknown/degraded coverage.

### 3. Reproduction
The reproduction role starts only after the existing baseline test suite passes. It may modify test/fixture surfaces only. Its output is accepted only if type/lint remain valid and the configured suite now fails. The resulting branch and commit SHA are immutable repair inputs.

### 4. Evidence freeze
The failing reproduction SHA is recorded before repair begins. The repair stage must consume that exact SHA and cannot redefine the proof of failure.

### 5. Repair
The repair role branches from the exact reproduction SHA. It cannot modify reproduction evidence, central policy/workflows, the local contract, or project-protected paths. It may publish a PR only.

### 6. Deterministic verification
Workflow code independently checks reproduction integrity, changed paths, blast radius, project commands, schema/data restrictions, and security rules. Model confidence cannot waive a failed gate.

### 7. Independent review
A different model/reviewer receives the incident, immutable reproduction, complete diff, deterministic evidence, architecture constraints, and rollback plan. The review attempts to disprove correctness and is tied to an exact PR head SHA. Any subsequent head change invalidates that review.

### 8. Release authorization
Only an already-reviewed immutable candidate may enter staging/production. CI evidence, review evidence, integrated tree identity, environment policy, SLO state when enabled, and rollback availability must agree. PR/model workflows do not receive production credentials.

### 9. Deployment and production probation
A successful deployment is not treated as closure. The exact deployed SHA enters `production_probation`, where critical user journeys and runtime health evidence determine whether the release becomes healthy or requires recovery.

### 10. Recovery
Fresh regressions prioritize a compatible pre-approved rollback over speculative forward repair. Rollback requires explicit contract authorization, a distinct prior-known-good SHA, schema compatibility, bounded release distance, incident evidence, and post-recovery verification. Direct production SQL/customer-data remediation remains prohibited.

### 11. Learning
Resolved material incidents become curated verified records plus a durable improvement. Historical evidence is never rewritten to match a later hypothesis.

## Local caller pattern

A connected repository needs only thin wrappers such as:

```yaml
jobs:
  ci:
    uses: iotyndall/agentic-platform-operations/.github/workflows/reusable-node-ci.yml@<immutable-central-sha>
```

The deterministic operation controller can likewise be consumed through its composite action pinned to the same reviewed central revision.

The reusable workflow checks out the caller repository and reads `.agentic/platform-ops.json` from that caller. The central repo controls shared execution logic while the application controls its declared facts and business invariants.

## Current integration boundary

The controller, state schema, persistence wrapper, engineering review, release authorization, post-deploy verification, and rollback authorization mechanisms exist independently.

The current build step is to wire existing stages into the operation record one transition at a time without merging their permission domains. Until that wiring and an end-to-end behavioral canary are complete, existing stage-specific evidence remains authoritative and the operation record must never be treated as a bypass around release/recovery gates.

## Versioning and blast-radius control

This repository is infrastructure code for every connected project. Therefore:

1. all changes happen by PR;
2. third-party actions are pinned to immutable SHAs;
3. product templates explicitly pin central reusable workflows and composite actions;
4. central CI negative-tests safety invariants and prevents direct repair→promotion authority;
5. reviewed central versions are cut intentionally;
6. product repos pin an immutable central version/commit rather than `main`;
7. rollout occurs project-by-project, using proving-ground repositories before wider adoption;
8. the platform itself should continuously pass a disposable end-to-end canary lifecycle before broader autonomous release authority is increased.

Centralization reduces duplication only if it does not become a single moving failure point. Versioned rollout, local contracts, deterministic evidence, and behavioral self-certification provide that containment.
