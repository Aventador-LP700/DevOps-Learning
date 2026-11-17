import hashlib
import json
from . import vulnerable, secure
from labs.support import outcome, rejected

def demonstrate(work):
    script = work / "dependency_hook.py"
    script.write_text("from pathlib import Path\nPath('build-hook-marker').write_text('LAB_HOOK_EXECUTED')\n")
    marker = work / "build-hook-marker"
    code = vulnerable.build(script, work)
    ran = code == 0 and marker.read_text() == "LAB_HOOK_EXECUTED"
    marker.unlink()
    blocked = rejected(lambda: secure.build(script, "unused")) and not marker.exists()
    metadata = work / "dependency.json"
    metadata.write_text(json.dumps({"name": "demo", "version": "1.0.0", "kind": "prebuilt-metadata"}))
    expected = hashlib.sha256(metadata.read_bytes()).hexdigest()
    good = secure.build(metadata, expected)
    return outcome(ran, blocked, good["name"] == "demo",
                   {"vulnerable_hook_executed": ran, "secure_marker_exists": marker.exists(), "secure": "Source hooks rejected; trusted metadata consumed as data", "scope": "Simulation of build-hook execution, not a general Python package installer"})
