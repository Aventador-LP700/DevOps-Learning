# PipelineProof assessment

Generated: 2026-11-17T13:50:46.887453+00:00

Scope: disposable local teaching lab; synthetic secrets and findings.

| Scenario | Vulnerable exploit observed | Hardened control blocked attack | Result |
|---|---|---|---|
| pipeline-injection | True | True | PASS |
| secret-exposure | True | True | PASS |
| artifact-tampering | True | True | PASS |
| security-gate-bypass | True | True | PASS |

## Evidence

### pipeline-injection

```json
{
  "id": "pipeline-injection",
  "description": "Untrusted change metadata becomes a shell command",
  "cwe": "CWE-78",
  "vulnerable_exploited": true,
  "hardened_blocked": true,
  "passed": true,
  "evidence": {
    "payload": "release; printf compromised > injected.txt; #",
    "vulnerable": {
      "exit_code": 0,
      "stdout": "release\n",
      "stderr": ""
    },
    "hardened": {
      "exit_code": 0,
      "stdout": "release; printf compromised > injected.txt; #\n",
      "stderr": ""
    }
  }
}
```

### secret-exposure

```json
{
  "id": "secret-exposure",
  "description": "Build logging discloses a synthetic CI credential",
  "cwe": "CWE-532",
  "vulnerable_exploited": true,
  "hardened_blocked": true,
  "passed": true,
  "evidence": {
    "synthetic_only": true,
    "detection": "Exact synthetic-token match in captured logs",
    "vulnerable": {
      "exit_code": 0,
      "stdout": "Connecting with token=PP_SYNTHETIC_TOKEN_NOT_A_REAL_CREDENTIAL\n",
      "stderr": ""
    },
    "hardened": {
      "exit_code": 0,
      "stdout": "Credential supplied; authentication step configured\n",
      "stderr": ""
    }
  }
}
```

### artifact-tampering

```json
{
  "id": "artifact-tampering",
  "description": "Mutable artifact storage changes deployment contents",
  "cwe": "CWE-353",
  "vulnerable_exploited": true,
  "hardened_blocked": true,
  "passed": true,
  "evidence": {
    "trusted_digest": "70d1cf5744ec0f5e2244bd87c312d5adaff608af759ea9538603ae472083cd9f",
    "received_digest": "fc77b6f38417cca6446a70bc4ccc6c6f3c148cbc599bc7c54b8545402734d01a",
    "vulnerable": "Deployed modified JSON without integrity verification",
    "hardened": "Artifact integrity verification failed",
    "benign_artifact_accepted": true,
    "trust_assumption": "Expected digest comes from trusted build state, not the mutable artifact store"
  }
}
```

### security-gate-bypass

```json
{
  "id": "security-gate-bypass",
  "description": "Advisory-only vulnerability scanning permits a release",
  "cwe": "CWE-693",
  "vulnerable_exploited": true,
  "hardened_blocked": true,
  "passed": true,
  "evidence": {
    "source": "Synthetic Trivy-format fixture; no scanner was executed in this exercise",
    "vulnerable": {
      "exit_code": 0,
      "stdout": "{\"SchemaVersion\": 2, \"ArtifactName\": \"pipelineproof-teaching-fixture\", \"Results\": [{\"Target\": \"synthetic-package\", \"Vulnerabilities\": [{\"VulnerabilityID\": \"LAB-EXAMPLE-001\", \"PkgName\": \"synthetic-library\", \"InstalledVersion\": \"0.0.1\", \"FixedVersion\": \"0.0.2\", \"Severity\": \"CRITICAL\", \"Title\": \"Synthetic finding for policy testing; not a real CVE\"}]}]}\nAdvisory scan completed. Release allowed regardless of findings.\n",
      "stderr": ""
    },
    "hardened": {
      "allowed": false,
      "blocked_findings": [
        "LAB-EXAMPLE-001"
      ]
    },
    "clean_report_accepted": true
  }
}
```

## Interpretation

PASS means the expected lab exploit occurred and its hardened retest blocked it.
It does not certify a production pipeline. Kubernetes RBAC and live scanner runs are separate exercises.
