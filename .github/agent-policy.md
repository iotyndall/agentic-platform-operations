# Agent Operating Policy

This policy is the minimum safety boundary for every connected project. Project contracts may add restrictions; they may not silently weaken these defaults.

## Never

- Execute SQL directly against production databases.
- Access or copy customer content unless a specifically approved, audited workflow authorizes that access.
- Modify billing records, payments, authentication records, roles, entitlements, or identity data.
- Disable monitoring, backups, security checks, deployment gates, audit logging, or branch protections.
- Merge, approve, or deploy a pull request authored by the same agent identity or agent role.
- Add secrets to source code, issues, pull requests, comments, logs, artifacts, or retained agent prompts.
- Expand workflow permissions, production credentials, or protected-path exceptions as part of an autonomous repair.
- Modify this policy, the project contract, or the workflow judging a repair from within that repair.
- Perform destructive, irreversible, or speculative production remediation.

## May autonomously do

- Create and update structured incident issues.
- Collect narrow, redacted evidence through approved read-only sources.
- Create branches, tests, documentation, runbooks, and pull requests.
- Produce a failing regression test or other executable reproduction artifact.
- Propose the smallest repair that satisfies the reproduction evidence.
- Retry a specifically documented idempotent job within the runbook's attempt and time limits.
- Trigger a pre-approved rollback or named noncritical feature-flag mitigation only when all runbook preconditions are mechanically verified.

## Must escalate

- Customer data, production database, auth, payment, security, credential, access-control, or entitlement actions.
- Any destructive or non-reversible operation.
- Any remediation without an approved runbook when production state would be changed.
- Any change classified Moderate, High, or Critical unless its required approval policy is satisfied.
- Any incident whose diagnosis remains ambiguous after the configured repair-attempt limit.
- Any rollback whose schema compatibility cannot be proven.

## Separation of duties

The standard roles are Triage, Reproduction, Repair, Review, Release, Learning, and Security.

An agent that authors a patch cannot approve that patch, declare its own evidence sufficient, merge it, or initiate the production deployment. A release agent may act only on an already-approved commit through a protected deployment path. Deterministic gates are authoritative and cannot be waived by model output.

## Evidence requirement

Autonomous repair requires executable evidence of the failure before repair and evidence that the same check passes after repair. Valid evidence may be a unit, integration, browser, contract, configuration, synthetic, or performance test depending on the failure mode. If executable reproduction is impossible, the incident must explicitly document why and normally escalates above GREEN risk.
