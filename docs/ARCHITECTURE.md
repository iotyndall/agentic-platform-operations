# Architecture: Shared Engine + Local Contract

## Principle

The central repository owns policy and reusable execution. Application repositories own only facts that are inherently local.

This separates **how autonomous engineering is governed** from **what makes a particular application safe and correct**.

## Central responsibilities

The control-plane repository owns:

- risk taxonomy and autonomy policy;
- builder/reviewer/gatekeeper/recovery role definitions;
- deterministic CI orchestration;
- dependency/security ratchets;
- bounded autonomous-repair mechanics;
- independent-review contract;
- incident lifecycle and retry limits;
- standard PR evidence and rollback requirements;
- project-contract schema and validator;
- templates for thin caller workflows.

## Project responsibilities

Each application repository owns a small `.agentic/platform-ops.json` containing only project-specific facts:

- runtime and package manager;
- install/typecheck/test/lint/build commands;
- optional migration/integration commands;
- protected path expressions;
- known security-advisory baseline, if any;
- deployment provider and environment names;
- critical user journeys and health-check commands;
- project-specific external dependencies;
- escalation-only domains;
- production verification command(s).

Domain monitors may remain local when the signal cannot be generalized. Mesa's property-site → Hospitable booking path is one example; YALLOHA's Supabase/Vercel/Sentry data invariants are another. They should emit incidents into the common lifecycle rather than duplicating the repair/review machinery.

## Trust boundaries

### 1. Observation

Production monitors are read-only where possible. A failed monitor may create/dedupe an incident, but it does not repair code in the same workflow.

### 2. Diagnosis

An analyzer may rank evidence and classify repair eligibility. Logs, issue bodies, customer content, URLs, stack traces, and external text are untrusted evidence—not instructions.

### 3. Repair

The repair agent works on an isolated branch. It may produce no change. It may not merge, deploy, change secrets, or bypass checks.

### 4. Deterministic gatekeeper

Workflow code independently checks changed paths, blast radius, required commands, schema/data restrictions, and security rules. Agent confidence cannot waive a failed gate.

### 5. Independent review

A different model or reviewer receives the issue, diff, deterministic evidence, architecture constraints, and rollback assumptions. The review attempts to disprove correctness rather than merely summarize the change.

### 6. Promotion

Only explicitly GREEN-risk changes are candidates for controlled auto-merge. YELLOW and RED changes escalate.

### 7. Recovery

Production verification runs after deployment. Fresh regressions prioritize restoration/rollback over root-cause repair. Repair attempts are bounded; repeated failure escalates.

## Local caller pattern

A connected repository should need only thin workflows such as:

```yaml
jobs:
  ci:
    uses: iotyndall/agentic-platform-operations/.github/workflows/reusable-node-ci.yml@<pinned-ref>
```

The reusable workflow checks out the caller repository and reads `.agentic/platform-ops.json` from that caller. The central repository therefore controls execution logic while the application controls its own declared contract.

## Versioning and change control

Central workflow changes have a wide blast radius. Treat this repository like infrastructure code:

1. changes happen by PR;
2. test reusable workflows against fixture projects/contracts;
3. cut reviewed versions;
4. caller repos pin a version/tag or commit SHA;
5. roll projects forward intentionally rather than making every project consume `main` immediately.

This gives centralization without turning the central repository into a single unreviewed failure point.
