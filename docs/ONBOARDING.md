# Connect a Project

A new project should inherit the common operating model with minimal local code.

## 1. Enable access to this private reusable-workflow repository

In GitHub repository settings for `agentic-platform-operations`, allow Actions access from the private repositories that will call these reusable workflows. Keep the central repository private unless there is a deliberate reason to publish the playbook.

## 2. Add the local project contract

Copy `templates/project/.agentic/platform-ops.json` into the application as:

`.agentic/platform-ops.json`

Fill in only project-specific facts:

- package/runtime commands;
- protected paths and escalation domains;
- deployment/infrastructure metadata;
- critical user journeys;
- production health/smoke commands;
- any exact legacy security advisories temporarily allowed by the ratchet.

Never place secrets in this contract.

## 3. Add thin caller workflows

Start with the templates under `templates/project/.github/workflows/`.

The caller should contain trigger/permission decisions that belong to the application. The execution logic should live here in the central repository.

Example:

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  verify:
    uses: iotyndall/agentic-platform-operations/.github/workflows/reusable-node-ci.yml@<pinned-ref>
```

## 4. Keep domain monitors local

Do not force every production monitor into a generic workflow. Keep a monitor local when it encodes the application's business contract.

Examples:

- Mesa's Hospitable booking mapping and public-site availability;
- YALLOHA's production data invariants and social-publishing health.

The monitor should emit a standardized issue/fingerprint that can feed the central repair/review pipeline.

## 5. Choose the autonomy level

Projects can adopt progressively:

- Level 0: central CI/security only;
- Level 1: production monitoring + deduplicated incidents;
- Level 2: bounded autonomous repair that opens PRs;
- Level 3: independent adversarial review;
- Level 4: controlled GREEN-risk auto-merge;
- Level 5: post-deploy verification and automatic recovery/rollback where safe.

Do not skip directly to Level 4 if the project lacks deterministic coverage.

## 6. Pin the central version

During bootstrap a caller may use `@main`, but production projects should pin a reviewed tag/release or immutable commit SHA. Central changes have multi-project blast radius.

## 7. Validate the connection

Before removing old local workflows:

1. run the new central CI alongside existing CI;
2. compare results for several PRs;
3. exercise a deliberately failing fixture/branch;
4. exercise project-specific smoke/health checks;
5. verify permissions are least-privilege;
6. only then delete duplicated local control-plane logic.

This parallel period prevents centralization from reducing coverage accidentally.

## Migration plan for existing projects

### Mesa Direct

Keep `scripts/booking-health.mjs` and its property/Hospitable truth table local initially. Move generic CI, security ratchet, PR/recovery policy, and later repair/review logic to the central workflows.

### YALLOHA

Keep the production signal collectors and data invariants local. Replace the duplicated bounded-repair workflow/control policy with a thin caller of the central repair workflow after side-by-side validation.

The goal is not zero local workflow code. The goal is zero duplicated *platform operations logic*.
