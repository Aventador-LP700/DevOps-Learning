# Operating the expanded lab

## Native mode

Requirements: Python 3.10+, Bash, POSIX sh and printf. The core implementation uses
only Python's standard library; browser/security scanners are optional separate tools.

```bash
git pull
bash ./setup.sh --lab-only
cat reports/assessment.md
python3 -m lab.cli list
python3 -m lab.cli run --native --scenario sql-injection --output reports/sql-injection
python3 -m unittest labs.sql_injection.test_lab -v
python3 -m unittest discover -s tests -v
```

`bash ./setup.sh` additionally starts the original demo API on localhost:8080 after
24 exercises. Ctrl+C stops it. `--serve-only` retains the original lightweight API
behavior. The existing native setup, container deployment and scenario IDs still work.

The assessment contains 24 results, not 25 fabricated passes: scenario 05 uses a
real Kubernetes API and is operated separately. Local SSRF/registry fixtures bind
to random 127.0.0.1 ports and are closed by their context managers. Attack files and
SQLite databases are temporary; exported JSON/Markdown persists until removed.

## HTTP application labs

The new HTTP adapter is separate from the original three-route deployment API.
It reuses the actual fixed/vulnerable modules; it does not pretend every exercise
is a separate web application. Modules not listed below run through the CLI.

```bash
python3 -m labs.web --port 8081
# Explicitly opt into vulnerable mode instead, on another port if desired:
python3 -m labs.web --port 8083 --vulnerable --enable-vulnerable-labs
```

Both bind only to 127.0.0.1. A single vulnerable flag is rejected. Stop either service
with Ctrl+C. All server state, synthetic files and comments are discarded on exit.
Do not add port forwarding, public reverse proxies or real accounts.

Create a synthetic authenticated session against either local instance:

```bash
curl -c reports/lab-cookies.txt -H 'Content-Type: application/json'   -d '{"user":"alice","password":"dummy-correct-horse"}' http://127.0.0.1:8081/api/login
curl -b reports/lab-cookies.txt http://127.0.0.1:8081/api/orders/200
curl -b reports/lab-cookies.txt http://127.0.0.1:8081/api/orders/100
rm -f reports/lab-cookies.txt
```

The first order request is forbidden in fixed mode; Alice's own order is allowed.
The same synthetic credential is intentionally public; it is not a production login.
The adapter does not claim to use scenario 14's password database: password-storage
practice remains its own executable module.

| Route | Method | Practice |
|---|---|---|
| `/health`, `/` | GET | Mode/health and local landing page |
| `/api/session`, `/api/login` | GET, POST respectively | Session creation, rotation and login throttling |
| `/api/orders/100`, `/api/orders/200` | GET | Object ownership |
| `/api/profile` | GET, POST | CORS reads and protected-field updates |
| `/api/admin/deactivate` | POST | Function-level authorization; JSON `target` field |
| `/api/debug` | GET | Exception disclosure; synthetic 500 response |
| `/api/files?name=welcome.txt` | GET | Public/private synthetic filesystem boundary |
| `/comments`, `/api/comments` | GET, POST respectively | Stored comment rendering; JSON `body` field |

State-changing routes require JSON and authentication where appropriate. Fixed mode
rejects cross-origin POSTs and unexpected Host headers. No HTTP route exposes shell
commands, pickle restoration, arbitrary SSRF destinations or arbitrary package installs.

## Browser integration

```bash
python3 -m venv .work/browser-venv
.work/browser-venv/bin/pip install -r requirements-dev.txt
.work/browser-venv/bin/python -m playwright install chromium
.work/browser-venv/bin/python -m unittest discover -s tests -p browser_labs.py -v
```

On Linux CI, `playwright install --with-deps chromium` also installs OS browser
libraries. Native exercises do not need these. Tests use fresh browser contexts,
synthetic sessions and temporary loopback services, never an existing signed-in browser.

## Docker and Kubernetes

```bash
make lab
make report
make up
make down
make k8s-up k8s-test
make k8s-down
```

Docker lab mode has no external network and no host Docker-socket/checkout mounts.
Loopback fixture requests still work inside that container. The original namespace
RBAC exercise uses the dedicated `kind-pipelineproof` context. No fake local RBAC
simulation replaces it. `make clean` removes the Compose evidence volume.

## Security tools

```bash
bash scripts/install_tools.sh trivy syft cosign gitleaks
export PATH="$PWD/.work/bin:$PATH"
# Install Semgrep 1.185.0 via pipx or a dedicated virtual environment.
python3 -m scripts.sast
python3 -m scripts.fs_scan
make scan
bash scripts/supply_chain.sh
python3 -m scripts.zap
```

ZAP uses a digest-pinned container with host networking solely to reach a newly
allocated loopback secure service; it mounts no host socket or credentials. This
method is intended for Linux Docker hosts and the hosted CI runner. Optional tool
requirements, quality policy and intentional-finding separation are documented in
[SECURITY_GATES.md](SECURITY_GATES.md).
