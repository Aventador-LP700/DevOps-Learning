"""Fixed teaching attacks for isolated containers or explicitly selected native practice."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from .controls import evaluate_scan, verify_artifact

ROOT = Path(__file__).resolve().parent.parent


def run_step(script, work, extra_env=None):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(work)}
    env.update(extra_env or {})
    result = subprocess.run(
        [sys.executable, str(ROOT / script)], cwd=work, env=env,
        text=True, capture_output=True, timeout=10,
    )
    return {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def injection(work):
    # Harmless proof: only create a marker inside this scenario's temporary directory.
    payload = "release; printf compromised > injected.txt; #"
    vulnerable = run_step("pipelines/vulnerable/metadata.py", work, {"CHANGE_TITLE": payload})
    exploited = (work / "injected.txt").read_text() == "compromised" if (work / "injected.txt").exists() else False
    (work / "injected.txt").unlink(missing_ok=True)
    hardened = run_step("pipelines/hardened/metadata.py", work, {"CHANGE_TITLE": payload})
    blocked = hardened["exit_code"] == 0 and not (work / "injected.txt").exists()
    return exploited, blocked, {"payload": payload, "vulnerable": vulnerable, "hardened": hardened}


def secrets(work):
    secret = "PP_SYNTHETIC_TOKEN_NOT_A_REAL_CREDENTIAL"
    vulnerable = run_step("pipelines/vulnerable/secrets.py", work, {"LAB_TOKEN": secret})
    hardened = run_step("pipelines/hardened/secrets.py", work, {"LAB_TOKEN": secret})
    exposed = secret in vulnerable["stdout"] + vulnerable["stderr"]
    blocked = secret not in hardened["stdout"] + hardened["stderr"] and hardened["exit_code"] == 0
    return exposed, blocked, {"synthetic_only": True, "detection": "Exact synthetic-token match in captured logs", "vulnerable": vulnerable, "hardened": hardened}


def artifact(work):
    path = work / "release.json"
    original = b'{"application":"demo","version":"1.0.0"}\n'
    path.write_bytes(original)
    trusted = hashlib.sha256(original).hexdigest()
    benign_verified = verify_artifact(path, trusted) == trusted
    path.write_text('{"application":"tampered","version":"1.0.0"}\n')
    vulnerable = json.loads(path.read_text())["application"] == "tampered"
    try:
        verify_artifact(path, trusted)
        blocked, message = False, "Unexpected acceptance"
    except ValueError as exc:
        blocked, message = True, str(exc)
    return vulnerable, blocked and benign_verified, {
        "trusted_digest": trusted,
        "received_digest": hashlib.sha256(path.read_bytes()).hexdigest(),
        "vulnerable": "Deployed modified JSON without integrity verification",
        "hardened": message,
        "benign_artifact_accepted": benign_verified,
        "trust_assumption": "Expected digest comes from trusted build state, not the mutable artifact store",
    }


def gate(work):
    report = json.loads((ROOT / "fixtures/trivy-vulnerable.json").read_text())
    policy = json.loads((ROOT / "policies/release.json").read_text())
    vulnerable = run_step("pipelines/vulnerable/gate.py", work, {"SCAN_REPORT": str(ROOT / "fixtures/trivy-vulnerable.json")})
    decision = evaluate_scan(report, policy)
    clean = evaluate_scan({"SchemaVersion": 2, "Results": [{"Target": "clean", "Vulnerabilities": None}]}, policy)
    return vulnerable["exit_code"] == 0, not decision["allowed"] and clean["allowed"], {
        "source": "Synthetic Trivy-format fixture; no scanner was executed in this exercise",
        "vulnerable": vulnerable, "hardened": decision, "clean_report_accepted": clean["allowed"],
    }


SCENARIOS = {
    "pipeline-injection": (injection, "Untrusted change metadata becomes a shell command", "CWE-78"),
    "secret-exposure": (secrets, "Build logging discloses a synthetic CI credential", "CWE-532"),
    "artifact-tampering": (artifact, "Mutable artifact storage changes deployment contents", "CWE-353"),
    "security-gate-bypass": (gate, "Advisory-only vulnerability scanning permits a release", "CWE-693"),
}


def run_scenario(name):
    fn, description, cwe = SCENARIOS[name]
    with tempfile.TemporaryDirectory(prefix="pipelineproof-") as directory:
        vulnerable, hardened, evidence = fn(Path(directory))
    return {"id": name, "description": description, "cwe": cwe,
            "vulnerable_exploited": bool(vulnerable), "hardened_blocked": bool(hardened),
            "passed": bool(vulnerable and hardened), "evidence": evidence}
