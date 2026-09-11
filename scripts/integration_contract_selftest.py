#!/usr/bin/env python3
"""Regression checks for reusable-workflow integration contracts discovered in live adopters."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    node_ci = (WORKFLOWS / "reusable-node-ci.yml").read_text(encoding="utf-8")
    security = (WORKFLOWS / "reusable-security.yml").read_text(encoding="utf-8")
    audit_parser = (ROOT / "scripts" / "extract_critical_advisories.py").read_text(encoding="utf-8")

    require("grep -q $'\\n'" not in node_ci,
            "Node CI reintroduced the grep-newline bug that rejects every nonempty contract value")
    require("[[ \"$value\" == *$'\\n'* ]]" in node_ci,
            "Node CI no longer checks embedded newlines safely")

    require("scripts/extract_critical_advisories.py" in security,
            "Security ratchet no longer delegates audit evidence parsing to the tested parser")
    require("data.get(\"advisories\")" in audit_parser and "data.get(\"vulnerabilities\")" in audit_parser,
            "Security ratchet parser must support both legacy and npm audit v2 evidence shapes")
    require("lower() != \"critical\"" in audit_parser,
            "Security ratchet parser no longer filters advisory evidence structurally to critical severity")
    require("GHSA_RE" in audit_parser and "github_advisory_id" in audit_parser,
            "Security ratchet parser no longer resolves canonical GHSA identifiers")
    require("declared_critical == 0" in audit_parser,
            "npm audit v2 parser no longer proves zero-critical lower-severity evidence from metadata")
    require("no critical GHSA identifier could be resolved" in audit_parser,
            "Security ratchet parser no longer fails closed on ambiguous critical evidence")
    require("grep -Eo 'GHSA-" not in security,
            "Security ratchet reverted to scraping arbitrary GHSA references from audit prose")
    require("found-critical-ghsa.txt" in security,
            "Security ratchet no longer materializes an explicit critical-advisory evidence set")

    require("ANTHROPIC_API_KEY[[:space:]]" not in security,
            "Secret guard again treats generic documented ANTHROPIC_API_KEY assignments as secrets")
    require("OPENAI_API_KEY[[:space:]]" not in security,
            "Secret guard again treats generic documented OPENAI_API_KEY assignments as secrets")
    require("sk-ant-[A-Za-z0-9_-]{20,}" in security,
            "Secret guard lost high-confidence Anthropic token detection")
    require("private-key-block" in security and "{80,}" in security,
            "Secret guard no longer requires a substantive private-key block")

    print("PASS live integration contract regressions")


if __name__ == "__main__":
    main()
