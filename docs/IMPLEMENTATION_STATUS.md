# Implementation Status

This file tracks the agreed bounded self-healing engineering-operations target against the central reusable control plane.

## Implemented in platform-ops-v1

- Shared-engine + local-project-contract architecture.
- Machine-readable project contract and dependency-free safety validator.
- Reusable deterministic Node CI with typecheck, tests, lint, build, migration, integration, external-contract, and browser hooks.
- Reusable dependency/security ratchet and high-signal credential guard.
- Immutable commit pinning for third-party GitHub Actions used by the central control plane.
- LOW/MODERATE/HIGH changed-file risk classifier.
- Structured incident, evidence-bundle, and lesson schemas.
- Narrow Triage, Reproduction, Repair, Review, Release, Learning, and Security role contracts.
- Test-first reproduction workflow: green baseline → test-only branch → failing executable evidence → immutable reproduction SHA.
- Bounded repair workflow that must consume the exact reproduction branch/SHA, cannot edit reproduction evidence, enforces protected paths/diff limits, runs deterministic checks, and may open a PR only.
- Versioned runbooks for failed deployments, third-party outages, failed migrations, webhook backlogs, and feature-flag mitigations.
- Conservative SLO/error-budget defaults.
- PR, incident, security-incident, and reliability-work templates plus CODEOWNERS for central control-plane paths.
- Incident learning-library structure and closure standard.

## Partially implemented / project dependent

- Runtime incident intake and deduplication: Mesa and YALLOHA have local monitors; a generic incident router/evidence packager is not yet central.
- Observability: project-local sources can be declared, but OpenTelemetry correlation and central SLO ingestion are not implemented.
- Risk classification: path-based classifier exists; dependency, telemetry, rollback availability, feature-flag state, and error-budget inputs are not yet part of one promotion score.
- Security: dependency/credential guards exist; CodeQL/dependency-review/push-protection depend on GitHub plan/repository capabilities and are not yet centrally orchestrated.

## Not yet implemented

- Independent cross-model Review workflow with structured PASS/ESCALATE output.
- Protected staging deployment workflow and staging evidence bundle.
- Production Release workflow gated by reviewed immutable SHA, environment protection, SLO/error-budget state, and staging evidence.
- Executable pre-authorized rollback and feature-flag mitigation workflows.
- Central evidence scrubber/packager with artifact hashes and retention policy enforcement.
- OpenTelemetry/SLO evaluator and error-budget release gate.
- Automatic Learning agent that creates postmortem/lesson/runbook/monitor improvement PRs.
- Artifact attestation/SBOM/provenance generation.
- Organization-level `.github` defaults and repository rulesets/branch protection enforcement.

## MVP acceptance criteria status

1. Alert creates structured incident issue — **Partial** (project-local Mesa/YALLOHA behavior, central schema/template exists).
2. Incident contains service/environment/SHA/impact/signal/redacted evidence — **Schema/template implemented; generic router pending**.
3. Triage agent produces bounded investigation/risk — **Role defined; reusable workflow pending**.
4. Reproduction agent creates failing regression evidence — **Reusable workflow implemented**.
5. Repair agent opens minimal test-backed PR — **Reusable workflow implemented**.
6. CI blocks merge on critical check failure — **Reusable checks implemented; repository enforcement still required**.
7. Staging deploys after validation — **Pending**.
8. Production requires protected-environment policy — **Contract requires it; release workflow/repository environment enforcement pending**.
9. Defined health failure can invoke pre-approved rollback — **Runbook implemented; executable rollback workflow pending**.
10. Incident closure requires postmortem + durable improvement — **Policy/library defined; automated enforcement pending**.

## Next build order

1. Independent cross-model reviewer and signed/structured review evidence.
2. Staging/release workflows with environment-scoped permissions and immutable-SHA checks.
3. Deployment verification + rollback workflow abstraction.
4. Evidence bundle generation/redaction/hashing.
5. SLO/error-budget evaluator and release freeze policy.
6. Learning-agent workflow and incident-library PR generation.
7. Wire Mesa and YALLOHA to a versioned central release, one project at a time.
