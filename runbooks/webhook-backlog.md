# Runbook: Webhook Backlog

## Trigger
Queue depth, processing delay, retry volume, or valid-webhook completion time exceeds the project threshold.

## Preconditions for automated retry/scale
- The job is declared idempotent or has a mechanically enforced idempotency key.
- Retry limits and backoff are defined in the project contract/runbook.
- The action does not mutate customer data outside normal application semantics.

## Pre-authorized actions
1. Record queue depth, age, error categories, and redacted sample metadata.
2. Scale only pre-approved workers within configured limits when supported.
3. Retry idempotent jobs with bounded exponential backoff.
4. Route repeated failures to a configured dead-letter path.
5. Create/update an incident when backlog or retry thresholds remain exceeded.

## Never
- Reprocess events without idempotency protection.
- Drop events silently.
- Paste raw webhook bodies or customer payloads into GitHub.
- Repair queue state with direct production SQL.
- Retry indefinitely.

## Verification
Queue age and depth must return below threshold, successful processing must recover, and duplicate side-effect indicators must remain within baseline.

## Escalation
Escalate on non-idempotent handlers, repeated dead-letter growth, suspected duplicate side effects, customer-data inconsistency, or dependency-wide outages.
