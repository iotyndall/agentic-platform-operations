# Canonical Agentic Engineering Playbook

## Mission

Maximize useful engineering autonomy without letting model confidence substitute for evidence. The system should continuously improve software, detect production failures, propose repairs, and eventually promote low-risk changes while keeping blast radius bounded and recovery fast.

## Operating loop

`observe → orient → decide → act → verify → learn`

The loop is intentionally OODA-like, but deterministic code should handle facts it can establish cheaply and reliably. LLM reasoning is reserved for ambiguity, diagnosis, prioritization, implementation, and adversarial review.

## Roles

### Builder

- Read the originating issue and local project contract.
- Reproduce the defect or requirement where practical.
- Make the smallest coherent change that solves the root cause.
- Add/update deterministic tests for repaired defects where practical.
- Never weaken tests, validation, authorization, tenant isolation, observability, or error handling merely to obtain green CI.

### Reviewer

- Be independent of the builder where possible.
- Attempt to falsify the solution.
- Inspect correctness, security, data integrity, tenant boundaries, scope creep, missing regression coverage, operational impact, and rollback assumptions.
- Return PASS or ESCALATE with concrete findings.

### Gatekeeper

Deterministic workflow code is authoritative for:

- compile/typecheck;
- unit/integration tests;
- lint/static analysis;
- production build;
- migration replay/schema checks;
- tenant isolation/RLS checks;
- security/dependency policy;
- changed-path restrictions;
- diff-size/backstop limits;
- critical-path smoke tests;
- stale-head/review checks.

No agent can waive a failed deterministic gate.

### Recovery

- Restore service before pursuing an elegant root-cause repair when a fresh deployment causes a production regression.
- Prefer rollback/known-good restoration when safe and available.
- Keep repair attempts bounded.
- Preserve evidence for later diagnosis.

## Risk classes

### GREEN — eligible for high autonomy

Typical examples:

- small bug fix with deterministic reproduction;
- isolated UI/logic defect away from security/data boundaries;
- dependency patch/minor update that passes the full suite;
- documentation/test-only correction;
- high-confidence production repair within configured path/size limits.

Requirements: all deterministic gates pass, independent review passes when auto-promotion is enabled, rollback is straightforward, and post-deploy verification exists.

### YELLOW — proposal autonomous, promotion constrained

Typical examples:

- moderate refactor;
- integration behavior change;
- dependency major-version upgrade;
- pricing/booking/publishing behavior change;
- migration that is additive but operationally meaningful;
- observability or infrastructure changes that can hide failures if wrong.

Require stronger independent review and normally human approval until project-specific automation proves equivalent controls.

### RED — escalation only

Default RED domains:

- authentication/authorization/RLS;
- secrets/credentials/key rotation;
- destructive database/schema/data operations;
- irreversible migrations;
- payment authorization or money movement;
- broad infrastructure changes;
- removal/weakening of safety or observability controls;
- changes whose failure could be difficult to detect or reverse.

Projects may add RED domains but should not silently remove these defaults.

## Incident lifecycle

1. **Detect.** Prefer deterministic invariants and persistent error stores over sampled logs.
2. **Qualify evidence.** Absence of telemetry is not evidence of health. Report observation coverage explicitly.
3. **Dedupe.** Use stable fingerprints, not model-generated titles.
4. **Classify.** Severity and confidence are separate. High severity does not imply high-confidence diagnosis.
5. **Restore if necessary.** For a fresh production regression, recovery can precede root-cause repair.
6. **Determine repair eligibility.** Small + reversible + high-confidence + outside protected domains.
7. **Repair on a branch.** Never direct-to-main.
8. **Run deterministic gates.** Validate the actual branch/diff produced by the builder.
9. **Independent review.** Different model/reviewer where possible.
10. **Promote or escalate.** GREEN may eventually auto-merge; YELLOW/RED stop.
11. **Verify production.** Critical user journeys must pass after deployment.
12. **Learn.** Add the missing regression test/invariant so the same class of failure is cheaper to catch next time.

## Autonomous repair rules

A repair candidate should be rejected automatically when any of these apply:

- confidence is below the project's threshold;
- protected paths are touched;
- production diff exceeds the configured limit;
- data/schema migration is involved unless explicitly allowed;
- security-sensitive behavior is involved;
- no meaningful deterministic reproduction or verification exists for a risky change;
- the repair attempts to edit the workflow/policy that is judging it;
- the branch/head changed after review;
- the maximum repair-attempt count has been reached.

Prefer a safe refusal over speculative editing.

## Security ratchet

Legacy repositories may contain known dependency vulnerabilities. Do not solve this by disabling the audit.

Use a ratchet:

- record exact known advisory IDs in the project contract;
- open remediation issues for them;
- fail immediately on any new critical advisory;
- remove each baseline exception as soon as it is remediated.

A major framework upgrade should be its own reviewed change, not hidden inside control-plane installation.

## Production verification

Every project must name its critical user journeys. Examples:

- Mesa Direct: public property site → correct Hospitable booking widget → Hospitable reachable.
- YALLOHA: authentication/tenant boundaries, scheduled publishing, Meta connectivity, production build/runtime signals, and core data invariants.

A deployment is not considered proven healthy merely because CI passed. Post-deploy checks should cover the business outcome the application exists to deliver.

## Bounded retries

Default maximum: two materially distinct autonomous repair attempts for the same incident fingerprint. Rewording or retrying the same fix does not reset the counter. After the limit, escalate with accumulated evidence.

## Promotion policy target

The desired mature loop is:

`detect → diagnose → repair → test → independent review → merge → deploy → verify → rollback/escalate if necessary`

The system earns autonomy one risk class at a time. Do not enable universal auto-merge merely because some repairs work well.
