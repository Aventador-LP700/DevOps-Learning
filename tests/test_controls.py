import hashlib
import tempfile
from pathlib import Path
import unittest
from lab.controls import evaluate_scan, verify_artifact
from lab.cli import render_markdown

POLICY = {"blocked_severities": ["HIGH", "CRITICAL"], "require_scan_results": True}

class GateTests(unittest.TestCase):
    def test_checks_all_targets(self):
        report = {"SchemaVersion": 2, "Results": [{"Target": "first", "Vulnerabilities": []}, {"Target": "second", "Vulnerabilities": [{"Severity": "CRITICAL", "VulnerabilityID": "LAB-1"}]}]}
        self.assertEqual(evaluate_scan(report, POLICY), {"allowed": False, "blocked_findings": ["LAB-1"]})

    def test_clean_trivy_null_is_accepted(self):
        self.assertTrue(evaluate_scan({"SchemaVersion": 2, "Results": [{"Target": "clean", "Vulnerabilities": None}]}, POLICY)["allowed"])

    def test_invalid_scans_fail_closed(self):
        for report in ([], {}, {"Results": []}, {"Results": None}, {"Results": [3]}, {"SchemaVersion": 2, "Results": [{"Target": "bad", "Vulnerabilities": "bad"}]}, {"SchemaVersion": 2, "Results": [{"Target": "bad", "Vulnerabilities": [{"Severity": "TYPO"}]}]}, {"SchemaVersion": 2, "Results": [{}]}):
            with self.subTest(report=report), self.assertRaises(ValueError):
                evaluate_scan(report, POLICY)

    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_scan({"SchemaVersion": 2, "Results": [{"Target": "clean"}]}, {"blocked_severities": []})

class ArtifactTests(unittest.TestCase):
    def test_valid_then_tampered(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact"
            path.write_bytes(b"original")
            expected = hashlib.sha256(b"original").hexdigest()
            self.assertEqual(verify_artifact(path, expected), expected)
            path.write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                verify_artifact(path, expected)

    def test_invalid_digest_rejected(self):
        with self.assertRaises(ValueError):
            verify_artifact(Path("does-not-exist"), "not-a-digest")

class ReportTests(unittest.TestCase):
    def test_failure_visible(self):
        report = {"generated_at": "test", "results": [{"id": "broken", "passed": False, "vulnerable_exploited": True, "hardened_blocked": False}]}
        self.assertIn("| broken | True | False | FAIL |", render_markdown(report))
