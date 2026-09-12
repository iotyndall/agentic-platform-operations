# Agentic Platform Operations

Central GitHub-centered control plane for autonomous software engineering, reliability, product definition, and maintenance across current and future projects.

The operating model is **shared engine + local contract**:

- this repository owns reusable policy, product-intake, CI/security/reproduction/repair/review/release/recovery machinery, deterministic operation-state control, role definitions, runbooks, schemas, SLO defaults, and project templates;
- each application repository keeps a small `.agentic/platform-ops.json` describing only its unique commands, infrastructure, protected paths, evidence sources, environments, critical user journeys, SLOs, approved mitigations, and release constraints;
- application-specific runtime monitors stay close to the application when domain behavior cannot be generalized, but they feed the common incident/evidence/reproduction/repair/review/release/recovery/learning lifecycle here.

## Mission

Build bounded self-healing engineering operations while also turning loosely defined product ideas into disciplined engineering inputs.

The operating principle is:

> **Agents reason. Deterministic software grants authority. Evidence moves the state machine forward.**

Incident path:

`observe → orient → decide → reproduce → freeze evidence → repair → verify → independent review → authorize release → deploy → production probation → healthy or rollback/recover → learn → close`

Feature path:

`idea → issue routing → Product Agent → adversarial Product Review → engineering-ready specification → builder → validation → independent review → protected release`

The platform is intentionally **not** an all-powerful autonomous engineer. Agents may create evidence and proposals broadly; production actions are allowed only through pre-authorized, reversible, mechanically verified runbooks and protected release paths. Model confidence never substitutes for deterministic evidence.

## Why an operation controller

Individual workflows can be safe and still fail to form a safe autonomous system if nothing binds their evidence together. Platform Ops therefore maintains a durable **Operation Record** for each incident.

The deterministic controller binds:

- the known-good production SHA before the incident;
- the exact failing reproduction SHA;
- the repair candidate SHA;
- the exact SHA independently reviewed;
- the exact SHA authorized and deployed;
- production probation evidence;
- the authorized prior-known-good rollback SHA when recovery is required;
- the learning and closure record.

Each state transition is explicitly allowlisted and evidence-gated. Operation events are SHA-256 hash-chained so mutation or reordering of prior evidence fails validation. The controller itself has no network, repository-write, merge, deployment, or rollback authority.

See `docs/OPERATION_STATE_MACHINE.md` for the full state model.

## Core safety rules

1. Customer safety and data integrity outrank autonomous speed.
2. GitHub is the engineering control plane, not the sole source of runtime truth.
3. Agents reason and propose; deterministic gates grant authority.
4. A feature request is not a defect and can never enter reproduction merely because of an ambiguous label.
5. Code repair requires executable reproduction evidence: baseline green, failing before repair, passing after repair.
6. The reproduction SHA is frozen before repair and the repair agent cannot redefine that evidence.
7. An agent that authors a patch cannot approve, merge, deploy, or rollback it.
8. Independent engineering review is bound to one exact candidate SHA and becomes stale when that SHA changes.
9. A successful deployment enters **production probation**; deployment alone is not evidence of health.
10. Autonomous production recovery must be explicitly declared, reversible, observable, mechanically authorized, and backed by a versioned runbook.
11. When a fresh deployment causes a bounded, rollback-compatible regression, restore known-good service before attempting speculative forward repair.
12. Every material incident must create a durable improvement or an explicitly owned reliability item.

## Autonomous incident state machine

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
  ├──────────────→ healthy ────────────→ learning ─→ closed
  │
  └→ rollback_authorized
          ↓
       rolled_back
          ↓
     recovery_verified ────────────────→ learning ─→ closed
