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

    require("grep -q $'\\n'" not in node_ci,
            "Node CI reintroduced the grep-newline bug that rejects every nonempty contract value")
    require("[[ \"$value\" == *$'\\n'* ]]" in node_ci,
            "Node CI no longer checks embedded newlines safely")

    require("str(advisory.get('severity', '')).lower() != 'critical'" in security,
            "Security ratchet no longer filters audit evidence structurally to critical severity")
    require("advisory.get('github_advisory_id')" in security,
            "Security ratchet no longer reads the advisory's canonical GHSA field")
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
