"""The catalog enumerates implemented modules; it does not assert test outcomes."""
import importlib
import json
from pathlib import Path
CATALOG = json.loads(Path(__file__).with_suffix(".json").read_text())

def demonstrate(name, work):
    entry = next(item for item in CATALOG if item["id"] == name)
    module = importlib.import_module("labs." + entry["module"] + ".attack")
    return module.demonstrate(work)

def adapter(name):
    def run(work):
        result = demonstrate(name, work)
        evidence = dict(result["evidence"], legitimate_operation_allowed=result["legitimate_allowed"])
        return result["vulnerable_exploited"], result["secure_blocked"] and result["legitimate_allowed"], evidence
    return run
