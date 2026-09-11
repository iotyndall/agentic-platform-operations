# Runbook: Failed Deployment

## Trigger
A production deployment completes and a configured critical health or synthetic check fails at the project's declared threshold.

## Preconditions for automated rollback
- The previous deployment is identified and recorded as known-good.
- The rollback target is immutable.
- No destructive/incompatible migration or irreversible production mutation occurred after the known-good release.
- The configured rollback mechanism is available and scoped to the affected service.
- The incident and current deployment SHA have been recorded.

## Pre-authorized actions
1. Mark the current release suspect and freeze further promotion.
2. Invoke the project-declared rollback workflow.
3. Verify critical journeys against the restored release.
4. Create/update the incident with current/prior SHA and verification evidence.
5. Start triage/reproduction after service restoration.

## Never
- Roll back through direct production SQL.
- Guess at schema compatibility.
- Modify data to make the old release compatible.
- Attempt repeated forward fixes in production.

## Verification
All configured critical journeys must return to healthy state during the observation window. Record the exact rollback target and verification artifacts.

## Escalation
If rollback is unsafe, unavailable, or fails to restore health, stop automated remediation and escalate immediately with accumulated evidence.
