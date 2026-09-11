#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path

from extract_critical_advisories import AuditEvidenceError, extract_critical_ghsas, main


class ExtractCriticalAdvisoriesTests(unittest.TestCase):
    def test_legacy_v1_extracts_only_critical(self):
        data = {
            "advisories": {
                "1": {"severity": "moderate", "github_advisory_id": "GHSA-mmmm-1111-2222"},
                "2": {"severity": "critical", "github_advisory_id": "GHSA-crit-1111-2222"},
            }
        }
        self.assertEqual(extract_critical_ghsas(data), ["GHSA-crit-1111-2222"])

    def test_npm_v2_zero_critical_accepts_lower_severity_nonzero_audit(self):
        data = {
            "auditReportVersion": 2,
            "vulnerabilities": {
                "express": {
                    "severity": "moderate",
                    "via": [
                        {
                            "severity": "moderate",
                            "url": "https://github.com/advisories/GHSA-x5fp-wj9c-mxmx",
                        }
                    ],
                }
            },
            "metadata": {"vulnerabilities": {"moderate": 1, "critical": 0, "total": 1}},
        }
        self.assertEqual(extract_critical_ghsas(data), [])

    def test_npm_v2_extracts_critical_advisory_url(self):
        data = {
            "auditReportVersion": 2,
            "vulnerabilities": {
                "direct-package": {"severity": "critical", "via": ["transitive-package"]},
                "transitive-package": {
                    "severity": "critical",
                    "via": [
                        {
                            "severity": "critical",
                            "url": "https://github.com/advisories/GHSA-abcd-1234-wxyz",
                        }
                    ],
                },
            },
            "metadata": {"vulnerabilities": {"critical": 2, "total": 2}},
        }
        self.assertEqual(extract_critical_ghsas(data), ["GHSA-abcd-1234-wxyz"])

    def test_npm_v2_fails_closed_when_critical_count_has_no_ghsa(self):
        data = {
            "auditReportVersion": 2,
            "vulnerabilities": {
                "mystery": {"severity": "critical", "via": ["another-package"]}
            },
            "metadata": {"vulnerabilities": {"critical": 1, "total": 1}},
        }
        with self.assertRaises(AuditEvidenceError):
            extract_critical_ghsas(data)

    def test_unknown_shape_fails_closed(self):
        with self.assertRaises(AuditEvidenceError):
            extract_critical_ghsas({"metadata": {}})

    def test_cli_writes_sorted_unique_ids(self):
        data = {
            "advisories": {
                "1": {"severity": "critical", "github_advisory_id": "GHSA-zzzz-1111-2222"},
                "2": {"severity": "critical", "github_advisory_id": "GHSA-aaaa-1111-2222"},
                "3": {"severity": "critical", "github_advisory_id": "GHSA-zzzz-1111-2222"},
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "audit.json"
            output = Path(tmp) / "critical.txt"
            source.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(main(["extract_critical_advisories.py", str(source), str(output)]), 0)
            self.assertEqual(
                output.read_text(encoding="utf-8"),
                "GHSA-aaaa-1111-2222\nGHSA-zzzz-1111-2222\n",
            )


if __name__ == "__main__":
    unittest.main()
