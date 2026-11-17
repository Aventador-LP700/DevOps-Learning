import json
from . import vulnerable, secure
from labs.support import outcome

def users():
    return {"admin": {"role": "admin"}, "alice": {"role": "user"}, "bob": {"role": "user"}}

def demonstrate(work):
    missing, audit = work / "missing.jsonl", work / "audit.jsonl"
    a, b = users(), users()
    changed = vulnerable.change_role("admin", "alice", "admin", a, missing)
    good = secure.change_role("admin", "alice", "admin", b, audit)
    denied = not secure.change_role("bob", "admin", "user", b, audit)
    events = [json.loads(line) for line in audit.read_text().splitlines()]
    return outcome(changed and not missing.exists(), denied and [event["result"] for event in events] == ["allowed", "denied"], good and b["alice"]["role"] == "admin",
                   {"vulnerable_audit_exists": missing.exists(), "secure_events": events, "scope": "Local JSONL evidence, not a deployed SIEM or tamper-resistant log store"})
