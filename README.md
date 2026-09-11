# Agentic Platform Operations

Central control plane for autonomous software engineering across current and future projects.

The operating model is **shared engine + local contract**:

- this repository owns the reusable playbook, CI/security/repair workflows, agent policies, schemas, and project templates;
- each application repository keeps only a small `.agentic/platform-ops.json` describing its unique commands, infrastructure, protected paths, critical user journeys, and health checks;
- application-specific production monitors remain close to the application when they depend on domain behavior, but they follow the common incident/repair/review lifecycle defined here.

## Goals

1. Avoid copying hundreds of lines of workflow and agent-control logic into every repository.
2. Make deterministic checks authoritative; agents may propose changes but may not waive failed gates.
3. Keep production observation, code repair, independent review, promotion, and recovery as separate safety domains.
4. Let every project define its own critical-path invariants without reinventing the operating model.
5. Make new-project onboarding a small configuration exercise instead of a bespoke CI/CD build.

## Repository map

- `docs/PLAYBOOK.md` — canonical engineering and recovery playbook.
- `docs/ARCHITECTURE.md` — shared-engine/local-contract design.
- `docs/ONBOARDING.md` — how to connect a project.
- `schemas/platform-ops.schema.json` — project contract.
- `examples/` — Mesa Direct and YALLOHA contracts.
- `.github/workflows/reusable-node-ci.yml` — reusable deterministic Node/Next.js verification.
- `.github/workflows/reusable-security.yml` — reusable dependency/security ratchet.
- `.github/workflows/reusable-bounded-repair.yml` — reusable PR-only repair lane.
- `templates/project/` — thin caller files for application repositories.

## Autonomy boundary

The intended progression is:

`detect → diagnose → issue → bounded repair → deterministic verification → independent review → controlled merge → deployment → production verification → rollback/escalation`

A project may adopt only the stages it is ready for. Sensitive changes—authentication, authorization/RLS, secrets, destructive data/schema operations, payment controls, broad architecture changes—remain escalation-only unless a project explicitly defines stronger controls.

## Versioning

Caller repositories should pin reusable workflows to a reviewed release/tag or immutable commit SHA. `@main` is acceptable only during bootstrap; production projects should migrate to a versioned ref once the first release is cut.
