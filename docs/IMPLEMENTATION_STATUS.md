# Implementation Status

This file tracks the bounded self-healing engineering-operations target against the central reusable control plane.

## Implemented centrally

- Shared-engine + local-project-contract architecture.
- Machine-readable project contract and dependency-free safety validator.
- Reusable deterministic CI with project-declared typecheck, tests, lint, build, migration, integration, contract, browser, and performance hooks.
- Reusable dependency/security ratchet and high-signal credential guard.
- Immutable commit pinning for third-party GitHub Actions used by the central control plane.
- LOW/MODERATE/HIGH changed-file risk classification.
- Structured incident, evidence-bundle, lesson, feature-spec, product-review, and operation-record schemas.
- Narrow Product, Product Review, Triage, Reproduction, Repair, Engineering Review, Release, Learning, and Security role contracts.
- Conservative issue routing that mechanically distinguishes feature work from defect/incident work.
- Test-first reproduction workflow: green baseline → test-only branch → failing executable evidence → immutable reproduction SHA.
- Bounded repair workflow that consumes the exact reproduction branch/SHA, cannot edit reproduction evidence, enforces protected paths/diff limits, runs deterministic checks, and may open a PR only.
- Independent engineering-review workflow bound to an exact PR head SHA with structured PASS/REVISE/ESCALATE evidence.
- Protected release gate that binds reviewed SHA, CI SHA, merged candidate tree, target environment, staging evidence, SLO state when enabled, and rollback availability.
- Staging and production caller templates with environment-scoped deployment adapters.
- Post-deploy verification workflow that runs declared synthetic checks and binds verification metadata to an exact candidate SHA.
- Pre-authorized rollback gate requiring an open incident, failure threshold, schema compatibility, bounded ancestor distance, and declared reversible mitigation.
- Production rollback caller template with compatibility check, protected environment, verification, and incident outcome recording.
- Reusable mitigation gate and versioned recovery runbooks.
- SLO/error-budget evaluator semantics and conservative defaults.
- Learning workflow and incident learning-library conventions.
- Deterministic operation controller with explicit legal transitions, evidence prerequisites, exact-SHA bindings, and SHA-256 hash-chained event history.
- Pinned composite operation-controller action for project workflows.
- Thin operation-state persistence workflow that accepts only bot-authored prior records from the canonical incident and appends the next machine-authored record.
- Behavioral controller tests covering healthy production, rollback recovery, stale SHA evidence, skipped states, wrong rollback target, terminal escalation, and hash-chain tampering.

## Partially implemented / project dependent

- Runtime incident intake and deduplication: local monitors exist in proving-ground projects; generic central intake machinery exists but domain-specific monitors remain project-local by design.
- Operation-record integration: controller and persistence wrapper exist, but the existing intake/triage/reproduction/repair/review/release/recovery workflows do not yet all emit state transitions automatically.
- Deployment execution: central authorization and project caller patterns exist, while each project must implement and prove its staging/production/rollback adapters.
- Production probation: the state and evidence requirements are defined; a reusable probation orchestrator that repeatedly evaluates critical journeys and triggers rollback dispatch is not yet wired.
- Observability: project-local evidence sources and SLO inputs are supported, but OpenTelemetry correlation and a general telemetry-normalization layer are not implemented.
- Risk classification: path-based and independent-review risk evidence exist; dependency, telemetry, rollback history, feature-flag state, and learned historical risk are not yet combined into one promotion/trust score.
- Security: dependency/credential guards exist; CodeQL, dependency review, push protection, SBOM, and provenance support depend on repository capabilities and are not yet fully orchestrated centrally.
- Learning: workflow and schemas exist, but automatic conversion of every closed operation into a verified incident-library improvement PR is not yet end-to-end proven.

## Not yet implemented / not yet proven end to end

- Disposable golden-path canary repository that continuously proves the entire autonomous lifecycle against real GitHub APIs.
- Automatic production-probation orchestrator with repeated critical-journey checks and deterministic rollback dispatch.
- Full operation-record wiring across every existing workflow stage.
- Earned-autonomy scoring by failure/change class using historical operation outcomes.
- Central evidence scrubber/packager with signed artifact hashes and retention-policy enforcement.
- OpenTelemetry correlation and normalized SLO ingestion across heterogeneous projects.
- Artifact attestation/SBOM/provenance generation and verification in release policy.
- Organization-level `.github` defaults plus repository ruleset/branch-protection enforcement.
- Broad provider-specific deployment adapters; project templates intentionally fail closed until configured.

## MVP acceptance criteria status

1. Alert creates structured incident issue — **Partial / project dependent**.
2. Incident contains service/environment/SHA/impact/signal/redacted evidence — **Schema/intake machinery implemented; domain signal quality remains project dependent**.
3. Triage produces bounded investigation/risk — **Reusable triage workflow implemented**.
4. Reproduction creates failing regression evidence — **Implemented and externally trialed**.
5. Repair opens minimal test-backed PR without changing reproduction evidence — **Implemented and externally trialed**.
6. Independent engineering review binds verdict to exact proposed SHA — **Implemented; production use still requires project pinning and repository enforcement**.
7. Staging release requires deterministic validation and exact-SHA evidence — **Workflow/gate implemented; project deployment adapter required**.
8. Production requires protected-environment policy, staged evidence, review, CI, rollback availability, and SLO evidence when enabled — **Gate/template implemented; project environment/adapters required**.
9. Defined health failure can invoke pre-approved rollback — **Gate/template implemented; automatic probation-to-rollback orchestration pending**.
10. Incident closure requires learning and durable improvement — **Policy/workflow/controller state implemented; end-to-end automatic wiring pending**.
11. One durable operation record binds the incident across all states — **Controller and persistence wrapper implemented; stage integration pending**.
12. The complete lifecycle is behaviorally self-certified in a disposable repository — **Pending**.

## Current build order

1. Wire incident intake, triage, reproduction, repair, review, release, probation, rollback/recovery, and learning workflows into the operation controller one transition at a time.
2. Add the reusable production-probation orchestrator and deterministic rollback dispatch.
3. Build a disposable golden-path canary repository that plants a defect and proves red → repair → review → release → failed probation → rollback → recovery → learning.
4. Add normalized evidence packaging/redaction/hashing and artifact provenance.
5. Add richer SLO/telemetry correlation and error-budget policy inputs.
6. Add learned autonomy/trust scoring by bounded change/failure class.
7. Wire proving-ground product repositories to a reviewed immutable central release one project at a time.
