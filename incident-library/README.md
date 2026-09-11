# Incident Learning Library

This directory stores curated, verified operational lessons—not raw production dumps.

## Purpose

Every material incident should make future detection, diagnosis, mitigation, or prevention cheaper. The library is retrieval material for future agents, so verified facts must remain distinct from hypotheses and customer/secret data must never be copied here.

## Recommended structure

```text
incident-library/
  <project>/
    YYYY-MM-DD-<failure-mode>/
      incident.md
      evidence.json
      root-cause.md
      remediation.md
      regression-tests.md
      runbook-delta.md
      lesson.json
```

`lesson.json` must follow `schemas/lesson.schema.json`. Evidence metadata follows `schemas/evidence.schema.json`; raw evidence should remain in the approved audited store or short-lived workflow artifact and be referenced by immutable ID/hash.

## Closure questions

A material incident is not fully learned until the record answers:

1. What customer-visible behavior failed?
2. What was observed versus hypothesized?
3. What root cause was actually verified?
4. Why did existing tests or monitors not catch it sooner?
5. What mitigation minimized customer impact?
6. Is that mitigation safe enough to codify as a runbook?
7. Which regression test, monitor, runbook, policy, rollback, security control, or architecture change reduces recurrence?
8. What evidence proves the remediation worked?

## Durable improvement requirement

Close with at least one linked improvement: regression test, monitor/alert, runbook, rollback capability, ADR, security control, or explicitly owned reliability backlog item. Incident count is not the success metric; detection quality and decreasing recurrence/recovery time are.
