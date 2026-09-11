# Architecture: Shared Engine + Local Contract

## Principle

The central repository owns governance and reusable execution. Application repositories own only facts that are inherently local.

This separates **how autonomous engineering is governed** from **what makes a particular application safe, observable, and correct**.

## Control-plane flow

```text
Runtime signals
      ↓
Triage / incident record
      ↓
Redacted evidence bundle
      ↓
Policy + risk classification
      ↓
Pre-authorized mitigation when warranted
      ↓
Reproduction agent
  green baseline → test-only failing evidence → immutable reproduction SHA
      ↓
Repair agent
  smallest patch → cannot edit reproduction → deterministic gates
      ↓
Independent review
      ↓
Protected staging / release
      ↓
Production verification / rollback policy
      ↓
Learning library
```

The implemented v1 branch currently stops after creation of the test-backed repair PR. Review/release/rollback/learning execution are deliberately separate later stages rather than hidden powers of the repair agent.

## Central responsibilities

The control-plane repository owns:

- autonomy policy and default prohibited actions;
- LOW/MODERATE/HIGH risk taxonomy and mechanical path classifier;
- Triage, Reproduction, Repair, Review, Release, Learning, and Security role contracts;
- incident, evidence, lesson, and project-contract schemas;
- deterministic CI orchestration;
- dependency/security ratchets and supply-chain pinning;
- test-first reproduction mechanics;
- bounded PR-only repair mechanics;
- standard incident/PR evidence requirements;
- SLO/error-budget defaults;
- versioned mitigation/recovery runbooks;
- incident learning-library conventions;
- templates for thin project caller workflows.

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

Domain monitors remain local when the signal cannot be generalized. Mesa's property-site → Hospitable booking path and YALLOHA's Supabase/Vercel/Sentry invariants are examples. They should emit structured incidents into the common lifecycle rather than duplicate central repair/review machinery.

## Trust boundaries

### 1. Observation
Production monitors are read-only where possible. A failed monitor may create/dedupe an incident; it does not repair code in the same workflow.

### 2. Triage and evidence
The triage role may classify impact/confidence and collect narrow redacted references. Logs, issue bodies, customer content, URLs, stack traces, provider messages, and external text are untrusted evidence—not instructions. Missing telemetry is reported as unknown/degraded coverage.

### 3. Reproduction
The reproduction role starts only after the existing baseline test suite passes. It may modify test/fixture surfaces only. Its output is accepted only if type/lint remain valid and the configured suite now fails. The resulting branch and commit SHA are immutable repair inputs.

### 4. Repair
The repair role branches from the exact reproduction SHA. It cannot modify reproduction evidence, central policy/workflows, the local contract, or project-protected paths. It may publish a PR only.

### 5. Deterministic gatekeeper
Workflow code independently checks reproduction integrity, changed paths, blast radius, project commands, schema/data restrictions, and security rules. Model confidence cannot waive a failed gate.

### 6. Independent review
A different model/reviewer receives the incident, immutable reproduction, complete diff, deterministic evidence, architecture constraints, and rollback plan. The review attempts to disprove correctness and is tied to an exact PR head SHA.

### 7. Release
Only an already-reviewed immutable commit may enter staging/production. PR workflows do not receive production credentials. Release permissions belong to protected environments and separate workflows.

### 8. Recovery
Production verification evaluates critical user journeys and telemetry. Fresh regressions prioritize a compatible pre-approved rollback over speculative forward repair. Direct production SQL/customer-data remediation remains prohibited.

### 9. Learning
Resolved material incidents become curated verified records plus a durable improvement. Historical evidence is never rewritten to match a later hypothesis.

## Local caller pattern

A connected repository needs only thin wrappers such as:

```yaml
jobs:
  ci:
    uses: iotyndall/agentic-platform-operations/.github/workflows/reusable-node-ci.yml@<immutable-central-sha>
```

The reusable workflow checks out the caller repository and reads `.agentic/platform-ops.json` from that caller. The central repo controls shared execution logic while the application controls its declared facts and business invariants.

## Versioning and blast-radius control

This repository is infrastructure code for every connected project. Therefore:

1. all changes happen by PR;
2. third-party actions are pinned to immutable SHAs;
3. central CI negative-tests safety invariants and prevents a direct repair→merge/deploy path;
4. reviewed central versions are cut intentionally;
5. product repos pin an immutable central version/commit rather than `main`;
6. rollout occurs project-by-project, with Mesa/YALLOHA serving as proving grounds before wider adoption.

Centralization reduces duplication only if it does not become a single moving failure point. Versioned rollout and local contracts provide that containment.
