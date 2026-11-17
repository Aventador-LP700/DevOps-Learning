"""Container and opt-in native exercise runner and machine-readable evidence exporter."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import traceback
from .scenarios import SCENARIOS, run_scenario


def render_markdown(report):
    lines = ["# PipelineProof assessment", "", f"Generated: {report['generated_at']}", "",
             "Scope: local teaching lab; synthetic secrets and findings.",
             f"Execution mode: {report.get('execution_mode', 'container')}", "",
             "| Scenario | Vulnerable exploit observed | Hardened control blocked attack | Result |",
             "|---|---|---|---|"]
    for result in report["results"]:
        lines.append(f"| {result['id']} | {result['vulnerable_exploited']} | {result['hardened_blocked']} | {'PASS' if result['passed'] else 'FAIL'} |")
    lines += ["", "## Evidence", ""]
    for result in report["results"]:
        lines += [f"### {result['id']}", "", "```json", json.dumps(result, indent=2), "```", ""]
    lines += ["## Interpretation", "", "PASS means the expected lab exploit occurred and its hardened retest blocked it.",
              "It does not certify a production pipeline. Kubernetes RBAC and live scanner runs are separate exercises.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    run = sub.add_parser("run")
    run.add_argument("--scenario", choices=SCENARIOS)
    run.add_argument("--output", type=Path)
    run.add_argument("--native", action="store_true",
                     help="Run fixed teaching exercises on the host without container isolation")
    args = parser.parse_args()
    if args.command == "list":
        for name, (_, description, _) in SCENARIOS.items():
            print(f"{name}: {description}")
        return 0
    if args.native:
        if os.name != "posix":
            parser.error("Native exercises require Linux, macOS or WSL2")
        print("Native mode: fixed teaching payloads run as your user; no container isolation.")
    elif not Path("/lab/.pipelineproof-container").is_file():
        parser.error("Use make lab for isolation, or bash ./setup.sh for native practice")
    if args.output is None:
        args.output = Path("reports") if args.native else Path("/reports")
    results = []
    for name in ([args.scenario] if args.scenario else SCENARIOS):
        try:
            result = run_scenario(name)
        except Exception:
            result = {"id": name, "passed": False, "vulnerable_exploited": False,
                      "hardened_blocked": False, "evidence": {"error": traceback.format_exc()}}
        results.append(result)
        print(f"{'PASS' if result['passed'] else 'FAIL'} {name}")
    report = {"execution_mode": "native" if args.native else "container", "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
              "passed": all(r["passed"] for r in results), "results": results}
    args.output.mkdir(parents=True, exist_ok=True)
    # Each execution replaces previous evidence, preventing mixed/stale run results.
    (args.output / "assessment.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "assessment.md").write_text(render_markdown(report))
    print(f"Evidence written to {args.output}")
    return 0 if report["passed"] else 1

if __name__ == "__main__":
    sys.exit(main())
