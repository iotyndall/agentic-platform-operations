#!/usr/bin/env python3
"""Dependency-free validation for platform-ops project contracts.

This intentionally validates the safety-critical subset without requiring a
JSON Schema package on every caller. The JSON Schema remains the human/tooling
contract; this script is the CI backstop for invariants we never want to lose.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DEFAULT_ESCALATION = {
    "authentication",
    "authorization",
    "secrets",
    "destructive-data",
    "irreversible-migrations",
    "payments",
}


def fail(path: Path, message: str) -> None:
    raise ValueError(f"{path}: {message}")


def validate(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("version") != 1:
        fail(path, "version must be 1")

    project = data.get("project") or {}
    if not re.fullmatch(r"[^/]+/[^/]+", str(project.get("repository", ""))):
        fail(path, "project.repository must be OWNER/REPO")
    level = project.get("autonomyLevel")
    if not isinstance(level, int) or not 0 <= level <= 5:
        fail(path, "autonomyLevel must be integer 0..5")

    commands = data.get("commands") or {}
    for key in ("install", "build"):
        if not isinstance(commands.get(key), str) or not commands[key].strip():
            fail(path, f"commands.{key} is required")
    for key, value in commands.items():
        if not isinstance(value, str):
            fail(path, f"commands.{key} must be a string")
        if "\n" in value or "\r" in value:
            fail(path, f"commands.{key} must be one line")

    risk = data.get("risk") or {}
    protected = risk.get("protectedPathRegex")
    if not isinstance(protected, str) or not protected:
        fail(path, "risk.protectedPathRegex is required")
    try:
        re.compile(protected)
    except re.error as exc:
        fail(path, f"protectedPathRegex does not compile: {exc}")

    max_lines = risk.get("maxAutonomousProductionLines")
    if not isinstance(max_lines, int) or not 1 <= max_lines <= 500:
        fail(path, "maxAutonomousProductionLines must be 1..500")
    attempts = risk.get("maxRepairAttempts")
    if not isinstance(attempts, int) or not 1 <= attempts <= 5:
        fail(path, "maxRepairAttempts must be 1..5")

    domains = set(risk.get("escalationDomains") or [])
    missing = DEFAULT_ESCALATION - domains
    if missing:
        fail(path, f"cannot remove default escalation domains: {sorted(missing)}")

    security = data.get("security") or {}
    allowlist = security.get("criticalAdvisoryAllowlist") or []
    for advisory in allowlist:
        if not re.fullmatch(r"GHSA-[a-z0-9-]+", advisory):
            fail(path, f"invalid GHSA advisory id: {advisory}")

    production = data.get("production") or {}
    journeys = production.get("criticalJourneys") or []
    if not journeys:
        fail(path, "at least one production critical journey is required")
    ids: set[str] = set()
    for journey in journeys:
        jid = str(journey.get("id", ""))
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", jid):
            fail(path, f"invalid critical journey id: {jid!r}")
        if jid in ids:
            fail(path, f"duplicate critical journey id: {jid}")
        ids.add(jid)
        if journey.get("owner") not in {"local", "central"}:
            fail(path, f"journey {jid} owner must be local|central")

    repair = data.get("repair") or {}
    if repair.get("enabled"):
        if project.get("autonomyLevel", 0) < 2:
            fail(path, "repair.enabled requires autonomyLevel >= 2")
        if repair.get("minimumConfidence") != "high":
            fail(path, "v1 autonomous repair requires high confidence")
        if not repair.get("issueLabel"):
            fail(path, "repair.issueLabel is required when repair is enabled")
        provenance = repair.get("provenanceRegex") or ""
        if provenance:
            try:
                re.compile(provenance)
            except re.error as exc:
                fail(path, f"repair.provenanceRegex does not compile: {exc}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} contract.json [contract.json ...]", file=sys.stderr)
        return 2
    failures = []
    for raw in argv[1:]:
        path = Path(raw)
        try:
            validate(path)
        except Exception as exc:  # deliberate aggregate reporting
            failures.append(str(exc))
        else:
            print(f"OK  {path}")
    if failures:
        for message in failures:
            print(f"FAIL {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
