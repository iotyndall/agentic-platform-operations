# Canonical Agentic Engineering Operations Playbook

## Purpose

Build a GitHub-centered operating system for engineering maintenance and reliability that improves stability, uptime, security, and delivery quality over time.

The desired behavior is bounded self-healing:

`detect → collect evidence → classify → safely mitigate → reproduce → repair → validate → review → release → verify → learn`

GitHub coordinates engineering work and policy. Runtime observability remains the source of truth for whether users are actually healthy.

## Non-negotiable principles

1. Preserve customer safety and data integrity over autonomous speed.
2. Require executable evidence for code repair: a green baseline, a failing reproduction before repair, and passing evidence after repair.
3. Let automation execute production actions only when they are explicitly pre-authorized, reversible, scoped, observable, and backed by a versioned runbook.
4. Separate the roles that detect, reproduce, repair, review, and release a change.
5. Treat unknown or missing evidence as uncertainty, not health.
6. Every material incident must improve a test, monitor, runbook, rollback capability, policy, security control, architecture decision, or owned reliability backlog item.

The full non-negotiable authority boundary lives in `.github/agent-policy.md`.

## Roles and authority

### Triage
Consumes runtime signals and approved redacted evidence. Produces severity, impact, evidence summary, confidence, hypotheses, and next-step recommendation. It may create/update incidents but may not modify code or production.

### Reproduction
Turns a credible incident hypothesis into executable evidence. It may create only test/fixture/reproduction artifacts. The baseline suite must be green before its change; the reproduction must then cause a deterministic failure while remaining type/lint valid. It must not repair the defect.

### Repair
Starts from the exact immutable failing reproduction. It may make the smallest production-code patch necessary, but it may not edit the reproduction evidence, protected paths, control-plane policy/workflows, or sensitive production domains. It may open a PR only.

### Review
Receives the issue, immutable reproduction evidence, PR diff, deterministic results, architecture constraints, and rollback plan. It attempts to falsify correctness/security and emits PASS or ESCALATE against an exact reviewed SHA. It may not edit code or deploy.

### Release
May deploy only an already-reviewed immutable commit through protected staging/production workflows. It cannot author or approve the code. It owns staging evidence, production verification, and approved rollback decisions.

### Learning
Converts a resolved incident into curated operational memory and durable prevention. It may author docs/issues/PRs but cannot rewrite historical evidence or production state.

### Security
Consumes deterministic dependency/secret/static-analysis findings and produces bounded remediation proposals. Sensitive rotation, access revocation, customer notification, and root credentials remain human-authorized unless a narrowly scoped runbook explicitly says otherwise.

## Separation of duties

An agent that authors a patch must never approve, merge, or deploy that patch. A reproduction agent must not repair the failure it demonstrates. A review agent must not rewrite the patch it is judging. A release agent may act only on an already-approved immutable commit. Deterministic checks cannot be waived by any model.

## Risk model

### LOW
Documentation, copy/styling, test-only changes, or isolated logic fixes with comprehensive executable evidence and no sensitive path involvement. LOW changes may eventually be autonomous through review and release if the project contract permits it.

### MODERATE
API handlers, queues, meaningful product behavior, dependency changes, third-party integration behavior, or non-sensitive configuration. Require independent review and staging evidence; production automation remains constrained until project-specific controls are proven.

### HIGH / CRITICAL
Authentication, authorization/RLS, billing/payments, secrets/credentials, production workflows, infrastructure, destructive data/schema operations, irreversible migrations, customer-data remediation, root credentials, or changes whose failure is hard to detect/reverse. Human approval or human-led operations are required. Unknown risk defaults high.

The local project contract may add high-risk domains but may not silently remove central defaults.

## Incident lifecycle

1. **Detect.** Prefer deterministic health invariants, persistent error stores, synthetic journeys, deployment events, and security scanners over sampled anecdotes.
2. **Collect evidence.** Limit evidence to the affected service/time window, scrub secrets/customer data, preserve immutable IDs/hashes, and record observation coverage.
3. **Dedupe.** Correlate by stable fingerprint, service, deployment SHA, endpoint/job, time window, and signal—not model-generated titles.
4. **Classify.** Severity, impact, diagnosis confidence, and change risk are separate dimensions.
5. **Safely mitigate when authorized.** Restoration may precede diagnosis after a fresh bad deployment, but only through a pre-approved runbook whose preconditions are mechanically satisfied.
6. **Reproduce.** Baseline tests pass; a test-only branch establishes deterministic failing evidence. If executable reproduction is impossible, document why and generally escalate above LOW.
7. **Repair.** Work from the immutable reproduction branch/SHA. The repair may not modify the evidence that proves the failure.
8. **Validate.** Run configured type, lint, unit, integration, migration/schema, external contract, browser/synthetic, security, build, and blast-radius checks.
9. **Review.** Independent reviewer attacks the patch and returns a decision tied to the exact head SHA.
10. **Release.** Staging first, then production through protected environment policy. Production credentials are not available to PR workflows.
11. **Verify.** Measure the business-critical journey and runtime telemetry during a defined observation window.
12. **Rollback/escalate if needed.** Prefer known-good restoration to speculative forward edits when rollback compatibility is proven.
13. **Learn.** Curate a postmortem/lesson and create at least one durable improvement or owned reliability item.

