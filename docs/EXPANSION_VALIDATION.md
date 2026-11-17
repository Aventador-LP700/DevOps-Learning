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

Hosted CI/security run links and outcomes will be appended after publication. The
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