```

Any active state can fail closed into `escalated` when policy, evidence, risk, or runtime state is ambiguous. `closed` and `escalated` are terminal.

## Trust and autonomy ladder

Autonomy is intended to be earned by bounded failure/change class rather than granted globally to a model.

- **Level 0 — Observe:** agents may diagnose and recommend only.
- **Level 1 — Repair:** agents may reproduce defects and prepare bounded repairs; release remains human controlled.
- **Level 2 — Release:** mechanically eligible low-risk changes may pass through protected release after deterministic gates and independent review.
- **Level 3 — Recover:** eligible classes may release, enter production probation, and invoke a pre-authorized rollback when mechanical recovery conditions are met.

Higher autonomy does not remove the underlying evidence gates or separation of duties.

## Repository map

- `.github/agent-policy.md` — non-negotiable autonomy and separation-of-duties policy.
- `.github/actions/operation-controller/action.yml` — pinned composite interface to the deterministic operation controller.
- `agents/` — narrow Product, Product Review, Triage, Reproduction, Repair, Review, Release, Learning, and Security role contracts.
- `docs/PLAYBOOK.md` — canonical engineering/recovery playbook.
- `docs/ARCHITECTURE.md` — shared-engine/local-contract design.
- `docs/OPERATION_STATE_MACHINE.md` — durable incident state, evidence bindings, production probation, recovery, and integration order.
- `docs/ONBOARDING.md` — how to connect a project.
- `docs/IMPLEMENTATION_STATUS.md` — explicit MVP gap/status ledger.
- `schemas/platform-ops.schema.json` — local project contract.
- `schemas/operation-record.schema.json` — durable hash-chained operation record.
- `schemas/feature-spec.schema.json` — machine-readable product feature specification.
- `schemas/product-review.schema.json` — adversarial product-review disposition.
- `schemas/incident.schema.json` — structured incident record.
- `schemas/evidence.schema.json` — redacted immutable evidence-bundle metadata.
- `schemas/lesson.schema.json` — machine-readable verified incident lesson.
- `scripts/operation_controller.py` — dependency-free transition/evidence validator.
- `scripts/operation_controller_selftest.py` — behavioral and adversarial controller proof.
- `runbooks/` — versioned pre-authorized mitigation/recovery policies.
- `slo/defaults.yaml` — conservative SLO and error-budget defaults.
- `incident-library/` — curated post-incident operational memory.
- `examples/` — realistic reference project contracts.
- `.github/workflows/reusable-issue-router.yml` — conservative first-class issue classification.
- `.github/workflows/reusable-product-intake.yml` — Product Agent + independent adversarial product review.
- `.github/workflows/reusable-reproduction.yml` — test-only failing reproduction stage.
- `.github/workflows/reusable-bounded-repair.yml` — immutable-reproduction-backed PR-only repair stage.
- `.github/workflows/reusable-engineering-review.yml` — independent review bound to an exact PR head SHA.
- `.github/workflows/reusable-release-gate.yml` — deterministic protected release authorization.
- `.github/workflows/reusable-post-deploy-verify.yml` — environment-specific synthetic verification bound to an exact deployed SHA.
- `.github/workflows/reusable-rollback-gate.yml` — pre-authorized rollback decision gate.
- `templates/project/.github/workflows/platform-operation-state.yml` — thin persistence wrapper for bot-authored operation records.
- `templates/project/` — thin caller workflows, deployment/recovery adapter stubs, and starter local contract.

## Current autonomy boundary

Implemented centrally for features:

`loosely written issue → conservative routing → structured Product Agent specification → independent adversarial product review → engineering-ready | revise | escalate`

Implemented centrally for defects/incidents:

`eligible incident → reproduction → frozen failing evidence → bounded repair → deterministic validation → independent exact-SHA review → protected release authorization → deployment verification / rollback gates`

Implemented by the operation-controller layer:

`observed → oriented → decided → reproducing → evidence_frozen → repairing → verifying → reviewed → release_authorized → deployed → production_probation → healthy | rollback/recover → learning → closed`

The operation controller and thin persistence wrapper now exist, but **the existing stage workflows are not yet all wired to append operation transitions automatically**. Until that integration is complete and behaviorally proven, existing workflow evidence and release/recovery gates remain authoritative and autonomous repair remains bounded by each connected project's pinned configuration.

## Next build step

Wire the already-separated workflow stages into the operation controller one transition at a time while preserving their existing permissions:

`incident intake → triage → reproduction → repair → review → release → production probation → rollback/recovery → learning`

Then add a disposable golden-path repository that continuously proves the entire lifecycle, including a planted defect, red reproduction, bounded repair, review, release, synthetic failure, rollback, recovery verification, and learning closure.

## Versioning and supply chain

Central workflow changes have cross-project blast radius. Third-party Actions used here are pinned to immutable commit SHAs. Connected product repositories should pin reusable workflows and composite actions to a reviewed release tag or, preferably for high assurance, an immutable central commit SHA. Never point production projects at a moving central `main` reference.
