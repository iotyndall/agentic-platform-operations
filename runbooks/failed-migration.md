# Runbook: Failed Migration

## Trigger
A schema migration fails, application/schema compatibility checks fail, or post-migration health indicates incompatibility.

## Immediate actions
1. Halt further release promotion.
2. Preserve migration logs, version/checksum, deployment SHA, and schema-validation evidence.
3. Keep or restore the last application version compatible with the current schema when that compatibility is mechanically proven.
4. Open/update the incident and escalate for any data repair requirement.

## Automated actions allowed
- Stop promotion.
- Re-run read-only migration status/validation commands.
- Restore a compatible application version through the approved release workflow when no destructive schema change prevents it.
- Create a migration repair/revert proposal and tests on a branch.

## Never
- Execute ad hoc production SQL.
- Delete, rewrite, backfill, or repair customer data autonomously.
- Drop tables/columns or reverse an irreversible migration autonomously.
- Restore a database snapshot without human-led recovery authorization.

## Verification
Require migration replay in a disposable environment, integration tests, and application/schema compatibility checks before another production attempt.

## Escalation
Any ambiguous schema state, destructive migration, data repair, backup restore, or compatibility uncertainty is human-led.
