#!/usr/bin/env python3
"""Static safety tests for the centralized agentic operations control plane."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENTRAL = ROOT / ".github" / "workflows"
TEMPLATES = ROOT / "templates" / "project" / ".github" / "workflows"


def fail(message: str) -> None:
    raise AssertionError(message)


def workflow_text(name: str) -> str:
    return (CENTRAL / name).read_text(encoding="utf-8")


def all_workflow_files() -> list[Path]:
    return sorted([*CENTRAL.glob("*.yml"), *TEMPLATES.glob("*.yml")])


def assert_action_pinning() -> None:
    uses_re = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.M)
    for path in all_workflow_files():
        for ref in uses_re.findall(path.read_text(encoding="utf-8")):
            if ref.startswith("./"):
                continue
            if ref.startswith("iotyndall/agentic-platform-operations/") and ref.endswith("@PINNED_REF"):
                if TEMPLATES not in path.parents:
                    fail(f"PINNED_REF placeholder outside project templates: {path}: {ref}")
                continue
            if not re.search(r"@[0-9a-f]{40}$", ref):
                fail(f"moving/unpinned Action reference: {path}: {ref}")


def job_blocks(text: str) -> dict[str, str]:
    lines = text.splitlines()
    try:
        jobs_i = next(i for i, line in enumerate(lines) if line == "jobs:")
    except StopIteration:
        return {}
    blocks: dict[str, list[str]] = {}
    current = None
    for line in lines[jobs_i + 1 :]:
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if m:
            current = m.group(1)
            blocks[current] = [line]
        elif current is not None:
            if line and not line.startswith("  "):
                break
            blocks[current].append(line)
    return {k: "\n".join(v) for k, v in blocks.items()}


def assert_read_only_model_jobs() -> None:
    files = [
        "reusable-issue-router.yml",
        "reusable-product-intake.yml",
        "reusable-triage.yml",
        "reusable-engineering-review.yml",
        "reusable-learning.yml",
    ]
    for name in files:
        text = workflow_text(name)
        found_model = False
        found_writer = False
        for job_name, block in job_blocks(text).items():
            has_model = "anthropics/claude-code-action@" in block or "openai/codex-action@" in block
            has_write = bool(re.search(r"^\s{6}(?:contents|issues|pull-requests):\s*write\s*$", block, re.M))
            if has_model:
                found_model = True
                if has_write:
                    fail(f"read-only model job has repository write permission: {name}:{job_name}")
                if not re.search(r"^\s{6}contents:\s*read\s*$", block, re.M):
                    fail(f"model job lacks explicit contents: read: {name}:{job_name}")
            elif has_write:
                found_writer = True
        if not found_model:
            fail(f"expected model job missing: {name}")
        if not found_writer:
            fail(f"expected separate deterministic publisher/writer job missing: {name}")


def assert_dispatch_permission_contract() -> None:
    pairs = [
        ("reusable-issue-router.yml", "apply", "platform-issue-router.yml"),
        ("reusable-product-intake.yml", "publish", "platform-product-intake.yml"),
    ]
    for reusable_name, publisher_job, caller_name in pairs:
        reusable = workflow_text(reusable_name)
        block = job_blocks(reusable).get(publisher_job, "")
        if "repos/$GITHUB_REPOSITORY/dispatches" not in block:
            fail(f"expected repository_dispatch publisher missing: {reusable_name}:{publisher_job}")
        if not re.search(r"^\s{6}contents:\s*write\s*$", block, re.M):
            fail(f"repository_dispatch publisher lacks contents: write: {reusable_name}:{publisher_job}")
        caller = (TEMPLATES / caller_name).read_text(encoding="utf-8")
        if not re.search(r"^\s{2}contents:\s*write\s*$", caller, re.M):
            fail(f"caller caps dispatch workflow below required contents: write: {caller_name}")


def assert_routing_boundaries() -> None:
    router = workflow_text("reusable-issue-router.yml")
    dispatcher = workflow_text("reusable-incident-dispatcher.yml")
    if "feature: new or changed product capability/behavior" not in router:
        fail("issue router does not define feature intent")
    if "Auto-PR eligible:** `True`" in router:
        fail("issue router may not grant repair eligibility")
    if "'kind:feature' in labels" not in dispatcher:
        fail("reproduction dispatcher does not explicitly exclude features")
    if "{'kind:bug', 'kind:incident'}" not in dispatcher:
        fail("reproduction dispatcher does not require bug/incident kind")


def assert_repair_boundary() -> None:
    repair = workflow_text("reusable-bounded-repair.yml")
    if "gh pr create" not in repair:
        fail("bounded repair no longer produces a PR")
    for forbidden in ("gh pr merge", "kubectl apply", "terraform apply", "vercel --prod", "aws deploy"):
        if forbidden in repair:
            fail(f"bounded repair contains forbidden promotion command: {forbidden}")
    if "REPRODUCTION_SHA" not in repair or "REPRODUCTION_BRANCH" not in repair:
        fail("bounded repair is not bound to immutable reproduction evidence")


def assert_release_recovery_boundaries() -> None:
    release = workflow_text("reusable-release-gate.yml")
    rollback = workflow_text("reusable-rollback-gate.yml")
    mitigation = workflow_text("reusable-mitigation-gate.yml")
    for name, text in (("release", release), ("rollback", rollback), ("mitigation", mitigation)):
        for forbidden in ("vercel --prod", "kubectl apply", "terraform apply", "aws deploy", "supabase db"):
            if forbidden in text:
                fail(f"central {name} gate contains provider-specific/destructive command: {forbidden}")
    if "critical-risk releases require a human-led operational process" not in release:
        fail("critical-risk release hard stop missing")
    if "schema compatibility has not been mechanically proven" not in rollback:
        fail("rollback schema-compatibility hard stop missing")
    if "retry-idempotent-job" not in mitigation or "disable-feature-flag" not in mitigation:
        fail("bounded mitigation allowlist is missing")


def assert_template_fail_closed() -> None:
    scripts = ROOT / "templates" / "project" / "scripts" / "platform-ops"
    required = [
        "deploy-staging.sh",
        "deploy-production.sh",
        "rollback-production.sh",
        "check-rollback-compatibility.sh",
        "collect-slo.sh",
        "apply-mitigation.sh",
    ]
    for name in required:
        text = (scripts / name).read_text(encoding="utf-8")
        if "exit 78" not in text:
            fail(f"project adapter stub does not fail closed: {name}")

    prod = (TEMPLATES / "platform-production-release.yml").read_text(encoding="utf-8")
    if "workflow_dispatch:" not in prod or "group: deploy-production" not in prod or "cancel-in-progress: false" not in prod:
        fail("production release template lost manual/concurrency safeguards")
    if "environment: production" not in prod:
        fail("production release template does not use protected production environment")
    rollback = (TEMPLATES / "platform-production-rollback.yml").read_text(encoding="utf-8")
    if "reusable-rollback-gate.yml@PINNED_REF" not in rollback or "check-rollback-compatibility.sh" not in rollback:
        fail("rollback template bypasses compatibility/central authorization gate")


def assert_schemas_parse() -> None:
    for path in sorted((ROOT / "schemas").glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    tests = [
        assert_schemas_parse,
        assert_action_pinning,
        assert_read_only_model_jobs,
        assert_dispatch_permission_contract,
        assert_routing_boundaries,
        assert_repair_boundary,
        assert_release_recovery_boundaries,
        assert_template_fail_closed,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
