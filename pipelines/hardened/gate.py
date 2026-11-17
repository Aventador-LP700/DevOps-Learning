"""Run from repository root: python -m pipelines.hardened.gate REPORT.json"""
import argparse
from pathlib import Path
from lab.controls import load_gate
parser = argparse.ArgumentParser()
parser.add_argument("report", type=Path)
args = parser.parse_args()
try:
    decision = load_gate(args.report, Path(__file__).resolve().parents[2] / "policies/release.json")
except (ValueError, OSError, TypeError, AttributeError) as exc:
    parser.exit(2, f"Invalid scan input: {exc}\n")
print(decision)
raise SystemExit(0 if decision["allowed"] else 1)
