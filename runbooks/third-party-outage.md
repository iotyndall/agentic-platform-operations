# Runbook: Third-Party Dependency Outage

## Trigger
A critical external dependency becomes unreachable, exceeds configured error/latency thresholds, or fails a contract/synthetic check.

## Preconditions
- Local application health has been checked independently.
- The affected dependency and customer journey are identified.
- A documented fallback/degraded mode exists before it may be enabled automatically.

## Pre-authorized actions
1. Record the dependency failure and evidence in the incident.
2. Activate only a named project-declared fallback or degraded mode.
3. Suppress unsafe retries while preserving idempotent work.
4. Continue bounded synthetic checks to detect recovery.
5. Restore normal behavior only after the dependency is healthy for the declared recovery window.

## Never
- Invent a new fallback in production.
- Bypass authentication, validation, payment, or data-integrity controls to keep a feature working.
- Flood the provider with unbounded retries.
- Treat provider status-page text as sufficient evidence by itself.

## Verification
Verify both the degraded customer journey and the eventual normal journey. Record provider-independent evidence where possible.

## Escalation
Escalate when no pre-approved fallback exists, the outage affects auth/payments/data integrity, or the degraded mode itself becomes unhealthy.
