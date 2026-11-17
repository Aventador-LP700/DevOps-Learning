# Expansion validation — actual observations

Date: 17 November 2026. Original project baseline: `6bc8d3e`.
This record distinguishes local observations from hosted checks and future capabilities.
It does not turn an unrun integration into a successful scenario result.

## Batch execution

| Batch | New labs | Contract checks at that stage | Actual result |
|---|---|---|---|
| 1 | 06–10 | 15 | Passed |
| 2 | 11–15 | 30 cumulative | Passed |
| 3 | 16–20 | 45 cumulative | Passed |
| 4 | 21–25 | 60 cumulative | Passed |
| Integration | Original tests + 60 contracts + HTTP/edge checks | 89 total after quality-gate tests | Passed locally |
| Browser | Credentialed CORS and stored-XSS execution | 2 tests, both vulnerable/fixed modes | Passed in real Chromium |
| Native assessment | 24 local scenarios | Exploit, fix and positive observations | Passed |
| Docker assessment | 24 local scenarios | Same runner under restricted container | Passed |
| Semgrep | 5 checked-in rules | Fixed-code gate and separate teaching detections | 0 fixed-path findings; 6 expected teaching findings |

Commands actually run during implementation:

```bash
python3 -m unittest discover -s tests -p test_extended_labs.py -v
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s tests -p browser_labs.py -v
python3 -m lab.cli run --native --output reports/expanded
make lab
make report
python3 -m scripts.sast
python3 -m compileall -q app lab labs scripts tests
git diff --check
```

The SAST SQL taint rule initially produced a false positive by tainting subexpressions
inside a concatenation. It was corrected with an exact source match; the fixed code
then passed while the actual vulnerable SQL query still matched. No suppression or
secure-code rule exception was added.

## Preservation checks

The five original scenario README SHA256 values were recorded before editing and
verified unchanged after implementation. Existing pipeline implementations and
original HTTP application code were not replaced. AST comparison verified that all
original functions in `lab/scenarios.py` remain unchanged; registration is additive.
The existing native integration assertion was updated from 4 to 24 expected results,
retaining its original checks for reports, API startup, paths and forbidden tools.

## Durable evidence

- [Expanded native assessment](evidence/expanded-native.json)
- [Expanded Docker assessment](evidence/expanded-docker.json)
- [SAST summary](evidence/expanded-sast.json)
- Per-lab `test_lab.py` and attack observations under `labs/`

These are actual local snapshots during the expansion. They contain synthetic data
only. Current workflow runs identify the exact tested commit; generated artifacts
expire according to retention policy.

## Hosted integrations and limitations

Hosted results are recorded below. The
local rootless Docker daemon cannot start kind without systemd delegation; the
preserved real-cluster workflow is used for that integration. The managed workspace
also has limited disk space: a Docker rebuild initially exhausted it; generated
scanner/build caches were cleaned and the restricted-container assessment passed.

The original image gate has known HIGH/CRITICAL dependency findings. This is a
visible release limitation, not an exercise regression and not a waived control.
Optional Trivy filesystem/dependency and ZAP runs must be reported by their actual
outcomes, not inferred from unit tests. Browser tests use Playwright 1.62.0;
Semgrep is pinned to 1.185.0. Linux is the tested native platform; macOS/WSL2 need
independent platform validation. No production key custody, distributed limiter,
SIEM stack, real package takeover or full authenticated DAST is claimed.

## Final hosted outcomes

- [Core CI, commit 15f4962](https://github.com/Aventador-LP700/DevOps-Learning/actions/runs/44106680770):
  **passed** native, Docker, browser and SAST jobs. The fixed password KDF now uses
  scrypt N=16384, r=8, p=5 with a per-record random salt; its regression contract passed.
- [Real Kubernetes API, expansion commit 35f75db](https://github.com/Aventador-LP700/DevOps-Learning/actions/runs/44105056367):
  **passed** deployment, vulnerable Secret read, hardened Forbidden response and
  allowed deployment patch. This preserves the real scenario 05 integration.
- [Security tools, commit 15f4962](https://github.com/Aventador-LP700/DevOps-Learning/actions/runs/44106863090):
  **passed** filesystem/dependency/misconfiguration/secret scanning, source/history
  checks, signed-SBOM original/tamper verification and secure-app ZAP DAST.
  **Blocked:** actual image release due to HIGH/CRITICAL dependency findings.
  The overall manual workflow is therefore **failure**, not falsely reported green.

The ZAP integration initially reached the app but failed to write reports. A retry
showed that assigning volume ownership alone was insufficient. The final wrapper
uses a no-copy disposable report volume, retains an initialization marker and tests
write access as the image's non-root user before scanning. It exports the actual
reports, removes the scanner/volume, and passes the medium/high-alert gate. The
secure app also gained explicit COOP/COEP/CORP browser-isolation headers; real-browser
and HTTP regressions passed after that change. No alert was suppressed to obtain success.

[Machine-readable run outcomes](evidence/expanded-hosted.json) and the
[ZAP policy log excerpt](evidence/expanded-zap.txt) preserve the observed conclusions.
JSON/HTML/Markdown ZAP reports, Trivy JSON/SARIF, SAST JSON/SARIF, core assessments
and signed-SBOM evidence are uploaded to the corresponding workflow runs. Private
signing keys are never uploaded. Gitleaks found no secrets in the staged source
snapshot or repository history; the hosted history check also passed.

Local evidence files represent snapshots taken during implementation, so older
records may show the earlier password work factor. Use the commit-linked hosted
runs above for final-code verification. The original 01–05 walkthroughs remain
byte-for-byte unchanged. No scenario is labeled implemented solely because it has
a README; all 20 new packages have executable pairs and passing regression contracts.
