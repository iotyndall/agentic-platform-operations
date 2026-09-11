## Intent

Link the originating issue and describe the intended outcome, not just the implementation.

## Risk

- [ ] LOW
- [ ] MODERATE
- [ ] HIGH / CRITICAL

Explain the blast radius, protected paths, external dependencies, data/auth/payment impact, and why this classification is appropriate.

## Executable evidence

For defect repairs:
- Reproduction artifact/path:
- Base/reproduction SHA:
- Before patch: failing evidence:
- After patch: passing evidence:

For non-defect changes, state the acceptance tests or invariants that prove the intended behavior.

## Validation

- Type/lint:
- Unit tests:
- Integration tests:
- Contract tests:
- Browser/synthetic tests:
- Migration/schema checks:
- Security/dependency checks:
- Staging evidence:

## Production and rollback

- Critical journeys affected:
- Deployment/observation plan:
- Exact rollback or mitigation path:
- Schema compatibility concerns:

## Agent separation

If agent-authored, identify the Builder/Reproduction/Review roles and confirm the authoring agent will not approve, merge, or deploy its own change.
