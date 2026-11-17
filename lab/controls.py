"""Production-style controls, kept separate from intentionally vulnerable steps."""
import hashlib
import json
import re

SHA256 = re.compile(r"[a-f0-9]{64}")
KNOWN_SEVERITIES = {"UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"}

def verify_artifact(path, trusted_digest):
    if not isinstance(trusted_digest, str) or not SHA256.fullmatch(trusted_digest):
        raise ValueError("Invalid trusted SHA256 digest")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != trusted_digest:
        raise ValueError("Artifact integrity verification failed")
    return actual

def evaluate_scan(report, policy):
    """Fail closed on malformed Trivy vulnerability reports; gate all findings."""
    if not isinstance(report, dict) or report.get("SchemaVersion") != 2:
        raise ValueError("Expected Trivy SchemaVersion 2 report")
    if not isinstance(policy, dict):
        raise ValueError("Invalid policy")
    blocked = policy.get("blocked_severities")
    if not isinstance(blocked, list) or not blocked or any(s not in KNOWN_SEVERITIES for s in blocked):
        raise ValueError("Invalid severity policy")
    results = report.get("Results")
    if not isinstance(results, list) or (policy.get("require_scan_results", True) and not results):
        raise ValueError("Missing scan results")
    findings = []
    for result in results:
        if not isinstance(result, dict):
            raise ValueError("Invalid scan result")
        if not isinstance(result.get("Target"), str) or not result["Target"]:
            raise ValueError("Missing scan target")
        vulns = result.get("Vulnerabilities", [])
        if vulns is None:
            vulns = []  # Trivy uses null for targets without vulnerabilities.
        if not isinstance(vulns, list):
            raise ValueError("Invalid vulnerability list")
        for item in vulns:
            if not isinstance(item, dict) or item.get("Severity") not in KNOWN_SEVERITIES:
                raise ValueError("Invalid vulnerability severity")
            if item["Severity"] in blocked:
                findings.append(item.get("VulnerabilityID", "unspecified"))
    return {"allowed": not findings, "blocked_findings": findings}

def load_gate(report_path, policy_path):
    return evaluate_scan(json.loads(report_path.read_text()), json.loads(policy_path.read_text()))