## Executable evidence rules

The primary evidence type depends on the failure:

- deterministic business logic → unit test;
- API/database/auth/queue behavior → integration test;
- browser/customer workflow → browser or deployed synthetic test;
- third-party API/webhook behavior → contract test with fixtures;
- deployment/configuration failure → configuration assertion plus deployed synthetic check;
- latency/saturation regression → performance/load check plus telemetry threshold.

For webhook-driven systems, test duplicate, out-of-order, retried, invalid-signature, timeout/retry, partial-database-failure, idempotency collision, rate-limit, generation failure, and dead-letter behavior where relevant.

A repair must never alter its reproduction test merely to achieve green CI. If the reproduction is later proven invalid, that is a new reviewed reproduction decision, not part of the repair.

## Deterministic gatekeeper

The gatekeeper should prefer code over LLM judgment for facts it can establish mechanically:

- committed lockfile installation;
- typecheck/compile;
- lint/static analysis;
- unit/integration tests;
- migration replay/schema checks;
- tenant isolation/RLS tests;
- dependency/security policy;
- secret/credential scanning;
- changed-path risk classification;
- production diff-size limits;
- immutable reproduction integrity;
- external contract and browser tests;
- build verification;
- reviewed-head/stale-review checks;
- critical production journey verification.

No agent can convert a red deterministic check into a pass through explanation or confidence.

## Evidence handling

Evidence bundles follow `schemas/evidence.schema.json` and incidents follow `schemas/incident.schema.json`.

Agents receive the narrowest sufficient bundle. Evidence must be scrubbed of secrets and customer content, limited to the affected service/time range, and referenced by immutable IDs/hashes. Raw sensitive logs do not belong in GitHub issues, PRs, retained prompts, or the incident library.

Observations, hypotheses, and verified facts must remain separate. Absence of telemetry is explicitly reported as unknown/degraded evidence coverage.

## Production mitigation

Autonomous mitigation is deny-by-default. A project must list each allowed mitigation in `.agentic/platform-ops.json` with:

- a stable mitigation ID;
- versioned runbook;
- reversible action or robust compensating action;
- deterministic validation command;
- attempt/time limits;
- logging/audit trail.

Examples include rollback of a compatible bad deployment, bounded retry of a provably idempotent job, disabling a named noncritical feature flag, or scaling a pre-approved worker pool. Direct production SQL and direct customer-data remediation are never autonomous.

## Security and supply chain

- Pin third-party GitHub Actions to immutable commit SHAs.
- Use Dependabot/security updates plus deterministic dependency review/audit.
- Use secret scanning/push protection and static analysis where repository plan/capability permits.
- Keep `GITHUB_TOKEN` permissions minimal by workflow/job.
- Keep production credentials environment-scoped and prefer short-lived OIDC credentials.
- Never put service-role/database/root credentials into browser code or general agent contexts.
- Control-plane/policy changes are high-risk and require human ownership.

Legacy dependency findings use a security ratchet: baseline exact known advisory IDs with a remediation issue, fail on any new critical advisory, and remove exceptions as they are fixed.

## SLO and error-budget behavior

Projects may start from `slo/defaults.yaml`, then adapt objectives to actual business-critical journeys. Error-budget warning/exhaustion should progressively disable autonomous merging and nonessential release promotion, increase staging/review requirements, and create reliability work. Emergency rollback/restoration remains permitted when its runbook preconditions are satisfied.

## Release and rollback target

The mature delivery flow is:

`PR → policy/risk → deterministic CI/security → preview/integration evidence → independent review → merge → staging → staging synthetics/telemetry → protected production gate → deploy → observation window → promote complete or pre-approved rollback`

Pull-request workflows must not receive production deployment credentials. Production deployments use separate environment-scoped permission and concurrency. Competing production deploys are serialized.

## Learning loop

Curated lessons belong in `incident-library/` and follow `schemas/lesson.schema.json`. Each lesson records symptoms, observations, hypotheses, verified root-cause status, preventive controls, safe mitigation, required human approval, related runbooks/PRs/tests, monitor changes, and confidence.

Material incidents answer the closure questions in `incident-library/README.md`. Future agents may retrieve verified lessons; they must not treat an unresolved hypothesis as policy.

## Autonomy progression

Expand autonomy only after real outcomes demonstrate safety. The initial defaults are:

- auto-create incidents: yes;
- auto-triage: yes when evidence access is narrow/read-only;
- auto-create failing reproductions: yes for eligible high-confidence incidents;
- auto-create test-backed repair PRs: yes within path/blast-radius rules;
- auto-merge agent PRs: no until independent review and repository enforcement exist;
- auto-deploy to staging: target yes after CI/review;
- auto-deploy agent fixes to production: no initially;
- auto-rollback: yes only through a proven compatible rollback runbook;
- auto-disable feature flags: only named noncritical flags with a versioned runbook;
- direct production DB/customer-data changes: never.

The system earns broader autonomy one action and risk class at a time.
