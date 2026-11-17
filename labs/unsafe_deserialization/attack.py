import json
import pickle
from . import vulnerable, secure
from labs.support import outcome, rejected

class LocalProof:
    def __init__(self, path):
        self.path = str(path)
    def __reduce__(self):
        return vulnerable.write_marker, (self.path,)

def demonstrate(work):
    marker = work / "pickle-proof"
    payload = pickle.dumps(LocalProof(marker))
    vulnerable.restore(payload)
    ran = marker.read_text() == "LAB_PICKLE_EXECUTED"
    marker.unlink()
    blocked = rejected(lambda: secure.restore(payload)) and not marker.exists()
    normal = secure.restore(json.dumps({"user": "alice", "theme": "dark"}).encode())
    return outcome(ran, blocked, normal["theme"] == "dark",
                   {"vulnerable_callable_executed": ran, "secure_marker_exists": marker.exists(), "secure_format": "Schema-validated JSON; no pickle execution", "payload_bytes": len(payload)})
