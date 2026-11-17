# Security gates and intentional findings

The teaching assessment and release-risk decision have different meanings. A lab
passes only when its exploit occurs and its fixed/positive retests succeed. A
security gate must still fail if a fixed application or released dependency violates
policy. Existing image findings are not silently waived to make the project green.

## Scope separation

`python3 -m scripts.sast` builds an explicit fixed-code target list: the original
app/runner/security-script/hardened pipeline code, shared lab infrastructure and every `secure.py`
and `data.py`. It fails on any finding under the checked-in five-rule policy and
writes JSON plus SARIF. The rules cover shell invocation, unsafe pickle, MD5,
concatenated SQL and fail-open exception handling. This is focused coverage, not a
claim to detect every OWASP category.

A second, clearly labeled scan checks `labs/*/vulnerable.py` and the preserved
`pipelines/vulnerable/` separately. Its findings are expected teaching evidence and
do not approve a production release. The command also requires known teaching
findings to be detected, failing on scanner/rule drift. There are no inline
`nosemgrep` suppressions and no secure-code rule exclusions.

The Trivy filesystem scan copies the same fixed-code scope plus hardened deployment
manifests and the Dockerfile into `.work/release-scan/`. It also copies optional
browser-tool requirements to `requirements.txt` for analyzer recognition. This is
an explicit **scan snapshot**, not a runnable production bundle: it excludes
intentionally vulnerable modules/fixtures and must not be presented as a full-repo
clean bill of health. Core native labs have no third-party runtime dependencies;
this manifest covers optional browser tooling. Image scanning additionally checks
OS and bundled Python packages in the actual built lab image.

Gitleaks scans the entire Git history, including teaching code; no path allowlist
hides accidental real secrets. Ephemeral generated keys and reports remain ignored.
Only the SBOM public key, never its private key, is uploaded as signing evidence.

## Policy and outputs

| Check | Blocking policy | Evidence |
|---|---|---|
| Unit/HTTP/edge contracts | Any failed assertion or missing exploit/fix/positive observation | Job log and assessment JSON/Markdown |
| Browser integration | Any mismatch in actual stored-XSS execution or credentialed CORS read | Browser job log |
| Semgrep fixed paths | Any finding under the local policy | `semgrep-secure.json`, `.sarif` |
| Semgrep teaching paths | Missing expected detection or scanner failure | `semgrep-intentional.json`; findings explicitly expected |
| Trivy filesystem/dependency/misconfiguration/secrets | HIGH/CRITICAL findings or scanner errors | `trivy-fs.json`, `.sarif` |
| Trivy actual container | HIGH/CRITICAL vulnerability findings; malformed/missing report | `trivy.json`, `trivy-image.sarif` |
| Gitleaks history | Any secret finding or scanner failure | Redacted JSON/job log |
| ZAP baseline secure app | Medium/high alerts, configured baseline failures, malformed report or scanner errors | `zap.json`, `.html`, `.md` |
| SBOM integrity | Original fails verification or modified bytes verify | SPDX SBOM, detached signature, public key, job log |

ZAP baseline can return 2 for warnings. The wrapper retains every alert and applies
the explicit risk policy above: low/informational alerts are reviewed but do not
block; medium/high alerts do block. Baseline exit 1 remains a failure, and runtime
errors do not become a pass. No vulnerable HTTP instance is used as the DAST target.
The scan is passive baseline DAST; it is not a complete authenticated penetration test.

SARIF is produced where the installed tools support it (Semgrep/Trivy) and uploaded
as build evidence. No `security-events: write` permission is needed merely to store
SARIF artifacts. Uploading to GitHub code scanning can be configured separately.
ZAP's supported baseline JSON/HTML/Markdown outputs are retained rather than claiming
native SARIF support it does not provide here.

## Workflows

- Existing `Validate PipelineProof` now retains native/Docker jobs and adds isolated
  browser and SAST jobs on pushes/PRs. Permissions stay `contents: read`.
- Existing manual Kubernetes integration remains the real-cluster retest.
- Existing manual `Live security tools` retains image gating, source/history checks
  and signed SBOM, and adds filesystem/dependency checks and secure-app ZAP DAST.
- Actions are pinned to immutable commits. Download helper checks pinned release
  SHA256s. ZAP uses a pinned image digest. Dependency tooling is explicitly versioned.
- No PR metadata is interpolated into shell source and no job receives cloud keys,
  write-capable checkout credentials or organization runner registration tokens.

## Known release limitation

The pinned base image previously produced HIGH/CRITICAL findings. The current image
gate is intentionally allowed to fail visibly until its dependencies are remediated;
there is no `continue-on-error` to turn that release decision into a pass. Review
actual runs in the validation record. A successful exercise suite demonstrates
learning behavior, not production readiness or complete vulnerability coverage.
