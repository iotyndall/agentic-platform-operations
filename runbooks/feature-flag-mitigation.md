# Runbook: Feature-Flag Mitigation

## Trigger
A newly released feature is strongly correlated with a severe error, availability, or latency regression and the feature is registered as safe-to-disable in the project contract.

## Preconditions
- The exact flag is explicitly allowlisted for autonomous disablement.
- The feature is noncritical to authentication, payment, access control, data integrity, or required legal/compliance behavior.
- Current and prior values are recorded.
- A fixed verification and recovery window is defined.

## Pre-authorized actions
1. Create/update the incident with the correlated release and flag.
2. Disable only the named allowlisted flag through the approved flag-management workflow.
3. Observe configured health/SLO signals for the verification window.
4. Keep the feature disabled if health materially improves and open a repair/reproduction task.
5. Restore the prior value if the mitigation does not improve health and no new risk is introduced.

## Never
- Disable an unregistered flag.
- Change multiple flags in one autonomous mitigation.
- Alter auth, billing, entitlement, security, or data-integrity behavior.
- Modify flag infrastructure or permissions as part of the mitigation.

## Verification
Record before/after error, availability, latency, and critical-journey evidence tied to the same observation window.

## Escalation
Escalate if the feature is critical, the flag is not pre-authorized, health does not improve, or multiple interacting changes are suspected.
