# Agentic Platform Operations

Central GitHub-centered control plane for autonomous software engineering, reliability, and maintenance across current and future projects.

The operating model is **shared engine + local contract**:

- this repository owns reusable policy, CI/security/reproduction/repair machinery, role definitions, runbooks, schemas, SLO defaults, and project templates;
- each application repository keeps a small `.agentic/platform-ops.json` describing only its unique commands, infrastructure, protected paths, evidence sources, environments, critical user journeys, SLOs, approved mitigations, and release constraints;
- application-specific runtime monitors stay close to the application when domain behavior cannot be generalized, but they feed the common incident/evidence/reproduction/repair/review/release/learning lifecycle here.

## Mission

Build bounded self-healing engineering operations:

`detect → collect evidence → classify → safely mitigate → reproduce → repair → validate → review → release → verify → learn`

The platform is intentionally **not** an all-powerful autonomous engineer. Agents may create evidence and proposals broadly; production actions are allowed only through pre-authorized, reversible, mechanically verified runbooks and protected release paths.

## Core safety rules

1. Customer safety and data integrity outrank autonomous speed.
2. GitHub is the engineering control plane, not the sole source of runtime truth.
3. Code repair requires executable reproduction evidence: baseline green, failing before repair, passing after repair.
4. Deterministic gates are authoritative and cannot be waived by model output.
5. An agent that authors a patch cannot approve, merge, or deploy it.
6. Autonomous production mitigation must be explicitly declared, reversible, observable, and backed by a versioned runbook.
7. Every material incident must create a durable improvement or an explicitly owned reliability item.

## Repository map

- `.github/agent-policy.md` — non-negotiable autonomy and separation-of-duties policy.
- `agents/` — narrow Triage, Reproduction, Repair, Review, Release, Learning, and Security role contracts.
- `docs/PLAYBOOK.md` — canonical engineering/recovery playbook.
- `docs/ARCHITECTURE.md` — shared-engine/local-contract design.
- `docs/ONBOARDING.md` — how to connect a project.
- `docs/IMPLEMENTATION_STATUS.md` — explicit MVP gap/status ledger.
- `schemas/platform-ops.schema.json` — local project contract.
- `schemas/incident.schema.json` — structured incident record.
- `schemas/evidence.schema.json` — redacted immutable evidence-bundle metadata.
- `schemas/lesson.schema.json` — machine-readable verified incident lesson.
- `runbooks/` — versioned pre-authorized mitigation/recovery policies.
- `slo/defaults.yaml` — conservative SLO and error-budget defaults.
- `incident-library/` — curated post-incident operational memory.
- `examples/` — Mesa Direct and YALLOHA project contracts.
- `.github/workflows/reusable-policy.yml` — deterministic changed-file risk classification.
- `.github/workflows/reusable-node-ci.yml` — reusable deterministic CI.
- `.github/workflows/reusable-security.yml` — dependency/security ratchet.
- `.github/workflows/reusable-incident-dispatcher.yml` — eligible incident → reproduction queue.
- `.github/workflows/reusable-reproduction.yml` — test-only failing reproduction stage.
- `.github/workflows/reusable-bounded-repair.yml` — immutable-reproduction-backed PR-only repair stage.
- `templates/project/` — thin caller workflows and starter local contract.

## Current autonomy boundary

Implemented centrally:

`incident eligible → reproduction branch → failing executable evidence → bounded repair → deterministic verification → repair PR`

Not yet enabled centrally:

`independent cross-model review → staging release → protected production release → automated rollback/feature-flag mitigation → SLO error-budget gate → learning-agent PR`

Those missing stages are tracked explicitly in `docs/IMPLEMENTATION_STATUS.md`. Repair remains PR-only until they exist and are proven.

## Versioning and supply chain

Central workflow changes have cross-project blast radius. Third-party Actions used here are pinned to immutable commit SHAs. Connected product repositories should pin reusable workflows to a reviewed release tag or, preferably for high assurance, an immutable central commit SHA. Never point production projects at a moving central `main` reference.
