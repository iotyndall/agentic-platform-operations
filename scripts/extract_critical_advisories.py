#!/usr/bin/env python3
"""Extract critical GHSA identifiers from npm audit JSON.

Supports both npm audit report shapes currently seen in the platform:

- legacy/v1: top-level ``advisories`` object with ``github_advisory_id``;
- current/v2: top-level ``vulnerabilities`` object whose ``via`` arrays contain
  advisory objects with GitHub advisory URLs.

The parser fails closed when the report says critical vulnerabilities exist but
cannot bind them to concrete GHSA identifiers. That preserves the security
ratchet's core property: an ambiguous critical result is never silently ignored.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

GHSA_RE = re.compile(r"GHSA-[A-Za-z0-9-]+")


class AuditEvidenceError(ValueError):
    pass


def _ghsa_from_advisory(advisory: dict[str, Any]) -> str | None:
    direct = advisory.get("github_advisory_id")
    if isinstance(direct, str) and GHSA_RE.fullmatch(direct):
        return direct

    for key in ("url", "source_url", "advisory_url"):
        value = advisory.get(key)
        if isinstance(value, str):
            match = GHSA_RE.search(value)
            if match:
                return match.group(0)
    return None


def extract_critical_ghsas(data: dict[str, Any]) -> list[str]:
    advisories = data.get("advisories")
    if isinstance(advisories, dict):
        critical: set[str] = set()
        malformed: list[str] = []
        for advisory in advisories.values():
            if not isinstance(advisory, dict):
                continue
            if str(advisory.get("severity", "")).lower() != "critical":
                continue
            ghsa = _ghsa_from_advisory(advisory)
            if ghsa is None:
                malformed.append(repr(advisory.get("github_advisory_id")))
            else:
                critical.add(ghsa)
        if malformed:
            raise AuditEvidenceError(
                "Critical advisories were present without valid GHSA IDs: "
                + ", ".join(malformed)
            )
        return sorted(critical)

    vulnerabilities = data.get("vulnerabilities")
    if isinstance(vulnerabilities, dict):
        critical: set[str] = set()
        unresolved_critical_entries: list[str] = []

        # npm audit v2 represents transitive severity at the vulnerability node,
        # while the actual GitHub advisory normally appears in a ``via`` object.
        # Scan advisory objects globally so a direct package whose ``via`` is a
        # string can still be resolved through the underlying vulnerable package.
        for package_name, vulnerability in vulnerabilities.items():
            if not isinstance(vulnerability, dict):
                continue
            for via in vulnerability.get("via", []) or []:
                if not isinstance(via, dict):
                    continue
                if str(via.get("severity", "")).lower() != "critical":
                    continue
                ghsa = _ghsa_from_advisory(via)
                if ghsa is None:
                    unresolved_critical_entries.append(str(package_name))
                else:
                    critical.add(ghsa)

        metadata = data.get("metadata")
        declared_critical: int | None = None
        if isinstance(metadata, dict):
            counts = metadata.get("vulnerabilities")
            if isinstance(counts, dict) and isinstance(counts.get("critical"), int):
                declared_critical = counts["critical"]

        severity_critical_packages = [
            name
            for name, vulnerability in vulnerabilities.items()
            if isinstance(vulnerability, dict)
            and str(vulnerability.get("severity", "")).lower() == "critical"
        ]

        if unresolved_critical_entries:
            raise AuditEvidenceError(
                "Critical npm audit advisory objects were present without resolvable GHSA IDs: "
                + ", ".join(sorted(set(unresolved_critical_entries)))
            )

        # Metadata is the strongest v2 count signal. If it says no critical
        # vulnerabilities, a non-zero audit exit may safely represent only lower
        # severities. If it says critical findings exist, require at least one
        # concrete GHSA before allowing the ratchet comparison to proceed.
        if declared_critical is not None:
            if declared_critical == 0:
                return []
            if not critical:
                raise AuditEvidenceError(
                    f"npm audit reports {declared_critical} critical vulnerability/vulnerabilities "
                    "but no critical GHSA identifier could be resolved"
                )
        elif severity_critical_packages and not critical:
            raise AuditEvidenceError(
                "npm audit contains critical vulnerability nodes but no critical GHSA identifier "
                "could be resolved: " + ", ".join(sorted(severity_critical_packages))
            )

        return sorted(critical)

    raise AuditEvidenceError(
        "Dependency audit JSON contains neither an advisories object nor a vulnerabilities object; "
        "refusing ambiguous security evidence."
    )


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <audit.json> <critical-ghsa-output.txt>", file=sys.stderr)
        return 2

    source = Path(argv[1])
    destination = Path(argv[2])
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"::error::Dependency audit did not emit parseable JSON: {exc}", file=sys.stderr)
        return 1

    try:
        critical = extract_critical_ghsas(data)
    except AuditEvidenceError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    destination.write_text("".join(f"{ghsa}\n" for ghsa in critical), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
